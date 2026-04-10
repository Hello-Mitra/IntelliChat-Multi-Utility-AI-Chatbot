from __future__ import annotations

import sys
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.logger import logging
from src.exception import MyException
from src.schemas.requests import (
    ChatRequest, ChatResponse,
    ThreadsResponse, TitleRequest, SaveTitleResponse
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: Request, body: ChatRequest):
    """Invoke the chatbot for a given thread and return the full AI response."""
    try:
        logging.info(f"Chat request — thread={body.thread_id}, question={body.question[:60]}")

        chatbot = request.app.state.chatbot

        config = {
            "configurable": {"thread_id": body.thread_id},
            "run_name": f"chat_turn_{body.thread_id}",
            "tags": ["chatbot", body.thread_id],
            "metadata": {"thread_id": body.thread_id},
        }

        response = chatbot.invoke(
            {"messages": [HumanMessage(content=body.question)]},
            config=config,
        )

        answer = response["messages"][-1].content
        logging.info(f"Chat response generated for thread={body.thread_id}")

        return ChatResponse(answer=answer, thread_id=body.thread_id)

    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(MyException(e, sys)))


@router.post("/chat/stream")
def chat_stream(request: Request, body: ChatRequest):
    """Stream the chatbot response token by token using SSE."""
    try:
        logging.info(f"Stream request — thread={body.thread_id}, question={body.question[:60]}")

        chatbot = request.app.state.chatbot

        config = {
            "configurable": {"thread_id": body.thread_id},
            "run_name": f"chat_turn_{body.thread_id}",
            "tags": ["chatbot", body.thread_id],
            "metadata": {"thread_id": body.thread_id},
        }

        def generate():
            try:
                for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=body.question)]},
                    config=config,
                    stream_mode="messages"
                ):
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        yield f"data: {json.dumps({'type': 'tool', 'tool_name': tool_name})}\n\n"

                    elif isinstance(message_chunk, AIMessage) and message_chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': message_chunk.content})}\n\n"

                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as e:
                logging.error(f"Stream error: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        logging.error(f"Stream setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(MyException(e, sys)))


@router.post("/title")
def generate_title(request: Request, body: dict):
    """
    Generate a short conversation title from the first user message.

    Calls the LLM directly — does NOT use LangGraph so no checkpoint
    is created in SQLite. This prevents title generation from appearing
    as a fake conversation in the threads list.
    """
    try:
        message = body.get("message", "")
        if not message:
            return {"title": "New Chat"}

        logging.info(f"Title generation request — message='{message[:60]}'")

        llm = request.app.state.llm

        prompt = (
            f"Generate a very short title (max 5 words) for a conversation "
            f"that starts with: '{message}'. Return only the title, nothing else."
        )

        title = llm.invoke(prompt).content.strip()
        logging.info(f"Title generated: '{title}'")
        return {"title": title}

    except Exception as e:
        logging.error(f"Title generation error: {str(e)}")
        # Fallback — never crash title generation
        return {"title": body.get("message", "New Chat")[:40]}


@router.get("/threads", response_model=ThreadsResponse)
def get_threads(request: Request):
    """Return all known threads with their titles."""
    try:
        checkpointer_instance = request.app.state.checkpointer_instance
        title_store           = request.app.state.title_store

        checkpointer  = checkpointer_instance.get_checkpointer()
        all_threads: dict[str, str] = {}

        for checkpoint in checkpointer.list(None):
            thread_id = checkpoint.config["configurable"]["thread_id"]
            # ✅ Filter out the old title generation thread if it exists
            if thread_id == "__title_gen__":
                continue
            all_threads[thread_id] = "Previous Chat"

        saved_titles = title_store.get_all()
        for tid, title in saved_titles.items():
            if tid in all_threads:
                all_threads[tid] = title

        return ThreadsResponse(threads=all_threads)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(MyException(e, sys)))


@router.post("/threads/title", response_model=SaveTitleResponse)
def save_title(request: Request, body: TitleRequest):
    """Persist a conversation title for a thread."""
    try:
        title_store = request.app.state.title_store
        title_store.save(thread_id=body.thread_id, title=body.title)
        return SaveTitleResponse(thread_id=body.thread_id, title=body.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(MyException(e, sys)))


@router.get("/threads/{thread_id}/history")
def get_history(request: Request, thread_id: str):
    """Return the conversation history for a given thread."""
    try:
        chatbot  = request.app.state.chatbot
        state    = chatbot.get_state(config={"configurable": {"thread_id": thread_id}}).values
        messages = state.get("messages", [])

        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage) and msg.content:
                history.append({"role": "assistant", "content": msg.content})

        return {"thread_id": thread_id, "history": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(MyException(e, sys)))