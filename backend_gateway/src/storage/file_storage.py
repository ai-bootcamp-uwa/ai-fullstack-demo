import json
import os
import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .base import ChatStorage
from ..models.chat import ChatHistory, ChatSession, ChatMessage

class FileBasedChatStorage(ChatStorage):
    """File-based storage implementation for chat data."""
    
    def __init__(self, base_path: str = "data/chats"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_chat_file(self, user_id: str, chat_id: str) -> Path:
        """Get the file path for a specific chat."""
        user_dir = self.base_path / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir / f"{chat_id}.json"
    
    async def create_chat(self, user_id: str, chat: ChatSession) -> ChatSession:
        """Create a new chat session and save to file."""
        chat_file = self._get_chat_file(user_id, chat.chat_id)
        history = ChatHistory(session=chat, messages=[])
        
        # Write to file asynchronously
        await asyncio.to_thread(self._write_json, chat_file, history.dict())
        return chat
    
    async def get_chat(self, user_id: str, chat_id: str) -> Optional[ChatHistory]:
        """Get complete chat history from file."""
        chat_file = self._get_chat_file(user_id, chat_id)
        if not chat_file.exists():
            return None
            
        data = await asyncio.to_thread(self._read_json, chat_file)
        return ChatHistory(**data) if data else None
    
    async def list_chats(self, user_id: str) -> List[ChatSession]:
        """List all chat sessions for a user."""
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return []
        
        chats = []
        for chat_file in user_dir.glob("*.json"):
            data = await asyncio.to_thread(self._read_json, chat_file)
            if data and "session" in data:
                chats.append(ChatSession(**data["session"]))
        
        # Sort by updated_at descending (most recent first)
        return sorted(chats, key=lambda x: x.updated_at, reverse=True)
    
    async def add_message(self, user_id: str, chat_id: str, message: ChatMessage) -> None:
        """Add a message to an existing chat."""
        history = await self.get_chat(user_id, chat_id)
        if not history:
            raise ValueError(f"Chat {chat_id} not found for user {user_id}")
        
        # Add the message and update session metadata
        history.messages.append(message)
        history.session.message_count += 1
        history.session.updated_at = datetime.utcnow()
        
        # Save back to file
        chat_file = self._get_chat_file(user_id, chat_id)
        await asyncio.to_thread(self._write_json, chat_file, history.dict())
    
    async def delete_chat(self, user_id: str, chat_id: str) -> None:
        """Delete a chat session file."""
        chat_file = self._get_chat_file(user_id, chat_id)
        if chat_file.exists():
            await asyncio.to_thread(os.remove, chat_file)
    
    def _read_json(self, file_path: Path) -> Optional[dict]:
        """Read JSON data from file safely."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception):
            return None
    
    def _write_json(self, file_path: Path, data: dict) -> None:
        """Write JSON data to file safely."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False) 