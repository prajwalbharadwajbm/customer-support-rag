from pydantic import BaseModel
from typing import List, Literal

class ChatMessage(BaseModel):
    """
    Represents a single chat message.
    Like: {"content": "Hello!", "role": "user"}
    """
    content: str
    role: Literal["user", "assistant", "system"]

class ChatInput(BaseModel):
    """
    Represents the full chat conversation being sent to us.
    Contains a list of messages.
    """
    messages: List[ChatMessage]