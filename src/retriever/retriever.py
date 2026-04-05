from __future__ import annotations

import sys
from src.logger import logging
from src.exception import MyException
from entity.config_entity import RetrieverConfig
from entity.artifact_entity import VectorStoreArtifact, RetrieverArtifact


class Retriever:
    def __init__(self, config: RetrieverConfig, vector_store_artifact: VectorStoreArtifact):
        try:
            logging.info(f"Initializing Retriever — search_type={config.search_type}, top_k={config.top_k}")
            self.config = config
            self.vector_store = vector_store_artifact.vector_store
            logging.info("Retriever initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_retriever(self) -> RetrieverArtifact:
        try:
            logging.info("Building retriever")
            retriever = self.vector_store.as_retriever(
                search_type=self.config.search_type,
                search_kwargs={"k": self.config.top_k},
            )
            logging.info("Retriever built successfully")

            return RetrieverArtifact(
                retriever=retriever,
                search_type=self.config.search_type,
                top_k=self.config.top_k,
            )
        except Exception as e:
            raise MyException(e, sys)
