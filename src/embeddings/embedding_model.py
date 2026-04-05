from __future__ import annotations

import sys
from langchain_openai import OpenAIEmbeddings
from src.logger import logging
from src.exception import MyException
from entity.config_entity import EmbeddingConfig
from entity.artifact_entity import EmbeddingArtifact


class EmbeddingModel:
    def __init__(self, config: EmbeddingConfig):
        try:
            logging.info(f"Initializing EmbeddingModel — model={config.embedding_model}")
            self.config = config
            self.model = OpenAIEmbeddings(model=config.embedding_model)
            logging.info("EmbeddingModel initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_embedding_model(self) -> EmbeddingArtifact:
        try:
            logging.info("Creating EmbeddingArtifact")
            artifact = EmbeddingArtifact(embedding_model=self.model)
            logging.info("EmbeddingArtifact created successfully")
            return artifact
        except Exception as e:
            raise MyException(e, sys)
