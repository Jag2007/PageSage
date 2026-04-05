"""Application configuration constants for PageSage."""

APP_NAME = "PageSage"
APP_TAGLINE = "Wisdom from every page."
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_PROVIDER = "groq"  # isolate this — swapping to "ollama" later should be one line
LLM_MODEL = "llama-3.1-8b-instant"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
FAISS_INDEX_PATH = "faiss_index/default_workspace"
TOP_K = 4
