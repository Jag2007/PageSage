"""FastAPI entrypoint for the PageSage backend."""

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PageSage")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = None


class AskRequest(BaseModel):
    """Request body for the ask endpoint."""

    question: str


@app.get("/health")
def health():
    """Return backend health status."""
    return {"status": "ok", "app": "PageSage"}


@app.get("/")
def root():
    """Return a simple API running message."""
    return {"message": "PageSage API is running 🚀"}


@app.post("/upload_pdf")
async def upload_pdf(files: list[UploadFile] = File(...)):
    """Upload PDFs and ingest them into ChromaDB."""
    global db
    try:
        from app.ingest import ingest_documents, load_existing_db

        normalized_files = [
            {
                "filename": file.filename or "document.pdf",
                "content": await file.read()
            }
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
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.exception("Upload failed.")
        raise HTTPException(status_code=500, detail="Document ingestion failed.")


@app.post("/ask")
def ask(request: AskRequest):
    """Answer a question against the current ChromaDB collection."""
    global db

    try:
        if db is None:
            from app.ingest import load_existing_db
            db = load_existing_db()

        if db is None:
            return {
                "answer": "Please upload a PDF first.",
                "sources": [],
                "confidence": "LOW"
            }

        from app.rag import query_rag
        return query_rag(request.question, db)

    except Exception as exc:
        logger.exception("Question answering failed.")
        raise HTTPException(
            status_code=500,
            detail="Question answering failed."
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
