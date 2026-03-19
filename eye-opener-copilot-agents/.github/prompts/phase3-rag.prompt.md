# Phase 3 — RAG + retrieval layer agent

## When to use this prompt
Use when building the ChromaDB indexer and upgrading the Deep Diver to hybrid retrieval. Reference with `#phase3-rag` in Copilot Chat.

---

## Context
The Deep Diver uses hybrid retrieval. Phase 3 queries a local ChromaDB vector store first. If the top result confidence is below a threshold, it falls back to live DuckDuckGo search. The `retrieval_method` field in `AgentState` records which path was used.

---

## File: services/indexer.py
Build a standalone script that scrapes trusted Indian sources and indexes them into ChromaDB.

**Setup**
- Use `chromadb.PersistentClient` with path from `config.CHROMA_DB_PATH`
- Create or get collection named `"indian_political_facts"`
- Use `langchain_ollama.OllamaEmbeddings` with model `"nomic-embed-text"` for embeddings

**Sources to scrape** (scrape each with BeautifulSoup + requests):
```python
SOURCES = [
    {"name": "AltNews", "url": "https://www.altnews.in/", "selector": "article", "category": "fact_check"},
    {"name": "Factly", "url": "https://factly.in/category/fact-check/", "selector": "article", "category": "fact_check"},
    {"name": "BoomLive", "url": "https://www.boomlive.in/fact-check", "selector": "a[href*='/fact-check/']", "category": "fact_check"},
    {"name": "VishvasNews", "url": "https://www.vishvasnews.com/", "selector": "a[href*='vishvasnews.com']", "category": "fact_check"},
    {"name": "IndianKanoon", "url": "https://indiankanoon.org/search/?formInput=constitution+india&pagenum=1", "selector": "a[href*='/doc/']", "category": "legal"},
]
```

**Indexing logic**
- For each source: fetch page, parse with BeautifulSoup, extract text from selector
- Chunk text into 500-character overlapping chunks (100 char overlap)
- Generate embeddings via `OllamaEmbeddings`
- Upsert into ChromaDB with metadata including `source_name`, `url`, `scraped_at`, `chunk_index`, and `category`
- Print progress for each source

**Entry point**
`if __name__ == "__main__": index_all_sources()`

---

## File: services/retriever.py
Encapsulate all retrieval logic here so `agents.py` stays clean.

**Function: `rag_search(query: str, n_results: int = 5) -> tuple[list[dict], float]`**
- Connect to ChromaDB at `config.CHROMA_DB_PATH`
- Query the `"indian_political_facts"` collection with the query string
- Return: list of result dicts `{text, source, url, distance}` and the top result's confidence score (1 - distance, normalised to 0-1)

**Function: `live_search(query: str, sources: list[str]) -> list[dict]`**
- Use `ddgs.DDGS().text()` with site-restricted query strings
- Format: `f"{query} site:{source}"` for each source in the list
- Deduplicate results by URL
- Return: list of dicts `{title, body, text, url, source}`

**Function: `hybrid_search(query: str) -> tuple[list[dict], str]`**
- Call `rag_search(query)` first
- If top confidence >= 0.75: return results, `"rag"`
- Else: call `live_search(query, sources=TRUSTED_SOURCES)`, merge with RAG results, return merged, `"hybrid"` (or `"live_search"` if RAG returned nothing)

**TRUSTED_SOURCES constant**
```python
TRUSTED_SOURCES = ["pib.gov.in", "altnews.in", "factly.in", "boomlive.in", "vishvasnews.com", "indiankanoon.org"]
```

---

## Update: services/agents.py — diver function
Replace the existing diver implementation with the hybrid retrieval version:
- Import `hybrid_search` from `services/retriever`
- For each claim in `state["claims"]`: call `hybrid_search(claim)`
- Accumulate results into `state["research_logs"]`
- Set `state["retrieval_method"]` based on what `hybrid_search` returns
- If any search raises an exception, log it but do not set `state["error"]` unless the claim cannot be processed at all

---

## Testing checklist for this phase
After completing this phase, verify:
1. Run `python -m services.indexer` — should complete without errors and create or update the chroma_db folder
2. Open a Python shell, import `rag_search`, query a known political topic — should return results
3. Run the full pipeline with a real political claim — check `retrieval_method` in the SSE output
4. Disconnect from the internet, run again — pipeline should fall back to RAG only when the local index has coverage
