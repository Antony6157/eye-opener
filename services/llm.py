from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

import config


def _cerebras_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=config.CEREBRAS_MODEL,
        api_key=config.CEREBRAS_API_KEY,
        base_url="https://api.cerebras.ai/v1",
        temperature=0,
    )


def _groq_llm() -> ChatGroq:
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=0,
    )


def _github_quality_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=config.GITHUB_QUALITY_MODEL,
        api_key=config.GITHUB_TOKEN,
        base_url="https://models.inference.ai.azure.com",
        temperature=0,
    )


def get_llm(prefer_quality: bool = False):
    candidates = []

    if prefer_quality and config.GITHUB_TOKEN:
        candidates.append(_github_quality_llm())

    if config.GROQ_API_KEY:
        candidates.append(_groq_llm())

    if config.CEREBRAS_API_KEY:
        candidates.append(_cerebras_llm())

    if not candidates:
        raise ValueError(
            "No LLM credentials configured. Set CEREBRAS_API_KEY or GROQ_API_KEY, "
            "or set GITHUB_TOKEN when prefer_quality=True."
        )

    primary = candidates[0]
    if len(candidates) == 1:
        return primary

    return primary.with_fallbacks(candidates[1:])
