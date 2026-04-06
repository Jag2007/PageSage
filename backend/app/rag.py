"""Chroma retrieval and Groq answer generation for PageSage."""

import logging
import os

from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from app.config import LLM_MODEL, LLM_PROVIDER, TOP_K

logger = logging.getLogger(__name__)
BLOCKED_TERMS = ["password", "secret key", "api key", "private key"]


def get_llm() -> ChatGroq:
    """Load the configured LLM provider."""
    logger.info("Loading LLM provider: %s", LLM_PROVIDER)
    if LLM_PROVIDER == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY is missing or still set to the placeholder value.")
        return ChatGroq(model=LLM_MODEL, api_key=api_key)
    # elif LLM_PROVIDER == "ollama":
    #     from langchain_community.llms import Ollama
    #     return Ollama(model=LLM_MODEL)
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def _format_sources(docs: list) -> list[dict[str, str | int | None]]:
    """Convert LangChain documents into API-safe source dictionaries."""
    return [
        {
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page"),
            "content": doc.page_content,
        }
        for doc in docs
    ]


def query_rag(question: str, db: Chroma) -> dict[str, object]:
    """Retrieve relevant chunks from ChromaDB and answer the question using Groq."""
    if any(term in question.lower() for term in BLOCKED_TERMS):
        return {
            "answer": "I can't help retrieve or expose secrets from documents.",
            "sources": [],
            "confidence": "LOW",
        }

    docs = db.similarity_search(question, k=TOP_K)
    context = "\n\n".join(doc.page_content for doc in docs)[:1800]
    sources = _format_sources(docs)
    if not context.strip():
        return {
            "answer": "The pages don't speak to this — please upload a relevant document.",
            "sources": [],
            "confidence": "LOW",
        }

    prompt = (
        "You are PageSage, an elegant and precise document intelligence assistant. "
        "Your tagline is 'Wisdom from every page.' Answer ONLY from the context below. "
        "If the answer is not present, say: 'The pages don't speak to this — please upload "
        "a relevant document.' Always mention the file name and page number your answer "
        f"comes from. Be concise, clear, and wise. Context: {context} "
        f"Question: {question} Answer:"
    )
    answer = get_llm().invoke(prompt).content
    logger.info("Answered RAG query with %s sources.", len(sources))
    return {"answer": answer, "sources": sources, "confidence": "MEDIUM" if sources else "LOW"}
