"""Configuration constants for the PageSage backend."""

APP_NAME = "PageSage"
APP_TAGLINE = "Wisdom from every page."
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.1-8b-instant"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
CHROMA_PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION_NAME = "pagesage"
TOP_K = 4
