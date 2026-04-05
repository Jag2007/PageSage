import logging
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import streamlit as st
from groq import APIConnectionError, AuthenticationError, BadRequestError, RateLimitError

from app.ingest import ingest_documents, load_existing_index
from app.rag import build_qa_chain

logger = logging.getLogger(__name__)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "chunks_count" not in st.session_state:
    st.session_state.chunks_count = 0

try:
    vectorstore = load_existing_index()
    if vectorstore is not None and st.session_state.qa_chain is None:
        st.session_state.vectorstore = vectorstore
        st.session_state.qa_chain = build_qa_chain(vectorstore)
except Exception as exc:
    logger.warning("Failed to restore existing index on startup: %s", exc)

st.set_page_config(page_title="PageSage", page_icon="📖", layout="wide")

st.markdown(
    """
    <div style="padding: 3.5rem 0 3rem 0;">
        <div style="font-size: 3rem; font-weight: 700; letter-spacing: 0.18em; color: #1A1A1A;">
            PageSage
        </div>
        <div style="margin-top: 0.85rem; font-size: 1rem; font-style: italic; color: #C9A84C;">
            Wisdom from every page.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 📄 Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs", type=["pdf"], accept_multiple_files=True, key="uploaded_files"
    )
    if st.button("Ingest Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF first.")
        else:
            with st.spinner("Processing your documents..."):
                try:
                    vectorstore = ingest_documents(uploaded_files)
                    st.session_state.vectorstore = vectorstore
                    st.session_state.qa_chain = build_qa_chain(vectorstore)
                    st.session_state.chunks_count = vectorstore.index.ntotal
                    st.success(
                        f"✓ {st.session_state.chunks_count} chunks indexed from "
                        f"{len(uploaded_files)} documents."
                    )
                except ValueError:
                    st.error("No extractable text found. Please upload a readable PDF.")
                    logger.warning("Document ingestion produced no extractable chunks.")
                except Exception:
                    logger.exception("Document ingestion failed.")
                    st.error("Something went wrong during ingestion. Please try again.")

    st.caption("Settings coming soon.")
    st.divider()
    st.markdown("### 🗂 Conversation")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

if st.session_state.vectorstore is None:
    st.markdown(
        """
        <div style="padding-top: 12vh; text-align: center; color: #7A7A74;">
            <div style="font-size: 1rem;">Upload your PDFs from the sidebar to begin.</div>
            <div style="margin-top: 0.5rem; font-size: 0.95rem;">PageSage will find the wisdom within.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📄 Sources"):
                    for doc in message["sources"]:
                        source = doc.metadata.get("source", "Unknown")
                        page = doc.metadata.get("page", "—")
                        st.markdown(f"**Source:** {source} — Page {page}")
                        st.caption(doc.page_content)

    user_input = st.chat_input("Ask anything from your documents...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                with st.spinner("PageSage is thinking..."):
                    result = st.session_state.qa_chain.invoke({"query": user_input})
                answer = result["result"]
                source_docs = result["source_documents"]
                st.markdown(answer)
                if source_docs:
                    with st.expander("📄 Sources"):
                        for doc in source_docs:
                            source = doc.metadata.get("source", "Unknown")
                            page = doc.metadata.get("page", "—")
                            st.markdown(f"**Source:** {source} — Page {page}")
                            st.caption(doc.page_content)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": source_docs}
                )
            except AuthenticationError:
                logger.exception("Groq authentication failed during chat request.")
                st.error("Groq authentication failed. Please check your API key in `.env`.")
            except APIConnectionError:
                logger.exception("Groq connection failed during chat request.")
                st.error("PageSage could not reach Groq. Please check your internet connection and try again.")
            except RateLimitError:
                logger.exception("Groq rate limit reached during chat request.")
                st.error("Groq rate limits were reached. Please wait a moment and try again.")
            except BadRequestError:
                logger.exception("Groq rejected the chat request.")
                st.error("The selected Groq model is unavailable or the request was rejected.")
            except ValueError:
                logger.exception("PageSage chat configuration is invalid.")
                st.error("PageSage is not fully configured. Please verify your `.env` settings.")
            except Exception:
                logger.exception("Unexpected chat failure.")
                st.error("PageSage encountered an issue. Please try again.")
