"""PDF text extraction utilities for PageSage."""

import logging
import re
from typing import Optional

import fitz

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract page-tagged text from PDF bytes and return an error string on failure."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except (fitz.FileDataError, ValueError, TypeError) as exc:
        msg = "Error: The uploaded PDF appears to be corrupted or unreadable."
        logger.warning("Corrupted PDF upload rejected: %s", exc)
        return msg

    try:
        if doc.needs_pass:
            msg = "Error: The uploaded PDF is password-protected and cannot be processed."
            logger.warning("Password-protected PDF upload rejected.")
            return msg

        pages = []
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            pages.append(f"[Page {index}]\n{text}")

        combined_text = "\n\n".join(pages).strip()
        if not doc.page_count or not re.sub(r"\[Page \d+\]\s*", "", combined_text).strip():
            msg = "Error: The uploaded PDF contains no extractable text."
            logger.warning("Empty PDF upload rejected: no extractable text found.")
            return msg

        logger.info("Extracted text from PDF successfully: %s pages processed.", doc.page_count)
        return combined_text
    except Exception as exc:
        msg = "Error: The uploaded PDF appears to be corrupted or unreadable."
        logger.warning("PDF extraction failed due to unreadable content: %s", exc)
        return msg
    finally:
        doc.close()


def get_page_number_from_marker(text_chunk: str) -> Optional[int]:
    """Return the first page number marker found in a text chunk, if present."""
    match = re.search(r"\[Page (\d+)\]", text_chunk)
    return int(match.group(1)) if match else None
