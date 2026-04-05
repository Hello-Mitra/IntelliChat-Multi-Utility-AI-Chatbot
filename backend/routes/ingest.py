from __future__ import annotations

import sys
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from src.logger import logging
from src.exception import MyException
from src.schemas.requests import IngestResponse
from pipeline.ingest_pipeline import IngestPipeline

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    request: Request,
    file: UploadFile = File(...),
    thread_id: str = Form(...),
):
    """
    Upload and index a PDF for a given thread.
    Accepts multipart/form-data with fields: file (PDF) and thread_id (string).
    """
    try:
        logging.info(f"Ingest request — thread={thread_id}, file={file.filename}")

        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        file_bytes = await file.read()

        pipeline = IngestPipeline()
        artifact = pipeline.run(
            file_bytes=file_bytes,
            thread_id=thread_id,
            filename=file.filename,
        )

        logging.info(f"Ingest complete — {artifact.num_chunks} chunks for thread={thread_id}")

        return IngestResponse(
            filename=artifact.filename,
            num_pages=artifact.num_pages,
            num_chunks=artifact.num_chunks,
            thread_id=thread_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Ingest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(MyException(e, sys)))
