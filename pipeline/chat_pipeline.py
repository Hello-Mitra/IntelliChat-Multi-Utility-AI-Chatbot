from __future__ import annotations

import sys
import os
from src.logger import logging
from src.exception import MyException
from src.graph.state import ChatState
from src.graph.nodes import build_chat_node
from src.tools import ALL_TOOLS
from src.embeddings.embedding_model import EmbeddingModel
from src.vector_store.faiss_store import VectorStore
from src.utils.thread_store import set_retriever
from entity.config_entity import (
    LLMConfig,
    EmbeddingConfig,
    VectorStoreConfig,
    RetrieverConfig,
    CheckpointerConfig,
)
from src.checkpointer.sqlite_checkpointer import SQLiteCheckpointer
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition


class ChatPipeline:
    """
    Builds and returns the compiled LangGraph chatbot.
    Also loads any saved FAISS indexes from disk on startup.
    """

    def __init__(self):
        self.llm_config          = LLMConfig()
        self.embedding_config    = EmbeddingConfig()
        self.vector_store_config = VectorStoreConfig()
        self.retriever_config    = RetrieverConfig()
        self.checkpointer_config = CheckpointerConfig()

    def _load_saved_indexes(self, embedding_model) -> None:
        """Load all persisted FAISS indexes into thread_store on startup."""
        faiss_dir = self.vector_store_config.faiss_index_dir
        if not os.path.isdir(faiss_dir):
            return
        for item in os.listdir(faiss_dir):
            if item.startswith("faiss_index_") and os.path.isdir(os.path.join(faiss_dir, item)):
                thread_id = item.replace("faiss_index_", "")
                try:
                    vs = VectorStore.load_local(
                        os.path.join(faiss_dir, item),
                        embedding_model,
                    )
                    retriever = vs.as_retriever(
                        search_type=self.retriever_config.search_type,
                        search_kwargs={"k": self.retriever_config.top_k},
                    )
                    set_retriever(thread_id, retriever)
                    logging.info(f"Loaded FAISS index for thread {thread_id}")
                except Exception:
                    logging.warning(f"Could not load FAISS index for thread {thread_id} — skipping")

    def build(self):
        """Build the compiled LangGraph chatbot and return (chatbot, checkpointer_instance)."""
        try:
            logging.info("Building ChatPipeline")

            # LLM
            llm = ChatOpenAI(
                model=self.llm_config.model_name,
                temperature=self.llm_config.temperature,
            )
            llm_with_tools = llm.bind_tools(ALL_TOOLS)

            # Load saved FAISS indexes
            embedding_model = EmbeddingModel(config=self.embedding_config)
            self._load_saved_indexes(embedding_model.model)

            # Checkpointer
            checkpointer_instance = SQLiteCheckpointer(config=self.checkpointer_config)
            checkpointer = checkpointer_instance.get_checkpointer()

            # Graph
            chat_node = build_chat_node(llm_with_tools)
            tool_node = ToolNode(tools=ALL_TOOLS)

            graph = StateGraph(ChatState)
            graph.add_node("chat_node", chat_node)
            graph.add_node("tools", tool_node)
            graph.add_edge(START, "chat_node")
            graph.add_conditional_edges("chat_node", tools_condition)
            graph.add_edge("tools", "chat_node")
            graph.add_edge("chat_node", END)

            chatbot = graph.compile(checkpointer=checkpointer)

            logging.info("ChatPipeline built successfully")
            return chatbot, checkpointer_instance

        except Exception as e:
            raise MyException(e, sys)
