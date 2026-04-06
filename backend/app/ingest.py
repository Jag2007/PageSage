"""PDF ingestion and ChromaDB persistence for PageSage."""

import logging
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR, CHUNK_OVERLAP, CHUNK_SIZE
from app.embeddings import get_embeddings
from app.pdf_utils import extract_text_from_pdf, get_page_number_from_marker

logger = logging.getLogger(__name__)


def _file_name_and_bytes(uploaded_file: Any) -> tuple[str, bytes]:
    """Return a filename and bytes from a normalized upload object."""
    if isinstance(uploaded_file, dict):
        return uploaded_file["filename"], uploaded_file["content"]
    return uploaded_file.name, uploaded_file.read()


def ingest_documents(uploaded_files: list[Any]) -> dict[str, int]:
    """Extract PDFs, chunk text, persist chunks in ChromaDB, and return ingestion counts."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    texts: list[str] = []
    metadatas: list[dict[str, str | int]] = []
    files_processed = 0

    for uploaded_file in uploaded_files:
        filename, content = _file_name_and_bytes(uploaded_file)
        text = extract_text_from_pdf(content)
        if text.startswith("Error:"):
            logger.warning("Skipping %s due to extraction error.", filename)
            continue

        chunks = splitter.split_text(text)
        texts.extend(chunks)
        metadatas.extend(
            {
                "source": filename,
                "page": get_page_number_from_marker(chunk) or "—",
            }
            for chunk in chunks
        )
        files_processed += 1

    if not texts:
        raise ValueError("No extractable text found.")

    Chroma.from_texts(
        texts=texts,
        embedding=get_embeddings(),
        metadatas=metadatas,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    logger.info("Indexed %s chunks from %s files.", len(texts), files_processed)
    return {"chunks": len(texts), "files": files_processed}


def load_existing_db() -> Chroma | None:
    """Load an existing ChromaDB collection from disk, returning None if unavailable."""
    if not Path(CHROMA_PERSIST_DIR).exists():
        logger.info("No existing ChromaDB directory found.")
        return None
    try:
        return Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=get_embeddings(),
        )
    except Exception as exc:
        logger.warning("Failed to load ChromaDB: %s", exc)
        return None
