from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.logger import logging
from src.exception import MyException
from pipeline.chat_pipeline import ChatPipeline
from src.db.title_store import TitleStore
from backend.routes import chat, ingest

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build chatbot and shared state once on startup."""
    try:
        logging.info("Starting Multi Utility AI Chatbot API")
        pipeline = ChatPipeline()
        chatbot, checkpointer_instance = pipeline.build()

        title_store = TitleStore(conn=checkpointer_instance.get_conn())

        # Share via app.state so routes can access them
        app.state.chatbot     = chatbot
        app.state.checkpointer_instance = checkpointer_instance
        app.state.title_store = title_store

        logging.info("API startup complete")
        yield

    except Exception as e:
        raise MyException(e, sys)
    finally:
        logging.info("API shutting down")


app = FastAPI(
    title="Multi Utility AI Chatbot API",
    description="LangGraph chatbot with RAG, web search, stock prices and calculator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router,   prefix="/api")
app.include_router(ingest.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
