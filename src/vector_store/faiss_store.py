from __future__ import annotations

import sys
import os
from langchain_community.vectorstores import FAISS
from src.logger import logging
from src.exception import MyException
from entity.config_entity import VectorStoreConfig
from entity.artifact_entity import EmbeddingArtifact, TextSplitterArtifact, VectorStoreArtifact


class VectorStore:
    def __init__(self, config: VectorStoreConfig, embedding_artifact: EmbeddingArtifact):
        try:
            logging.info("Initializing VectorStore")
            self.config = config
            self.embedding_model = embedding_artifact.embedding_model
            logging.info("VectorStore initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_vector_store(
        self,
        text_splitter_artifact: TextSplitterArtifact,
        thread_id: str,
    ) -> VectorStoreArtifact:
        try:
            logging.info(f"Building FAISS store from {text_splitter_artifact.num_chunks} chunks")
            store = FAISS.from_documents(text_splitter_artifact.chunks, self.embedding_model)

            index_save_path = os.path.join(self.config.faiss_index_dir, f"faiss_index_{thread_id}")
            os.makedirs(self.config.faiss_index_dir, exist_ok=True)
            store.save_local(index_save_path)

            logging.info(f"FAISS index saved to {index_save_path}")

            return VectorStoreArtifact(
                vector_store=store,
                index_save_path=index_save_path,
            )
        except Exception as e:
            raise MyException(e, sys)

    @staticmethod
    def load_local(index_path: str, embedding_model) -> FAISS:
        """Load a saved FAISS index from disk."""
        return FAISS.load_local(
            index_path,
            embedding_model,
            allow_dangerous_deserialization=True,
        )
