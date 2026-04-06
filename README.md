# 📖 PageSage
### *Wisdom from every page.*

PageSage is a production-style document intelligence RAG system split into two independently deployable services. The FastAPI backend owns PDF processing, OCR fallback, chunking, embeddings, ChromaDB persistence, retrieval, and Groq generation. The Streamlit frontend owns only the user interface and calls the backend over HTTP.

The current visual direction is calm and editorial with dark blues, light blues, and whites.

## Architecture

```text
PDF Upload (Streamlit UI)
        ↓ HTTP POST /upload_pdf
FastAPI Backend (Render)
        ↓
Text Extraction + OCR Fallback (PyMuPDF)
        ↓
Chunking (RecursiveCharacterTextSplitter)
        ↓
Embedding (HuggingFace)
        ↓
ChromaDB Persistent Store
        ↓
User Question (Streamlit UI)
        ↓ HTTP POST /ask
Retriever → Groq LLM → Answer + Sources
```

## Local Development

1. Clone the repository:

```bash
git clone https://github.com/your-username/PageSage.git
cd PageSage
```

2. Create the root `.env` file:

```bash
printf "GROQ_API_KEY=your_groq_api_key_here\nBACKEND_URL=http://localhost:8000\n" > .env
```

Replace `your_groq_api_key_here` with your real key from `https://console.groq.com`.

3. Run the backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. In a second terminal, run the frontend:

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run ui.py
```

Open the Streamlit URL, upload PDFs, ingest them, then ask questions.

## Deployment

### Backend on Render

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Runtime: `backend/runtime.txt`
- Environment variable: `GROQ_API_KEY`

For OCR on scanned/image-only PDFs, install Tesseract in the backend environment. The code still handles missing OCR support gracefully, but image-only pages require Tesseract to extract text.

### Frontend on Streamlit Cloud

- Main file path: `frontend/ui.py`
- Requirements file: `frontend/requirements.txt`
- Runtime: `frontend/runtime.txt`
- Environment variable or secret: `BACKEND_URL=https://your-render-backend-url`

The frontend should not contain the Groq key. It only sends PDF uploads and questions to the backend.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check backend health |
| `POST` | `/upload_pdf` | Upload one or more PDFs and build the ChromaDB index |
| `POST` | `/ask` | Ask a question against the current ChromaDB collection |

## Environment Variables

| Variable | Service | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | Backend | Authenticates Groq LLM requests |
| `BACKEND_URL` | Frontend | Points Streamlit to the FastAPI backend |

## Tech Stack

| Component | Tool | Why |
| --- | --- | --- |
| Backend API | FastAPI | Clean HTTP boundary for RAG logic |
| Frontend | Streamlit | Fast UI iteration and hosted frontend |
| LLM | Groq — `llama-3.1-8b-instant` | Current working fast hosted model |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` | Local embeddings with no API key |
| Vector Store | ChromaDB | Persistent local vector database |
| PDF Parsing | PyMuPDF | Fast PDF text extraction with OCR fallback |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` | Consistent chunks with overlap |
| Environment | python-dotenv | Local `.env` loading |

## Project Structure

```text
PageSage/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── embeddings.py
│   │   ├── ingest.py
│   │   ├── pdf_utils.py
│   │   └── rag.py
│   ├── main.py
│   ├── requirements.txt
│   └── runtime.txt
├── frontend/
│   ├── .streamlit/
│   │   └── config.toml
│   ├── ui.py
│   ├── requirements.txt
│   └── runtime.txt
├── assets/
│   └── logo.png
├── .env
├── .gitignore
└── README.md
```

*Built with care by Jagruthi Pulumati — because every page deserves to be understood.*
