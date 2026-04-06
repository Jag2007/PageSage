"""PDF extraction helpers for PageSage."""

import logging
import os
import re
from pathlib import Path

import fitz

logger = logging.getLogger(__name__)
MAX_OCR_PAGES = 20


def _get_tessdata_path() -> str | None:
    """Return a known tessdata directory for PyMuPDF OCR, if available."""
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
        logger.warning("Corrupted PDF rejected: %s", exc)
        return "Error: The uploaded PDF appears to be corrupted or unreadable."

    try:
        if doc.needs_pass:
            logger.warning("Password-protected PDF rejected.")
            return "Error: The uploaded PDF is password-protected and cannot be processed."

        page_texts: list[tuple[int, str]] = []
        blank_page_numbers: list[int] = []
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            page_texts.append((index, text))
            if not text:
                blank_page_numbers.append(index)

        has_selectable_text = any(text for _, text in page_texts)
        if has_selectable_text:
            pages = [f"[Page {index}]\n{text}" for index, text in page_texts]
            combined_text = "\n\n".join(pages).strip()
            logger.info(
                "Extracted %s PDF pages; skipped OCR for %s blank/image-only pages.",
                doc.page_count,
                len(blank_page_numbers),
            )
            return combined_text

        pages: list[str] = []
        ocr_failures = 0
        for index, page in enumerate(doc, start=1):
            text = ""
            if index <= MAX_OCR_PAGES:
                try:
                    textpage = page.get_textpage_ocr(
                        language="eng", dpi=150, full=True, tessdata=_get_tessdata_path()
                    )
                    text = page.get_text("text", textpage=textpage).strip()
                except Exception as exc:
                    ocr_failures += 1
                    logger.warning("OCR fallback failed on page %s: %s", index, exc)
            pages.append(f"[Page {index}]\n{text}")

        combined_text = "\n\n".join(pages).strip()
        if not doc.page_count or not re.sub(r"\[Page \d+\]\s*", "", combined_text).strip():
            logger.warning("No extractable text found; OCR failures=%s.", ocr_failures)
            return "Error: The uploaded PDF contains no extractable text."

        logger.info("Extracted %s PDF pages with %s OCR failures.", doc.page_count, ocr_failures)
        return combined_text
    except Exception as exc:
        logger.warning("PDF extraction failed: %s", exc)
        return "Error: The uploaded PDF appears to be corrupted or unreadable."
    finally:
        doc.close()


def get_page_number_from_marker(text_chunk: str) -> int | None:
    """Return the first page number marker found in a text chunk, if present."""
    match = re.search(r"\[Page (\d+)\]", text_chunk)
    return int(match.group(1)) if match else None
