import logging
import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi

from services.state import AgentState


LOGGER = logging.getLogger(__name__)


YOUTUBE_WATCH_RE = re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]{6,})", re.IGNORECASE)
YOUTU_BE_RE = re.compile(r"(?:https?://)?(?:www\.)?youtu\.be/([\w-]{6,})", re.IGNORECASE)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_video_id(url: str) -> str:
    watch_match = YOUTUBE_WATCH_RE.search(url)
    if watch_match:
        return watch_match.group(1)

    short_match = YOUTU_BE_RE.search(url)
    if short_match:
        return short_match.group(1)

    parsed = urlparse(url)
    if parsed.netloc.lower().replace("www.", "") in {"youtube.com", "m.youtube.com"} and parsed.path == "/watch":
        return parse_qs(parsed.query).get("v", [""])[0]

    return ""


def _is_youtube_url(value: str) -> bool:
    return bool(YOUTUBE_WATCH_RE.search(value) or YOUTU_BE_RE.search(value))


def _fetch_transcript(video_id: str) -> str:
    ytt = YouTubeTranscriptApi()
    transcript = ytt.fetch(video_id)
    cleaned_text = " ".join([t.text for t in transcript])
    return _normalize_text(cleaned_text)


def preprocess(state: AgentState) -> AgentState:
    state["active_agent"] = "preprocessor"
    raw_input = state["raw_input"].strip()
    LOGGER.info("Preprocessor started")

    if not raw_input:
        state["error"] = "Input is required. Provide plain text or a YouTube URL."
        LOGGER.error(state["error"])
        return state

    if _is_youtube_url(raw_input):
        LOGGER.info("Detected YouTube input")
        video_id = _extract_video_id(raw_input)
        if not video_id:
            state["error"] = "Invalid YouTube URL. Could not parse a video id."
            LOGGER.error(state["error"])
            return state

        try:
            cleaned_text = _fetch_transcript(video_id)
            LOGGER.info("Transcript fetched successfully")
        except Exception as exc:
            state["error"] = f"Failed to fetch YouTube transcript: {exc}"
            LOGGER.exception("Transcript fetch failed")
            return state
    else:
        LOGGER.info("Detected plain-text input")
        cleaned_text = _normalize_text(raw_input)

    if not cleaned_text:
        state["error"] = "Input preprocessing produced empty text."
        LOGGER.error(state["error"])
        return state

    state["cleaned_text"] = cleaned_text
    state["error"] = None
    LOGGER.info("Preprocessor completed")
    return state