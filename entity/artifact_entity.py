from dataclasses import dataclass
from typing import Any, List


@dataclass
class PDFLoaderArtifact:
    docs: List[Any]
    num_pages: int
    filename: str


@dataclass
class TextSplitterArtifact:
    chunks: List[Any]
    num_chunks: int


@dataclass
class EmbeddingArtifact:
    embedding_model: Any


@dataclass
class VectorStoreArtifact:
    vector_store: Any
    index_save_path: str


@dataclass
class RetrieverArtifact:
    retriever: Any
    search_type: str
    top_k: int


@dataclass
class PDFIngestArtifact:
    filename: str
    num_pages: int
    num_chunks: int
    index_save_path: str


@dataclass
class ChatArtifact:
    answer: str
    thread_id: str
    question: str
