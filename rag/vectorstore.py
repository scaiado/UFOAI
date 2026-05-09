import json
import logging
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from config import EMBEDDINGS_DIR, OLLAMA_BASE_URL, EMBED_MODEL

logger = logging.getLogger(__name__)


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(EMBEDDINGS_DIR))


def get_or_create_collection(client: chromadb.PersistentClient, name: str = "uap_documents"):
    ef = embedding_functions.OllamaEmbeddingFunction(
        url=OLLAMA_BASE_URL,
        model_name=EMBED_MODEL,
    )
    return client.get_or_create_collection(
        name=name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def embed_chunks(chunks_file: str | Path | None = None):
    from config import PROCESSED_DIR

    if chunks_file is None:
        chunks_file = PROCESSED_DIR / "all_chunks.json"

    path = Path(chunks_file)
    if not path.exists():
        logger.error(f"Chunks file not found: {path}")
        return 0

    data = json.loads(path.read_text())
    if not data:
        logger.warning("No chunks to embed")
        return 0

    client = get_chroma_client()
    collection = get_or_create_collection(client)

    existing_ids = set(collection.get(include=[])["ids"])
    logger.info(f"Existing embeddings: {len(existing_ids)}")

    batch_size = 100
    added = 0

    for i in range(0, len(data), batch_size):
        batch = data[i : i + batch_size]
        ids = []
        documents = []
        metadatas = []

        for j, chunk in enumerate(batch):
            global_idx = i + j
            chunk_id = f"chunk_{global_idx:04d}_{chunk.get('source_file', 'unknown')[:50]}"
            if chunk_id in existing_ids:
                continue

            text = chunk.get("text", "").strip()
            if not text:
                continue

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(
                {
                    "source_file": chunk.get("source_file", ""),
                    "chunk_type": chunk.get("chunk_type", ""),
                    "agency": chunk.get("agency", ""),
                    "incident_date": chunk.get("incident_date", ""),
                    "incident_location": chunk.get("incident_location", ""),
                    "title": chunk.get("title", ""),
                }
            )

        if ids:
            try:
                collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
                added += len(ids)
                logger.info(f"Embedded batch {i // batch_size + 1}: {len(ids)} chunks")
            except Exception as e:
                logger.error(f"Embedding batch error: {e}")

    logger.info(f"Embedding complete. {added} new chunks added. Total: {collection.count()}")
    return added


def query_similar(query_text: str, n_results: int = 10, filter_metadata: dict | None = None) -> dict:
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    kwargs = {"query_texts": [query_text], "n_results": n_results}
    if filter_metadata:
        kwargs["where"] = filter_metadata

    return collection.query(**kwargs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    embed_chunks()
