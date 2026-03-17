import logging
import re
import time

from services.llm import get_llm
from services.retriever import hybrid_search
from services.state import AgentState


LOGGER = logging.getLogger(__name__)


WORD_TO_NUM = {
    "zero": 0,
    "ten": 10,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
    "one hundred": 100,
}


def _with_cooldown(state: AgentState) -> AgentState:
    time.sleep(2)
    return state


def _extract_numbered_lines(text: str) -> list[str]:
    claims: list[str] = []
    for line in text.splitlines():
        cleaned = line.strip()
        cleaned = re.sub(r"^\d+[.)]\s*", "", cleaned)
        if cleaned:
            claims.append(cleaned)
    return claims


def _safe_model_text(response: object) -> str:
    content = getattr(response, "content", "")
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if isinstance(text, str):
                parts.append(text)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts).strip()
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def surgeon(state: AgentState) -> AgentState:
    if state["error"]:
        return _with_cooldown(state)

    state["active_agent"] = "surgeon"
    text = state["cleaned_text"].strip()
    if not text:
        state["error"] = "No cleaned_text available for claim extraction."
        return _with_cooldown(state)

    try:
        llm = get_llm()
        prompt = (
            "Extract all specific, verifiable factual claims from the text below. "
            "Return only a numbered list, one claim per line.\n\n"
            f"Text:\n{text}"
        )
        response = llm.invoke(prompt)
        claims = _extract_numbered_lines(_safe_model_text(response))
    except Exception as exc:
        state["error"] = f"Surgeon failed: {exc}"
        return _with_cooldown(state)

    if not claims:
        state["error"] = "Surgeon could not extract any verifiable claims."
        return _with_cooldown(state)

    state["claims"] = claims
    return _with_cooldown(state)


def diver(state: AgentState) -> AgentState:
    if state["error"]:
        return _with_cooldown(state)

    state["active_agent"] = "diver"
    claims = state["claims"]
    if not claims:
        state["error"] = "No claims available for diver."
        return _with_cooldown(state)

    logs: list[dict] = []
    methods: set[str] = set()
    for claim in claims:
        try:
            results, method = hybrid_search(claim)
            methods.add(method)
            logs.append(
                {
                    "claim": claim,
                    "sources": results,
                    "evidence": [r["text"] for r in results],
                }
            )
        except Exception as exc:
            LOGGER.exception("Diver hybrid_search failed for claim '%s': %s", claim, exc)

    state["research_logs"] = logs
    if len(methods) > 1:
        state["retrieval_method"] = "hybrid"
    elif len(methods) == 1:
        state["retrieval_method"] = next(iter(methods))
    return _with_cooldown(state)


def skeptic(state: AgentState) -> AgentState:
    if state["error"]:
        return _with_cooldown(state)

    state["active_agent"] = "skeptic"
    if not state["research_logs"]:
        state["error"] = "No research_logs available for skeptic."
        return _with_cooldown(state)

    try:
        llm = get_llm()
        prompt = (
            "Given these claims and research logs, act as a devil's advocate. "
            "Identify missing context, potential misquotations, selective framing, or unsupported assertions. "
            "Return concise bullet points, one per line.\n\n"
            f"Claims: {state['claims']}\n"
            f"Research logs: {state['research_logs']}"
        )
        response = llm.invoke(prompt)
        critique_text = _safe_model_text(response)
        critiques = [line.strip("- \t") for line in critique_text.splitlines() if line.strip()]
    except Exception as exc:
        state["error"] = f"Skeptic failed: {exc}"
        return _with_cooldown(state)

    state["critiques"] = critiques
    return _with_cooldown(state)


def scorer(state: AgentState) -> AgentState:
    if state["error"]:
        return _with_cooldown(state)

    state["active_agent"] = "scorer"
    if not state["claims"]:
        state["error"] = "No claims available for scoring."
        return _with_cooldown(state)

    try:
        llm = get_llm(prefer_quality=True)
    except Exception as exc:
        state["error"] = f"Scorer failed to initialize quality LLM: {exc}"
        return _with_cooldown(state)

    verdicts: list[dict] = []
    scores: list[int] = []

    for claim in state["claims"]:
        evidence_for_claim = [item for item in state["research_logs"] if item.get("claim") == claim]
        prompt = (
            "You are a fact-checking scorer. For the claim below, return exactly four lines in this format:\n"
            "Always use digits (0-100), never write numbers as words. Score must be an integer.\n"
            "verdict: True|False|Misleading|Unverifiable\n"
            "confidence: 0-100\n"
            "reasoning: short explanation\n"
            "score: 0-100\n\n"
            f"Claim: {claim}\n"
            f"Evidence: {evidence_for_claim}\n"
            f"Critiques: {state['critiques']}"
        )

        try:
            response = llm.invoke(prompt)
            text = _safe_model_text(response)
            LOGGER.info("Scorer raw response for claim '%s': %s", claim, text)
        except Exception as exc:
            state["error"] = f"Scorer failed for claim '{claim}': {exc}"
            return _with_cooldown(state)

        verdict = "Unverifiable"
        confidence = 50
        reasoning = "Model response could not be parsed reliably."
        score = 50

        for line in text.splitlines():
            stripped = line.strip()
            lowered = stripped.lower()
            try:
                if lowered.startswith("verdict:"):
                    verdict = stripped.split(":", 1)[1].strip() or verdict
                elif lowered.startswith("confidence:"):
                    raw_value = stripped.split(":", 1)[1]
                    value = re.sub(r"[^0-9]", "", raw_value)
                    if not value:
                        raise ValueError(f"No numeric confidence value found in '{raw_value.strip()}'")
                    confidence = int(value)
                elif lowered.startswith("reasoning:"):
                    reasoning = stripped.split(":", 1)[1].strip() or reasoning
                elif lowered.startswith("score:"):
                    raw_value = stripped.split(":", 1)[1]
                    raw_lower = raw_value.strip().lower()
                    if raw_lower in WORD_TO_NUM:
                        value = str(WORD_TO_NUM[raw_lower])
                    else:
                        value = re.sub(r"[^0-9]", "", raw_value)
                    if not value:
                        raise ValueError(f"No numeric score value found in '{raw_value.strip()}'")
                    score = int(value)
            except Exception as exc:
                LOGGER.exception(
                    "Scorer parsing failed for claim '%s' on line '%s' with error: %s",
                    claim,
                    stripped,
                    exc,
                )

        confidence = max(0, min(100, confidence))
        score = max(0, min(100, score))
        scores.append(score)
        verdicts.append(
            {
                "claim": claim,
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": reasoning,
            }
        )

    state["verdicts"] = verdicts
    state["truth_score"] = int(sum(scores) / len(scores)) if scores else 0
    return _with_cooldown(state)