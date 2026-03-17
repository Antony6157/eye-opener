# Phase 1 — Project scaffold agent

## When to use this prompt
Use this at the very start of the project to generate boilerplate files. Reference it by typing `#phase1-scaffold` in Copilot Chat.

---

## Your task
Generate the Phase 1 scaffold for The Eye Opener project. Produce each file completely, ready to use with no placeholders.

### Files to generate

**`.gitignore`**
Cover Python (venv, __pycache__, *.pyc, .pytest_cache), Flask (instance/), env files (.env), ChromaDB data (chroma_db/), and OS files (.DS_Store, Thumbs.db).

**`.env.example`**
```
CEREBRAS_API_KEY=
GROQ_API_KEY=
FLASK_ENV=development
FLASK_PORT=5000
CHROMA_DB_PATH=./chroma_db
GITHUB_TOKEN=
```

**`requirements.txt`**
Pin these exact packages:
flask, flask-cors, langchain, langgraph, langchain-openai, langchain-groq, chromadb, langchain-community, youtube-transcript-api, beautifulsoup4, ddgs, requests, python-dotenv

**`config.py`**
Load .env with python-dotenv. Expose: CEREBRAS_API_KEY, GROQ_API_KEY, GITHUB_TOKEN, FLASK_ENV, FLASK_PORT (int, default 5000), CHROMA_DB_PATH. Do not crash when keys are missing; instead expose a warning when all three LLM keys are absent.

**`app.py`**
Minimal Flask app with:
- CORS enabled via flask-cors
- GET `/` serving static/index.html
- GET `/api/health` returning `{"status": "ok"}`
- POST `/api/verify` stub that returns `{"message": "pipeline not yet implemented"}`
- GET `/api/stream` stub SSE route that yields one test event then closes
- `if __name__ == "__main__"` block reading port from config

**`services/__init__.py`**, **`static/js/.gitkeep`**, **`static/css/.gitkeep`**
Empty init files to make packages importable.

---

## Output format
Print each file as a clearly labelled code block. After all files, print the exact terminal commands to:
1. Create and activate a virtual environment
2. Install requirements
3. Run the Flask app
