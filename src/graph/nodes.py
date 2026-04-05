from __future__ import annotations

import sys
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from src.logger import logging
from src.exception import MyException
from src.prompts.templates import SYSTEM_PROMPT
from src.graph.state import ChatState


def build_chat_node(llm_with_tools):
    """
    Factory that returns a chat_node function bound to the given llm_with_tools instance.
    This keeps the node stateless and testable.
    """

    def chat_node(state: ChatState, config: RunnableConfig) -> ChatState:
        """LLM node — answers directly or delegates to a tool."""
        try:
            logging.info("Entered chat_node")

            thread_id = config.get("configurable", {}).get("thread_id") if config else None

            system_message = SystemMessage(
                content=SYSTEM_PROMPT.format(thread_id=thread_id)
            )

            messages = [system_message, *state["messages"]]
            response = llm_with_tools.invoke(messages)

            logging.info("Exited chat_node successfully")
            return {"messages": [response]}

        except Exception as e:
            raise MyException(e, sys)

    return chat_node
