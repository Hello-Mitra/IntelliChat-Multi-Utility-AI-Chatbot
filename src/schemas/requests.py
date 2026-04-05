from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    thread_id: str


class ChatResponse(BaseModel):
    answer: str
    thread_id: str


class IngestResponse(BaseModel):
    filename: str
    num_pages: int
    num_chunks: int
    thread_id: str


class ThreadsResponse(BaseModel):
    threads: dict[str, str]


class TitleRequest(BaseModel):
    thread_id: str
    title: str


class SaveTitleResponse(BaseModel):
    thread_id: str
    title: str
    status: str = "saved"
