from __future__ import annotations

import time
from datetime import datetime, timezone
from hashlib import sha1
from typing import Iterable

import chromadb
import requests
from bs4 import BeautifulSoup
from langchain_community.embeddings import HuggingFaceEmbeddings

import config


SOURCES = [
    {"name": "PIB", "url": "https://pib.gov.in/allRel.aspx", "selector": "div.content-area"},
    {"name": "AltNews", "url": "https://www.altnews.in/", "selector": "article"},
    {"name": "Factly", "url": "https://factly.in/category/fact-check/", "selector": "article"},
    {"name": "BoomLive", "url": "https://www.boomlive.in/fact-check", "selector": "article"},
    {"name": "VishvasNews", "url": "https://www.vishvasnews.com/", "selector": "article"},
]

COLLECTION_NAME = "indian_political_facts"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
USER_AGENT = "EyeOpenerIndexer/1.0 (+https://localhost)"


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []

    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(clean):
            break
        start += step
    return chunks


def _extract_source_text(html: str, selector: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    nodes = soup.select(selector)
    if not nodes:
        return ""
    return "\n".join(node.get_text(" ", strip=True) for node in nodes)


def _fetch_source(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


def _build_ids(source_name: str, source_url: str, chunks: Iterable[str]) -> list[str]:
    ids: list[str] = []
    for index, chunk in enumerate(chunks):
        digest = sha1(f"{source_name}|{source_url}|{index}|{chunk}".encode("utf-8")).hexdigest()[:16]
        ids.append(f"{source_name.lower()}-{index}-{digest}")
    return ids


def _get_embedder() -> HuggingFaceEmbeddings:
    # Local sentence-transformer embeddings (no Google embedding dependency).
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_all_sources() -> None:
    print("Starting index build...")
    collection = _get_collection()
    embedder = _get_embedder()

    scraped_at = datetime.now(timezone.utc).isoformat()

    for source in SOURCES:
        name = source["name"]
        url = source["url"]
        selector = source["selector"]

        print(f"[INDEX] Fetching {name}: {url}")
        try:
            html = _fetch_source(url)
            extracted = _extract_source_text(html, selector)
            chunks = _chunk_text(extracted)

            if not chunks:
                print(f"[SKIP] {name}: no extractable content for selector '{selector}'")
            else:
                embeddings = embedder.embed_documents(chunks)
                ids = _build_ids(name, url, chunks)
                metadatas = [
                    {
                        "source_name": name,
                        "url": url,
                        "scraped_at": scraped_at,
                        "chunk_index": i,
                    }
                    for i, _ in enumerate(chunks)
                ]

                collection.upsert(
                    ids=ids,
                    documents=chunks,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )

                print(f"[DONE] {name}: indexed {len(chunks)} chunks")
        except Exception as exc:
            print(f"[ERROR] {name}: {exc}")

        time.sleep(2)

    print("Index build complete.")


if __name__ == "__main__":
    index_all_sources()
