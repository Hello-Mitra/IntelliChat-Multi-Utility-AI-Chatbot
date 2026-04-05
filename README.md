# IntelliChat — Multi Utility AI Chatbot

> A production-grade AI chatbot with RAG, web search, stock prices, calculator, persistent memory, and multi-thread conversation management — built with LangGraph, FastAPI, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-1.1.3-green?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-FF4B4B?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2%20%2B%20ECR-FF9900?style=flat-square&logo=amazonaws)

---

## Features

- **RAG (Retrieval Augmented Generation)** — Upload a PDF and ask questions about it. Per-thread FAISS vector store with disk persistence across restarts.
- **Web Search** — Real-time web search via DuckDuckGo for current information.
- **Stock Price Lookup** — Fetch live stock prices using Alpha Vantage API.
- **Calculator** — Arithmetic operations (add, subtract, multiply, divide).
- **Persistent Memory** — Conversations stored in SQLite via LangGraph checkpointing. History survives app restarts.
- **Multi-thread Conversations** — Isolated conversation threads, each with auto-generated titles. Switch between conversations from the sidebar.
- **Streaming Responses** — Token-by-token streaming via Server-Sent Events (SSE).
- **Tool Status Indicator** — Visual indicator when tools are being used.
- **LangSmith Observability** — Full tracing of every LangGraph run.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│         (PDF upload, chat UI, conversation sidebar)      │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / SSE
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                       │
│         /api/chat/stream  /api/ingest  /api/threads      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  LangGraph Pipeline                      │
│                                                          │
│   chat_node ──► tools_condition ──► tool_node            │
│       ▲                                  │               │
│       └──────────────────────────────────┘               │
│                                                          │
│   Tools: DuckDuckGo · Calculator · Stock · RAG           │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼───────┐         ┌────────▼────────┐
│  SQLite DB    │         │  FAISS Index    │
│ (LangGraph    │         │ (per-thread PDF  │
│  checkpoints  │         │  vector store)  │
│  + titles)    │         │                 │
└───────────────┘         └─────────────────┘
```

---

## Project Structure

```
IntelliChat-Multi-Utility-AI-Chatbot/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point with lifespan
│   └── routes/
│       ├── chat.py             # Chat, streaming, threads endpoints
│       └── ingest.py           # PDF upload endpoint
│
├── frontend/                   # Streamlit UI
│   ├── app.py
│   └── assets/                 # Avatars
│
├── pipeline/                   # Orchestration layer
│   ├── chat_pipeline.py        # Builds LangGraph chatbot
│   └── ingest_pipeline.py      # PDF → chunks → FAISS → retriever
│
├── src/                        # Core components
│   ├── graph/                  # LangGraph state and nodes
│   ├── tools/                  # calculator, search, stock, rag
│   ├── ingestion/              # PDF loader
│   ├── text_splitter/          # RecursiveCharacterTextSplitter
│   ├── embeddings/             # OpenAI embeddings
│   ├── vector_store/           # FAISS store
│   ├── retriever/              # Retriever
│   ├── checkpointer/           # SQLite checkpointer
│   ├── db/                     # Title store
│   ├── utils/                  # Thread store (in-memory retrievers)
│   ├── schemas/                # Pydantic request/response models
│   ├── prompts/                # System prompt templates
│   ├── logger/                 # Rotating file + console logger
│   └── exception/              # Custom exception with traceback
│
├── config/
│   └── settings.py             # Pydantic settings (all config in one place)
│
├── entity/
│   ├── config_entity.py        # Dataclass configs
│   └── artifact_entity.py      # Dataclass artifacts
│
├── artifacts/                  # Generated at runtime (gitignored)
│   └── faiss_indexes/          # Per-thread FAISS indexes
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── .github/workflows/cicd.yml  # CI/CD → AWS ECR → EC2
├── requirements.backend.txt
├── requirements.frontend.txt
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | GPT-4o-mini (OpenAI) |
| Embeddings | text-embedding-3-small (OpenAI) |
| Orchestration | LangGraph |
| Vector Store | FAISS |
| Persistence | SQLite (LangGraph SqliteSaver) |
| Web Search | DuckDuckGo |
| Stock Data | Alpha Vantage API |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Observability | LangSmith |
| Containerization | Docker + Docker Compose |
| Registry | AWS ECR |
| Deployment | AWS EC2 |
| CI/CD | GitHub Actions |

---

## Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key
- Alpha Vantage API key (free at alphavantage.co)
- LangSmith API key (optional, for observability)

### Local Setup

**1. Clone the repository:**
```bash
git clone https://github.com/Hello-Mitra/IntelliChat-Multi-Utility-AI-Chatbot.git
cd IntelliChat-Multi-Utility-AI-Chatbot
```

**2. Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

**3. Install dependencies:**
```bash
pip install -r requirements.backend.txt
pip install -r requirements.frontend.txt
```

**4. Create `.env` file:**
```bash
cp .env.example .env
# Fill in your API keys
```

**5. Run the backend:**
```bash
uvicorn backend.main:app --port 8000 --reload
```

**6. Run the frontend (new terminal):**
```bash
streamlit run frontend/app.py
```

**7. Open in browser:**
```
http://localhost:8501
```

### Docker Setup

```bash
# Build and run both services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
OPENAI_API_KEY=your_openai_api_key
ALPHAVANTAGE_STOCK_API_KEY=your_alphavantage_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=IntelliChat
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Full response chat |
| `POST` | `/api/chat/stream` | Streaming chat via SSE |
| `POST` | `/api/ingest` | Upload and index a PDF |
| `GET` | `/api/threads` | Get all conversation threads |
| `GET` | `/api/threads/{id}/history` | Get conversation history |
| `POST` | `/api/threads/title` | Save conversation title |
| `GET` | `/health` | Health check |

Full interactive API docs available at `http://localhost:8000/docs`

---

## CI/CD Pipeline

```
git push origin main
        │
        ▼
Continuous-Integration (GitHub hosted runner)
        │
        ├── Lint with Ruff
        ├── Build backend Docker image
        ├── Push to AWS ECR
        ├── Build frontend Docker image
        └── Push to AWS ECR
        │
        ▼
Continuous-Deployment (EC2 self-hosted runner)
        │
        ├── Pull latest images from ECR
        ├── docker-compose down
        └── docker-compose up -d
```

---

## How RAG Works

```
1. User uploads PDF
        ↓
2. PyMuPDF loads document
        ↓
3. RecursiveCharacterTextSplitter chunks text
   (chunk_size=1000, overlap=200)
        ↓
4. OpenAI text-embedding-3-small creates vectors
        ↓
5. FAISS stores vectors (saved to disk per thread)
        ↓
6. User asks question about PDF
        ↓
7. LLM calls rag_tool with query + thread_id
        ↓
8. FAISS retrieves top-4 similar chunks
        ↓
9. LLM generates answer from retrieved context
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Arijit Mitra**

[![GitHub](https://img.shields.io/badge/GitHub-Hello--Mitra-181717?style=flat-square&logo=github)](https://github.com/Hello-Mitra)