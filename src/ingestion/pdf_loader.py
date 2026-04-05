from __future__ import annotations

import sys
import os
import tempfile
from src.logger import logging
from src.exception import MyException
from langchain_community.document_loaders import PyMuPDFLoader
from entity.config_entity import TextSplitterConfig
from entity.artifact_entity import PDFLoaderArtifact


class PDFLoader:
    def __init__(self):
        logging.info("Initializing PDFLoader")

    def initiate_pdf_loader(self, file_bytes: bytes, filename: str) -> PDFLoaderArtifact:
        """Write bytes to a temp file, load with PyMuPDF, return artifact."""
        try:
            logging.info(f"Loading PDF: {filename}")

            if not file_bytes:
                raise ValueError("No bytes received for PDF loading.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            try:
                loader = PyMuPDFLoader(tmp_path)
                docs = loader.load()
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

            artifact = PDFLoaderArtifact(
                docs=docs,
                num_pages=len(docs),
                filename=filename,
            )

            logging.info(f"PDF loaded: {len(docs)} pages from {filename}")
            return artifact

        except Exception as e:
            raise MyException(e, sys)
