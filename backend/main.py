"""FastAPI entrypoint for the PageSage backend."""

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import APP_NAME
from app.ingest import ingest_documents, load_existing_db
from app.rag import query_rag

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
db = load_existing_db()


class AskRequest(BaseModel):
    """Request body for the ask endpoint."""

    question: str


@app.get("/health")
def health() -> dict[str, str]:
    """Return backend health information."""
    return {"status": "ok", "app": APP_NAME}


@app.post("/upload_pdf")
async def upload_pdf(files: list[UploadFile] = File(...)) -> dict[str, int | str]:
    """Upload PDFs, ingest them into ChromaDB, and update the active database."""
    global db
    try:
        normalized_files = [
            {"filename": file.filename or "document.pdf", "content": await file.read()}
            for file in files
        ]
        result = ingest_documents(normalized_files)
        db = load_existing_db()
        return {
            "message": "Ingested successfully",
            "chunks": result["chunks"],
            "files": result["files"],
        }
    except ValueError as exc:
        logger.warning("Upload rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Upload failed.")
        raise HTTPException(status_code=500, detail="Document ingestion failed.") from exc


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    """Answer a question against the active ChromaDB collection."""
    if db is None:
        return {"answer": "Please upload a PDF first.", "sources": [], "confidence": "LOW"}
    try:
        return query_rag(request.question, db)
    except Exception as exc:
        logger.exception("Question answering failed.")
        raise HTTPException(status_code=500, detail="Question answering failed.") from exc


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))