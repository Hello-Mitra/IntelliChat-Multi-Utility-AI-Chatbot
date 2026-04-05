from __future__ import annotations

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """LangGraph state — messages accumulate via the add_messages reducer."""
    messages: Annotated[list[BaseMessage], add_messages]
