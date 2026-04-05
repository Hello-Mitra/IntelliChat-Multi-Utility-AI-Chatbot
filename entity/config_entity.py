from dataclasses import dataclass
from config.settings import settings


@dataclass
class LLMConfig:
    model_name: str = settings.model_name
    temperature: float = settings.temperature


@dataclass
class EmbeddingConfig:
    embedding_model: str = settings.embedding_model


@dataclass
class TextSplitterConfig:
    chunk_size: int = settings.chunk_size
    chunk_overlap: int = settings.chunk_overlap


@dataclass
class RetrieverConfig:
    search_type: str = settings.search_type
    top_k: int = settings.top_k


@dataclass
class VectorStoreConfig:
    faiss_index_dir: str = settings.faiss_index_dir


@dataclass
class CheckpointerConfig:
    db_path: str = settings.db_path
