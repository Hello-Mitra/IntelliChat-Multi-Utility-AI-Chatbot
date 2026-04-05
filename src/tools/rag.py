from __future__ import annotations

from typing import Optional
from langchain_core.tools import tool
from src.utils.thread_store import get_retriever, get_metadata


@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Always include the thread_id when calling this tool.

    Args:
        query: The question to search for in the document.
        thread_id: The current conversation thread ID.

    Returns:
        A dict with retrieved context chunks and source metadata.
    """
    retriever = get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Please upload a PDF first.",
            "query": query,
        }

    results = retriever.invoke(query)
    return {
        "query": query,
        "context": [doc.page_content for doc in results],
        "metadata": [doc.metadata for doc in results],
        "source_file": get_metadata(str(thread_id) if thread_id else "").get("filename"),
    }
