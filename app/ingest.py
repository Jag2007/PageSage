"""Document ingestion and FAISS persistence utilities for PageSage."""

import logging
import os
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, FAISS_INDEX_PATH
from app.embeddings import get_embeddings
from app.pdf_utils import extract_text_from_pdf, get_page_number_from_marker

logger = logging.getLogger(__name__)


def ingest_documents(uploaded_files: list, workspace: str = "default_workspace") -> FAISS:
    """Extract, chunk, embed, and persist uploaded PDFs into a workspace-scoped FAISS index."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    texts, metadatas, processed_files = [], [], 0
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        text = extract_text_from_pdf(uploaded_file.read())
        if text.startswith("Error:"):
            logger.warning("Skipping file %s due to extraction error.", filename)
            continue
        chunks = splitter.split_text(text)
        texts.extend(chunks)
        metadatas.extend(
            {"source": filename, "page": get_page_number_from_marker(chunk)}
            for chunk in chunks
        )
        processed_files += 1

    if not texts:
        raise ValueError("No extractable text chunks were produced from the uploaded PDFs.")

    vectorstore = FAISS.from_texts(texts, get_embeddings(), metadatas=metadatas)
    index_path = Path(FAISS_INDEX_PATH).parent / workspace
    index_path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(os.fspath(index_path))
    logger.info("Indexed %s chunks across %s files.", len(texts), processed_files)
    return vectorstore


def load_existing_index(workspace: str = "default_workspace") -> FAISS | None:
    """Load an existing workspace FAISS index from disk, returning None when unavailable."""
    index_path = Path(FAISS_INDEX_PATH).parent / workspace
    if not index_path.exists():
        logger.info("No existing FAISS index found for workspace: %s", workspace)
        return None
    try:
        return FAISS.load_local(
            os.fspath(index_path),
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    except Exception as exc:
        logger.warning("Failed to load FAISS index for workspace %s: %s", workspace, exc)
        return None
