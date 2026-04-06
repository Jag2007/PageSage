# 📖 PageSage
### *Wisdom from every page.*

PageSage is a local, privacy-first document intelligence tool for extracting knowledge from PDF documents. Upload research papers, contracts, reports, notes, or technical manuals, then ask questions and receive precise, source-cited answers. Embedding and retrieval run locally with HuggingFace embeddings and FAISS; Groq is used only for LLM inference.

The interface is intentionally refined: a dark blue, light blue, and white Streamlit experience with a calm document-reader feel rather than a noisy chatbot aesthetic.

## Architecture

```text
PDF Upload → Text Extraction → Chunking → Embedding → FAISS Index
                                                           ↓
                                         Answer ← LLM ← Retriever
```

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/your-username/PageSage.git
cd PageSage
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add your Groq API key:

```bash
printf "GROQ_API_KEY=your_groq_api_key_here\n" > .env
```

Replace `your_groq_api_key_here` with your real key from `https://console.groq.com`.

5. Run PageSage:

```bash
streamlit run ui.py
```

If your shell cannot find `streamlit`, run:

```bash
python -m streamlit run ui.py
```

## How It Works

- Retrieve: PageSage searches your ingested PDFs for the most relevant passages using vector similarity, not keyword matching.
- Augment: The retrieved passages are inserted into the LLM prompt so answers stay grounded in your uploaded documents.
- Generate: The LLM produces a concise, cited answer; if the documents do not contain the answer, PageSage says so instead of guessing.

## Agentic Behavior

PageSage is agentic in the sense that it does not simply paste retrieved chunks into the chat. The RAG prompt asks the model to reason over the retrieved context, cite the file and page where possible, and admit when the pages do not contain the answer. `app/rag.py` also includes a clear extension point for future query rewriting, multi-hop retrieval, or answer verification.

## Tech Stack

| Component | Tool | Why |
| --- | --- | --- |
| UI | Streamlit | Fast, polished, Python-native interface |
| LLM | Groq — `llama-3.1-8b-instant` | Fast hosted inference with one API key |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` | Local embeddings with no API key |
| Vector Store | FAISS | Persistent local retrieval index |
| PDF Parsing | PyMuPDF | Reliable text extraction from PDF bytes |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` | Consistent chunks with overlap |
| RAG Framework | LangChain | Clean retriever and QA chain abstraction |
| Environment | python-dotenv | Simple `.env` secret loading |

## Project Structure

```text
PageSage/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── embeddings.py
│   ├── ingest.py
│   ├── pdf_utils.py
│   └── rag.py
├── assets/
│   └── logo.png
├── .streamlit/
│   └── config.toml
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── ui.py
```

## Notes

- PDF text extraction, chunking, embeddings, and FAISS retrieval run locally.
- Groq requires internet access because the LLM is hosted.
- FAISS indexes are saved under `faiss_index/default_workspace`.
- `.env`, `venv/`, and `faiss_index/` are intentionally ignored by Git.

*Built with care by Jagruthi Pulumati — because every page deserves to be understood.*
