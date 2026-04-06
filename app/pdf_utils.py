"""PDF text extraction utilities for PageSage."""

import logging
import os
import re
from pathlib import Path
from typing import Optional

import fitz

logger = logging.getLogger(__name__)


def _get_tessdata_path() -> str | None:
    """Return a known tessdata directory for PyMuPDF OCR, if one exists."""
    candidates = [
        os.getenv("TESSDATA_PREFIX"),
        "/opt/homebrew/share/tessdata",
        "/usr/local/share/tessdata",
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
    ]
    for candidate in candidates:
        if candidate and (Path(candidate) / "eng.traineddata").exists():
            return candidate
    return None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract page-tagged text from PDF bytes, using OCR fallback for image-only pages."""
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
        ocr_failures = 0
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if not text:
                try:
                    textpage = page.get_textpage_ocr(
                        language="eng",
                        dpi=150,
                        full=True,
                        tessdata=_get_tessdata_path(),
                    )
                    text = page.get_text("text", textpage=textpage).strip()
                except Exception as exc:
                    ocr_failures += 1
                    logger.warning("OCR fallback failed on page %s: %s", index, exc)
            pages.append(f"[Page {index}]\n{text}")

        combined_text = "\n\n".join(pages).strip()
        if not doc.page_count or not re.sub(r"\[Page \d+\]\s*", "", combined_text).strip():
            msg = (
                "Error: The uploaded PDF contains no extractable text. "
                "If it is scanned or image-only, OCR support may be unavailable."
            )
            logger.warning(
                "Empty PDF upload rejected: no extractable text found; OCR failures=%s.",
                ocr_failures,
            )
            return msg

        logger.info(
            "Extracted text from PDF successfully: %s pages processed, %s OCR failures.",
            doc.page_count,
            ocr_failures,
        )
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
