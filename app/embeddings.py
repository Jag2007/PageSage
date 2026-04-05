"""Embedding loader utilities for PageSage."""

import logging

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embeddings() -> HuggingFaceEmbeddings:
    """Load the local embedding model, which runs fully offline after its first download."""
    logger.info("Loading local embedding model: %s", EMBEDDING_MODEL)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    logger.info(
        "Embedding model loaded locally — no internet required for embeddings."
    )
    return embeddings
