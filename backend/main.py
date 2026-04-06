"""FastAPI entrypoint for the PageSage backend."""

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load env variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App init
app = FastAPI(title="PageSage")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global DB (lazy loaded)
db = None


# -------------------------
# Models
# -------------------------
class AskRequest(BaseModel):
    question: str


# -------------------------
# Routes
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok", "app": "PageSage"}


@app.post("/upload_pdf")
async def upload_pdf(files: list[UploadFile] = File(...)):
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

        # Reload DB after ingestion
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
    global db

    try:
        # Lazy load DB (THIS FIXES YOUR DEPLOY ISSUE 🚀)
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


# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)