from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class ChatSession(BaseModel):
    """Chat session model - represents a conversation"""
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0

class ChatMessage(BaseModel):
    """Individual chat message model"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(BaseModel):
    """Complete chat history including session and all messages"""
    session: ChatSession
    messages: List[ChatMessage] = [] 