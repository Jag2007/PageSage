"""Streamlit frontend for PageSage."""

import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

REQUEST_TIMEOUT = 300
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_backend_url() -> str:
    """Load the backend URL from environment configuration."""
    backend_url = os.getenv("BACKEND_URL")
    if not backend_url:
        try:
            backend_url = st.secrets.get("BACKEND_URL", "")
        except Exception:
            backend_url = ""
    if not backend_url:
        st.error("BACKEND_URL is not configured. Add it to .env or Streamlit secrets."); st.stop()
    return backend_url.rstrip("/")


def get_error_detail(response: requests.Response | None) -> str:
    """Extract a readable backend error message from an HTTP response."""
    if response is None:
        return ""
    try:
        data = response.json()
        detail = data.get("detail", "")
        return "; ".join(str(item.get("msg", item)) for item in detail) if isinstance(detail, list) else str(detail)
    except ValueError:
        return response.text.strip()

def render_sources(sources: list[dict[str, object]]) -> None:
    """Render retrieved source chunks in a compact expander."""
    if not sources: return
    with st.expander("📄 Sources"):
        for source in sources:
            st.markdown(f"**Source:** {source['source']} — Page {source.get('page', '—')}")
            st.caption(source.get("content", ""))

st.set_page_config(page_title="PageSage", page_icon="📖", layout="wide")
BACKEND_URL = get_backend_url()

st.session_state.setdefault("pdf_uploaded", False)
st.session_state.setdefault("messages", [])

st.markdown(
    """<div style="padding:3.5rem 0 3rem 0;">
    <div style="font-size:3rem;font-weight:700;letter-spacing:0.18em;color:#F4FAFF;">PageSage</div>
    <div style="margin-top:0.85rem;font-size:1rem;font-style:italic;color:#7EC8FF;">Wisdom from every page.</div>
    </div>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 📄 Documents")
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, key="uploaded_files")
    if st.button("Ingest Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF first.")
        else:
            with st.spinner("Processing your documents..."):
                try:
                    files = [("files", (file.name, file.getvalue(), "application/pdf")) for file in uploaded_files]
                    response = requests.post(f"{BACKEND_URL}/upload_pdf", files=files, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.pdf_uploaded = True
                    st.success(f"✓ {data['chunks']} chunks indexed from {data['files']} documents.")
                except requests.RequestException as exc:
                    detail = get_error_detail(getattr(exc, "response", None))
                    message = "PageSage could not ingest the PDF."
                    st.error(f"{message} {detail}".strip())

    st.divider()
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

if not st.session_state.pdf_uploaded:
    st.markdown(
        """<div style="padding-top:12vh;text-align:center;color:#B9D9F3;">
        <div style="font-size:1rem;">Upload your PDFs from the sidebar to begin.</div>
        <div style="margin-top:0.5rem;font-size:0.95rem;">PageSage will find the wisdom within.</div>
        </div>""",
        unsafe_allow_html=True,
    )
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                render_sources(message["sources"])

    user_input = st.chat_input("Ask anything from your documents...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                with st.spinner("PageSage is thinking..."):
                    response = requests.post(f"{BACKEND_URL}/ask", json={"question": user_input}, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                data = response.json()
                st.markdown(data["answer"])
                render_sources(data.get("sources", []))
                st.session_state.messages.append(
                    {"role": "assistant", "content": data["answer"], "sources": data.get("sources", [])}
                )
            except requests.RequestException as exc:
                detail = get_error_detail(getattr(exc, "response", None))
                message = "PageSage encountered an issue. Please try again."
                st.error(f"{message} {detail}".strip())
