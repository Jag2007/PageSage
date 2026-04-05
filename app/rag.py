"""RAG chain construction for PageSage."""

import logging
import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq

from app.config import LLM_MODEL, LLM_PROVIDER, TOP_K

load_dotenv()

logger = logging.getLogger(__name__)


def get_llm() -> BaseChatModel:
    """Load the configured chat model provider while keeping the LLM layer swappable."""
    logger.info("Loading LLM provider: %s", LLM_PROVIDER)
    if LLM_PROVIDER == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY is missing or still set to the placeholder value.")
        return ChatGroq(model=LLM_MODEL, api_key=api_key)
    # elif LLM_PROVIDER == "ollama":
    #     from langchain_community.llms import Ollama
    #     return Ollama(model=LLM_MODEL)
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def build_qa_chain(vectorstore: FAISS) -> RetrievalQA:
    """Build the RetrievalQA chain with source-returning retrieval and a grounded prompt."""
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are PageSage, an elegant and precise document intelligence assistant. "
            "Your tagline is 'Wisdom from every page.' Use ONLY the context below to answer "
            "the question. If the answer cannot be found in the provided documents, respond "
            "with: 'The pages don't speak to this — please upload a relevant document.' "
            "Always mention which part of the document your answer comes from, including "
            "the file name and page number if available. Be concise, clear, and wise. "
            "Context: {context} Question: {question} Answer:"
        ),
    )
    chain = RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": TOP_K}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    logger.info("RetrievalQA chain built successfully.")
    # AGENTIC EXTENSION POINT:
    # Query rewriting, multi-hop retrieval, or answer verification
    # can be layered in here before returning the chain.
    # e.g. wrap with an agent executor or add a self-check step.
    return chain
