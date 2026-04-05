from __future__ import annotations

from typing import Any, Dict, Optional

# Per-thread in-memory stores — populated at startup and on PDF ingest
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def set_retriever(thread_id: str, retriever: Any) -> None:
    """Store a retriever for a thread."""
    _THREAD_RETRIEVERS[str(thread_id)] = retriever


def get_retriever(thread_id: Optional[str]) -> Optional[Any]:
    """Fetch the retriever for a thread, or None if not found."""
    if thread_id and str(thread_id) in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[str(thread_id)]
    return None


def set_metadata(thread_id: str, metadata: dict) -> None:
    """Store PDF metadata for a thread."""
    _THREAD_METADATA[str(thread_id)] = metadata


def get_metadata(thread_id: str) -> dict:
    """Fetch PDF metadata for a thread."""
    return _THREAD_METADATA.get(str(thread_id), {})


def has_document(thread_id: str) -> bool:
    """Check if a thread has an indexed document."""
    return str(thread_id) in _THREAD_RETRIEVERS
