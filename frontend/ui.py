"""Streamlit frontend for PageSage."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="PageSage", page_icon="📖", layout="wide")

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
    <div style="padding: 3.5rem 0 3rem 0;">
        <div style="font-size: 3rem; font-weight: 700; letter-spacing: 0.18em; color: #F4FAFF;">
            PageSage
        </div>
        <div style="margin-top: 0.85rem; font-size: 1rem; font-style: italic; color: #7EC8FF;">
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
                    files = [
                        ("files", (file.name, file.getvalue(), "application/pdf"))
                        for file in uploaded_files
                    ]
                    response = requests.post(f"{BACKEND_URL}/upload_pdf", files=files, timeout=60)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.pdf_uploaded = True
                    st.success(f"✓ {data['chunks']} chunks indexed from {data['files']} documents.")
                except requests.RequestException as exc:
                    detail = getattr(exc.response, "text", "") if getattr(exc, "response", None) else ""
                    st.error(f"PageSage could not ingest the PDF. {detail}".strip())

    st.divider()
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

if not st.session_state.pdf_uploaded:
    st.markdown(
        """
        <div style="padding-top: 12vh; text-align: center; color: #B9D9F3;">
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
                    for source in message["sources"]:
                        st.markdown(f"**Source:** {source['source']} — Page {source.get('page', '—')}")
                        st.caption(source.get("content", ""))

    user_input = st.chat_input("Ask anything from your documents...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                with st.spinner("PageSage is thinking..."):
                    response = requests.post(
                        f"{BACKEND_URL}/ask", json={"question": user_input}, timeout=60
                    )
                    response.raise_for_status()
                    data = response.json()
                st.markdown(data["answer"])
                if data.get("sources"):
                    with st.expander("📄 Sources"):
                        for source in data["sources"]:
                            st.markdown(f"**Source:** {source['source']} — Page {source.get('page', '—')}")
                            st.caption(source.get("content", ""))
                st.session_state.messages.append(
                    {"role": "assistant", "content": data["answer"], "sources": data.get("sources", [])}
                )
            except requests.RequestException:
                st.error("PageSage encountered an issue. Please try again.")
