from __future__ import annotations

import sys
from src.logger import logging
from src.exception import MyException
from src.ingestion.pdf_loader import PDFLoader
from src.text_splitter.text_splitter import TextSplitter
from src.embeddings.embedding_model import EmbeddingModel
from src.vector_store.faiss_store import VectorStore
from src.retriever.retriever import Retriever
from src.utils.thread_store import set_retriever, set_metadata
from entity.config_entity import (
    TextSplitterConfig,
    EmbeddingConfig,
    VectorStoreConfig,
    RetrieverConfig,
)
from entity.artifact_entity import PDFIngestArtifact


class IngestPipeline:
    """
    Orchestrates: PDF bytes → loader → splitter → embeddings → FAISS → retriever
    Stores the retriever in thread_store so the LangGraph rag_tool can access it.
    """

    def __init__(self):
        self.text_splitter_config  = TextSplitterConfig()
        self.embedding_config      = EmbeddingConfig()
        self.vector_store_config   = VectorStoreConfig()
        self.retriever_config      = RetrieverConfig()

    def run(self, file_bytes: bytes, thread_id: str, filename: str) -> PDFIngestArtifact:
        logging.info("=" * 80)
        logging.info(f"Starting IngestPipeline for thread={thread_id}, file={filename}")
        logging.info("=" * 80)
        try:
            # 1. Load PDF
            logging.info("Step 1 — PDF Loader")
            pdf_loader = PDFLoader()
            pdf_artifact = pdf_loader.initiate_pdf_loader(file_bytes=file_bytes, filename=filename)

            # 2. Split
            logging.info("Step 2 — Text Splitter")
            splitter = TextSplitter(config=self.text_splitter_config)
            split_artifact = splitter.initiate_text_splitter(pdf_loader_artifact=pdf_artifact)

            # 3. Embeddings
            logging.info("Step 3 — Embedding Model")
            embedding_model = EmbeddingModel(config=self.embedding_config)
            embedding_artifact = embedding_model.initiate_embedding_model()

            # 4. Vector store
            logging.info("Step 4 — Vector Store")
            vector_store = VectorStore(
                config=self.vector_store_config,
                embedding_artifact=embedding_artifact,
            )
            vs_artifact = vector_store.initiate_vector_store(
                text_splitter_artifact=split_artifact,
                thread_id=thread_id,
            )

            # 5. Retriever
            logging.info("Step 5 — Retriever")
            retriever = Retriever(
                config=self.retriever_config,
                vector_store_artifact=vs_artifact,
            )
            retriever_artifact = retriever.initiate_retriever()

            # 6. Store in thread_store so rag_tool can access it at query time
            set_retriever(thread_id, retriever_artifact.retriever)
            set_metadata(thread_id, {
                "filename": filename,
                "num_pages": pdf_artifact.num_pages,
                "num_chunks": split_artifact.num_chunks,
            })

            ingest_artifact = PDFIngestArtifact(
                filename=filename,
                num_pages=pdf_artifact.num_pages,
                num_chunks=split_artifact.num_chunks,
                index_save_path=vs_artifact.index_save_path,
            )

            logging.info("=" * 80)
            logging.info(f"IngestPipeline completed — {split_artifact.num_chunks} chunks indexed")
            logging.info("=" * 80)
            return ingest_artifact

        except Exception as e:
            raise MyException(e, sys)
