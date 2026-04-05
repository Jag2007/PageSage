import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "chunks_count" not in st.session_state:
    st.session_state.chunks_count = 0

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
    # --- Document Upload ---

    # --- Settings ---

    # --- Conversation Controls ---
    pass

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
