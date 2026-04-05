# 📖 PageSage
### *Wisdom from every page.*

PageSage is a local, privacy-first document intelligence tool built for anyone who needs to extract knowledge from PDF documents without sending data to the cloud. Upload your research papers, contracts, reports, or notes — PageSage ingests them, understands them, and answers your questions with precise, source-cited responses. Built with LangChain, FAISS, and Groq, it runs embedding and retrieval entirely on your machine, using the internet only for LLM inference.

```text
PDF Upload → Text Extraction → Chunking → Embedding → FAISS Index
                                                           ↓
                                         Answer ← LLM ← Retriever
```

1. Clone the repository: `git clone https://github.com/your-username/PageSage.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API key to `.env` — open the file and replace `your_groq_api_key_here` with your real key from `console.groq.com`
4. Run the app: `streamlit run ui.py`

- Retrieve: When you ask a question, PageSage searches your ingested documents for the most relevant passages using vector similarity — not keyword matching.
- Augment: Those retrieved passages are added to the prompt sent to the LLM, grounding the answer in your actual documents rather than general knowledge.
- Generate: The LLM reads the context and produces a precise, cited answer — if the answer isn't in your documents, PageSage says so honestly.

PageSage is agentic in the sense that it doesn't just pattern-match your question to a document — it reasons over retrieved context before responding. The prompt instructs the model to think through what the sources say, cite where the answer comes from, and explicitly acknowledge when the documents don't contain the answer. A clearly marked extension point in `app/rag.py` allows query rewriting, multi-hop retrieval, and answer verification to be layered in as the next evolution.

| Component | Tool | Why |
| --- | --- | --- |
| UI | Streamlit | Fast, elegant, Python-native |
| LLM | Groq — llama3-8b-8192 | Free, fast, swappable via config |
| Embeddings | HuggingFace all-MiniLM-L6-v2 | Fully local, no API key needed |
| Vector Store | FAISS | Persistent, offline, disk-saved |
| PDF Parsing | PyMuPDF | Fast and handles complex layouts |
| RAG Framework | LangChain | Clean chain abstraction, extensible |
| Environment | python-dotenv | Single `.env` for all secrets |

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

*Built with care by Tejaswini Palwai — because every page deserves to be understood.*
