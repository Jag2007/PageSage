"""Embedding model loader for PageSage."""

import logging
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return the HuggingFace embedding model, fully local after first download."""
    logger.info("Loading local embedding model: %s", EMBEDDING_MODEL)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    logger.info("Embedding model loaded locally.")
    return embeddings
