import time
from typing import Any

import requests
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
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


def _ollama_llm() -> ChatOllama:
    return ChatOllama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=0,
    )


def _is_ollama_available() -> bool:
    try:
        with requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2) as response:
            return response.status_code == 200
    except Exception:
        return False


def get_llm(prefer_quality: bool = False):
    candidates: list[Any] = []

    # Quality mode should try the GitHub model first when available.
    if prefer_quality and config.GITHUB_TOKEN:
        candidates.append(_github_quality_llm())

    # Ollama local is primary when enabled and reachable.
    if config.USE_LOCAL_LLM and _is_ollama_available():
        candidates.append(_ollama_llm())

    # GitHub quality remains a useful fallback for non-quality calls too.
    if not prefer_quality and config.GITHUB_TOKEN:
        candidates.append(_github_quality_llm())

    # Cloud providers are fallbacks.
    if config.CEREBRAS_API_KEY:
        candidates.append(_cerebras_llm())

    if config.GROQ_API_KEY:
        candidates.append(_groq_llm())

    if not candidates:
        raise ValueError(
            "No LLM providers available. Ensure local Ollama is running or configure CEREBRAS_API_KEY/GROQ_API_KEY."
        )

    primary = candidates[0]
    if len(candidates) == 1:
        return primary

    return primary.with_fallbacks(candidates[1:])


def get_llm_with_retry(prefer_quality: bool = False, max_retries: int = 3) -> Any:
    delays = [5, 15, 30]
    last_error = None
    for attempt, delay in enumerate(delays[:max_retries]):
        try:
            return get_llm(prefer_quality=prefer_quality)
        except Exception as exc:
            if "429" in str(exc) or "rate" in str(exc).lower():
                print(f"[LLM] Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}")
                time.sleep(delay)
                last_error = exc
            else:
                raise
    raise last_error
