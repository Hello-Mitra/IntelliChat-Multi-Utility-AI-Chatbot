from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.2
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 4
    search_type: str = "similarity"
    faiss_index_dir: str = "artifacts/faiss_indexes"
    db_path: str = "artifacts/chatbot.db"
    langchain_tracing_v2: str = "false"
    langchain_api_key: str = ""
    langchain_project: str = "MultiUtilityChatbot"
    alphavantage_stock_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ✅ this is the fix


settings = Settings()