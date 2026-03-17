import os
from dotenv import load_dotenv


load_dotenv()


CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

CEREBRAS_MODEL = "llama3.3-70b"
GROQ_MODEL = "llama-3.3-70b-versatile"
GITHUB_QUALITY_MODEL = "gpt-4.1-mini"

FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")


def get_config_warnings() -> list[str]:
    warnings: list[str] = []
    if not (CEREBRAS_API_KEY or GROQ_API_KEY or GITHUB_TOKEN):
        warnings.append(
            "No LLM credentials configured. Set at least one of CEREBRAS_API_KEY, GROQ_API_KEY, or GITHUB_TOKEN."
        )
    return warnings


CONFIG_WARNINGS = get_config_warnings()
CONFIG_ERRORS: list[str] = []
