from typing import List, Optional
from datetime import datetime

from ..models.chat import ChatSession, ChatMessage, ChatHistory
from ..storage.file_storage import FileBasedChatStorage

class ChatService:
    """Service for managing chat sessions and messages."""
    
    def __init__(self):
        self.storage = FileBasedChatStorage()
    
    async def create_chat(self, user_id: str, title: str, first_message: str = None) -> ChatSession:
        """Create a new chat session."""
        # Create the chat session
        chat = ChatSession(user_id=user_id, title=title)
        await self.storage.create_chat(user_id, chat)
        
        # Add first message if provided
        if first_message:
            message = ChatMessage(role="user", content=first_message)
            await self.storage.add_message(user_id, chat.chat_id, message)
        
        return chat
    
    async def get_chat_history(self, user_id: str, chat_id: str) -> Optional[ChatHistory]:
        """Get complete chat history for a specific chat."""
        return await self.storage.get_chat(user_id, chat_id)
    
    async def list_user_chats(self, user_id: str) -> List[ChatSession]:
        """Get list of all chat sessions for a user."""
        return await self.storage.list_chats(user_id)
    
    async def add_message(self, user_id: str, chat_id: str, message: ChatMessage) -> None:
        """Add a message to an existing chat."""
        await self.storage.add_message(user_id, chat_id, message)
    
    async def delete_chat(self, user_id: str, chat_id: str) -> None:
        """Delete a chat session and all its messages."""
        await self.storage.delete_chat(user_id, chat_id)
    
    def build_context(self, messages: List[ChatMessage], max_messages: int = 5) -> str:
        """Build context string from recent chat messages."""
        if not messages:
            return ""
        
        # Get last N messages (excluding the most recent user message if it exists)
        # We want context from previous conversation, not including current question
        context_messages = messages[-(max_messages+1):-1] if len(messages) > 1 else []
        
        if not context_messages:
            return ""
        
        # Build context string
        context_parts = ["Previous conversation:"]
        for msg in context_messages:
            role = "User" if msg.role == "user" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts) + "\n\n"
    
    async def get_context_for_query(self, user_id: str, chat_id: str, max_messages: int = 5) -> tuple[str, int]:
        """Get formatted context for a chat query.
        
        Returns:
            tuple: (context_string, number_of_messages_included)
        """
        history = await self.get_chat_history(user_id, chat_id)
        if not history or not history.messages:
            return "", 0
        
        context = self.build_context(history.messages, max_messages)
        messages_used = min(len(history.messages), max_messages) if context else 0
        
        return context, messages_used

# Global service instance
chat_service = ChatService() 