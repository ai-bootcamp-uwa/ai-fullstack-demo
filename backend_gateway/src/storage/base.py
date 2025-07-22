from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.chat import ChatHistory, ChatSession, ChatMessage

class ChatStorage(ABC):
    """Abstract base class for chat storage implementations."""
    
    @abstractmethod
    async def create_chat(self, user_id: str, chat: ChatSession) -> ChatSession:
        """Create a new chat session."""
        pass
    
    @abstractmethod 
    async def get_chat(self, user_id: str, chat_id: str) -> Optional[ChatHistory]:
        """Get complete chat history by chat ID."""
        pass
    
    @abstractmethod
    async def list_chats(self, user_id: str) -> List[ChatSession]:
        """List all chat sessions for a user."""
        pass
    
    @abstractmethod
    async def add_message(self, user_id: str, chat_id: str, message: ChatMessage) -> None:
        """Add a message to an existing chat."""
        pass
    
    @abstractmethod
    async def delete_chat(self, user_id: str, chat_id: str) -> None:
        """Delete a chat session and all its messages."""
        pass 