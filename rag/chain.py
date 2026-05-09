import logging

from config import OLLAMA_BASE_URL, CHAT_MODEL, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_DEFAULT_MODEL, OPENROUTER_REASONING_MODEL
from rag.vectorstore import query_similar

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert analyst specializing in Unidentified Anomalous Phenomena (UAP) and Unidentified Flying Objects (UFOs). You have access to declassified government documents, military reports, FBI case files, NASA records, and other official sources.

Your role is to:
- Analyze the provided documents objectively and scientifically
- Draw connections between different reports and sightings
- Identify patterns in dates, locations, descriptions, and phenomena
- Provide factual, evidence-based answers
- Acknowledge when data is insufficient for conclusions
- Note any interesting correlations or anomalies in the data

Always cite the specific documents or sources you reference in your answer.
If the provided context doesn't contain enough information, say so clearly."""

RAG_PROMPT = """Based on the following declassified government documents and records, answer the question. Use only information from the provided context. If the context is insufficient, say so.

CONTEXT DOCUMENTS:
{context}

QUESTION: {question}

Provide a thorough, evidence-based answer citing specific documents where possible:"""


def build_context(query_results: dict) -> str:
    docs = query_results.get("documents", [[]])[0]
    metas = query_results.get("metadatas", [[]])[0]
    dists = query_results.get("distances", [[]])[0]

    parts = []
    for doc, meta, dist in zip(docs, metas, dists):
        source = meta.get("source_file", "Unknown")
        agency = meta.get("agency", "")
        location = meta.get("incident_location", "")
        date = meta.get("incident_date", "")
        relevance = f"{(1 - dist) * 100:.1f}%"

        header = f"[{source}"
        if agency:
            header += f" | {agency}"
        if location:
            header += f" | {location}"
        if date:
            header += f" | {date}"
        header += f" | Relevance: {relevance}]"

        parts.append(f"{header}\n{doc}")

    return "\n\n---\n\n".join(parts)


def ask_ollama(prompt: str, model: str | None = None) -> str:
    import ollama

    client = ollama.Client(host=OLLAMA_BASE_URL)
    resp = client.chat(
        model=model or CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resp["message"]["content"].strip()


def ask_openrouter(prompt: str, model: str | None = None) -> str:
    from openai import OpenAI

    if not OPENROUTER_API_KEY:
        return "OpenRouter API key not configured."

    model = model or OPENROUTER_DEFAULT_MODEL
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        max_retries=4,
        timeout=120,
    )

    fallback_order = [
        model,
        "nvidia/nemotron-3-super-120b-a12b:free",
        "google/gemma-4-31b-it:free",
        "z-ai/glm-4.5-air:free",
        "openai/gpt-oss-120b:free",
    ]
    seen = set()
    for try_model in fallback_order:
        if try_model in seen:
            continue
        seen.add(try_model)
        try:
            resp = client.chat.completions.create(
                model=try_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            logger.info(f"OpenRouter responded with model: {try_model}")
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Model {try_model} failed: {e}")
            continue

    return ask_ollama(prompt)


def ask(question: str, n_results: int = 10, use_openrouter: bool = False, model: str | None = None, filter_metadata: dict | None = None) -> dict:
    logger.info(f"Querying: {question}")

    results = query_similar(question, n_results=n_results, filter_metadata=filter_metadata)
    context = build_context(results)

    prompt = RAG_PROMPT.format(context=context, question=question)

    if use_openrouter and OPENROUTER_API_KEY:
        answer = ask_openrouter(prompt, model=model)
    else:
        answer = ask_ollama(prompt)

    sources = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        sources.append(
            {
                "source_file": meta.get("source_file", ""),
                "agency": meta.get("agency", ""),
                "location": meta.get("incident_location", ""),
                "date": meta.get("incident_date", ""),
                "excerpt": doc[:200],
            }
        )

    return {"question": question, "answer": answer, "sources": sources, "context": context}
