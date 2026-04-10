from __future__ import annotations

import os
import uuid
import json
import requests as http_requests
import streamlit as st

# ── Backend base URL (override via env var for Docker) ──────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Multi Utility AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

# ── Avatars ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
USER_AVATAR = os.path.join(BASE_DIR, "assets", "user_avatar.png")
BOT_AVATAR  = os.path.join(BASE_DIR, "assets", "ai_avatar.png")

# ── Helper: call backend ─────────────────────────────────────────────────────

def api_get(path: str) -> dict:
    resp = http_requests.get(f"{BACKEND_URL}{path}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, json: dict | None = None, **kwargs) -> dict:
    resp = http_requests.post(f"{BACKEND_URL}{path}", json=json, timeout=60, **kwargs)
    resp.raise_for_status()
    return resp.json()


def stream_chat(question: str, thread_id: str):
    """Stream response from backend using SSE."""
    with http_requests.post(
        f"{BACKEND_URL}/api/chat/stream",
        json={
            "question": question,
            "thread_id": thread_id,
        },
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data


# ── Utility functions ─────────────────────────────────────────────────────────

def generate_thread_id() -> str:
    return str(uuid.uuid4())


def reset_chat() -> None:
    st.session_state["thread_id"]       = generate_thread_id()
    st.session_state["message_history"] = []
    st.session_state["ingested_docs"].setdefault(st.session_state["thread_id"], {})
    add_thread(st.session_state["thread_id"])


def add_thread(thread_id: str, title: str = "Current Chat") -> None:
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"][thread_id] = title


def generate_chat_title(first_message: str) -> str:
    try:
        data = api_post(
            "/api/title",                         # ← new dedicated endpoint
            json={"message": first_message},      # ← clean, no thread_id
        )
        return data.get("title", first_message[:40])
    except Exception:
        return first_message[:40]


def save_title_to_backend(thread_id: str, title: str) -> None:
    try:
        api_post("/api/threads/title", json={"thread_id": thread_id, "title": title})
    except Exception:
        pass


def load_conversation(thread_id: str) -> list[dict]:
    try:
        data = api_get(f"/api/threads/{thread_id}/history")
        return data.get("history", [])
    except Exception:
        return []


# ── Session state bootstrap ───────────────────────────────────────────────────

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    try:
        data = api_get("/api/threads")
        st.session_state["chat_threads"] = data.get("threads", {})
    except Exception:
        st.session_state["chat_threads"] = {}

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

add_thread(st.session_state["thread_id"])

thread_key  = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.title("IntelliChat")

if st.sidebar.button("Start New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

# PDF upload
st.sidebar.divider()
st.sidebar.subheader("Document")

uploaded_pdf = st.sidebar.file_uploader("Upload a PDF for this chat", type=["pdf"])

if uploaded_pdf and uploaded_pdf.name not in thread_docs:
    with st.sidebar.status("Indexing PDF...", expanded=True) as status_box:
        try:
            status_box.write("📄 Reading PDF...")
            resp = http_requests.post(
                f"{BACKEND_URL}/api/ingest",
                files={"file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")},
                data={"thread_id": thread_key},
                timeout=300,
            )
            resp.raise_for_status()
            summary = resp.json()
            thread_docs[uploaded_pdf.name] = summary
            st.session_state["last_indexed"] = uploaded_pdf.name
            status_box.update(label="✅ PDF indexed", state="complete", expanded=False)
        except http_requests.exceptions.Timeout:
            status_box.update(label="❌ Timeout — PDF too large or backend slow", state="error", expanded=False)
        except Exception as e:
            status_box.update(label=f"❌ Error: {e}", state="error", expanded=False)
    st.rerun()

if thread_docs:
    latest = list(thread_docs.values())[-1]
    st.sidebar.success(f"✅ **{latest.get('filename')}** is ready")
    st.sidebar.caption(
        f"{latest.get('num_chunks')} chunks · {latest.get('num_pages')} pages"
    )
else:
    st.sidebar.info("📄 No PDF uploaded yet.")

# Conversations
st.sidebar.divider()
st.sidebar.subheader("My Conversations")

for tid, title in reversed(st.session_state["chat_threads"].items()):
    if st.sidebar.button(title, key=tid, use_container_width=True):
        st.session_state["thread_id"] = tid
        st.session_state["message_history"] = load_conversation(tid)
        st.session_state["ingested_docs"].setdefault(str(tid), {})
        st.rerun()

# ── Main UI ───────────────────────────────────────────────────────────────────

st.title("Multi Utility AI Chatbot")
st.caption("RAG · Web Search · Stock Prices · Calculator · Persistent Memory")

for message in st.session_state["message_history"]:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

user_input = st.chat_input(
    "Ask about your document, search the web, get stock prices, or calculate..."
)

if user_input:

    is_first_message = len(st.session_state["message_history"]) == 0

    st.session_state["message_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        status_holder = {"box": None}

        def token_stream():
            """Generator that yields tokens for st.write_stream."""
            try:
                for event in stream_chat(user_input, st.session_state["thread_id"]):
                    if event["type"] == "tool":
                        tool_name = event["tool_name"]
                        if status_holder["box"] is None:
                            status_holder["box"] = st.status(
                                f"🔧 Using `{tool_name}`...", expanded=True
                            )
                        else:
                            status_holder["box"].update(
                                label=f"🔧 Using `{tool_name}`...",
                                state="running",
                                expanded=True,
                            )
                    elif event["type"] == "token":
                        yield event["content"]
                    elif event["type"] == "error":
                        yield f"❌ {event['content']}"
            except Exception as e:
                yield f"❌ Error connecting to backend: {e}"

        ai_message = st.write_stream(token_stream())

        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # generate title only for first message, AFTER streaming
    if is_first_message:
        title = generate_chat_title(user_input)
        st.session_state["chat_threads"][st.session_state["thread_id"]] = title
        save_title_to_backend(st.session_state["thread_id"], title)

    # only save to history if not an error
    if not str(ai_message).startswith("❌"):
        st.session_state["message_history"].append({"role": "assistant", "content": ai_message})