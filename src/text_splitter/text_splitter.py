from __future__ import annotations

import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logger import logging
from src.exception import MyException
from entity.config_entity import TextSplitterConfig
from entity.artifact_entity import PDFLoaderArtifact, TextSplitterArtifact


class TextSplitter:
    def __init__(self, config: TextSplitterConfig):
        try:
            logging.info(f"Initializing TextSplitter — chunk_size={config.chunk_size}, overlap={config.chunk_overlap}")
            self.config = config
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                separators=["\n\n", "\n", " ", ""],
            )
            logging.info("TextSplitter initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_text_splitter(self, pdf_loader_artifact: PDFLoaderArtifact) -> TextSplitterArtifact:
        try:
            logging.info(f"Splitting {pdf_loader_artifact.num_pages} pages into chunks")
            chunks = self.splitter.split_documents(pdf_loader_artifact.docs)
            logging.info(f"Created {len(chunks)} chunks")

            return TextSplitterArtifact(
                chunks=chunks,
                num_chunks=len(chunks),
            )
        except Exception as e:
            raise MyException(e, sys)
