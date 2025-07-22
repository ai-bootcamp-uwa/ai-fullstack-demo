# Chat History - Simplified Implementation Guide

## 🎯 Overview

This document provides a **simplified, practical approach** to implementing basic chat history functionality in the Backend Gateway (Module 3). This focuses on the **MVP (Minimum Viable Product)** features that can be implemented quickly and effectively.

## 🏃‍♂️ Quick Start Approach

### Core Features (MVP)

1. **Multiple Chat Sessions** - Users can create and switch between different conversations
2. **Message Persistence** - Store all messages for each chat session
3. **Basic Context** - Include recent messages when querying AI
4. **Simple Management** - Create, list, view, and delete chats
5. **File Storage** - JSON-based storage (no database needed initially)

### What We're NOT Building (Initially)

-   Complex context algorithms
-   Advanced search functionality
-   Export features
-   Analytics and insights
-   Database integration
-   Real-time collaboration

## 📁 Directory Structure Changes

### Current Structure

```
backend_gateway/
├── src/
│   ├── api/main.py
│   ├── core/{auth.py, config.py}
│   ├── models/{requests.py, responses.py}
│   ├── services/{data_client.py, cortex_client.py}
│   └── tests/
└── main.py
```

### New Structure (After Implementation)

```
backend_gateway/
├── src/
│   ├── api/main.py                    # Updated with new endpoints
│   ├── core/
│   │   ├── auth.py
│   │   └── config.py                  # Add chat storage settings
│   ├── models/
│   │   ├── requests.py                # Add chat request models
│   │   ├── responses.py               # Add chat response models
│   │   └── chat.py                    # NEW: Chat data models
│   ├── services/
│   │   ├── data_client.py
│   │   ├── cortex_client.py
│   │   └── chat_service.py            # NEW: Chat management service
│   ├── storage/                       # NEW: Storage layer
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract storage interface
│   │   └── file_storage.py           # File-based storage implementation
│   └── tests/
│       ├── test_api.py                # Updated with chat tests
│       ├── test_chat_service.py       # NEW: Chat service tests
│       └── test_startup.py
├── data/                              # NEW: Data directory
│   └── chats/                         # Chat storage files
│       └── {user_id}/
│           └── {chat_id}.json
└── main.py
```

## 📊 Simplified Data Models

### Chat Session (Simple)

```python
# src/models/chat.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class ChatSession(BaseModel):
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0

class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(BaseModel):
    session: ChatSession
    messages: List[ChatMessage] = []
```

### Request/Response Models

```python
# src/models/requests.py - ADD these models

class CreateChatRequest(BaseModel):
    title: str
    first_message: Optional[str] = None

class ChatMessageRequest(BaseModel):
    chat_id: str
    message: str
    include_context: bool = True  # Simple on/off for context
```

```python
# src/models/responses.py - ADD these models

class ChatSessionResponse(BaseModel):
    chat_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class ChatListResponse(BaseModel):
    chats: List[ChatSessionResponse]
    total: int

class ChatDetailResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessage]

class EnhancedChatResponse(BaseModel):
    message_id: str
    response: str
    chat_id: str
    timestamp: datetime
    context_messages_used: int  # How many previous messages included
```

## 🔧 Simple Storage Implementation

### File-Based Storage Service

```python
# src/storage/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.chat import ChatHistory, ChatSession

class ChatStorage(ABC):
    @abstractmethod
    async def create_chat(self, user_id: str, chat: ChatSession) -> ChatSession: pass

    @abstractmethod
    async def get_chat(self, user_id: str, chat_id: str) -> Optional[ChatHistory]: pass

    @abstractmethod
    async def list_chats(self, user_id: str) -> List[ChatSession]: pass

    @abstractmethod
    async def add_message(self, user_id: str, chat_id: str, message: ChatMessage): pass

    @abstractmethod
    async def delete_chat(self, user_id: str, chat_id: str): pass
```

```python
# src/storage/file_storage.py
import json
import os
import asyncio
from pathlib import Path
from typing import List, Optional
from .base import ChatStorage
from ..models.chat import ChatHistory, ChatSession, ChatMessage

class FileBasedChatStorage(ChatStorage):
    def __init__(self, base_path: str = "data/chats"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_chat_file(self, user_id: str, chat_id: str) -> Path:
        user_dir = self.base_path / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir / f"{chat_id}.json"

    async def create_chat(self, user_id: str, chat: ChatSession) -> ChatSession:
        chat_file = self._get_chat_file(user_id, chat.chat_id)
        history = ChatHistory(session=chat, messages=[])

        # Write to file
        await asyncio.to_thread(self._write_json, chat_file, history.dict())
        return chat

    async def get_chat(self, user_id: str, chat_id: str) -> Optional[ChatHistory]:
        chat_file = self._get_chat_file(user_id, chat_id)
        if not chat_file.exists():
            return None

        data = await asyncio.to_thread(self._read_json, chat_file)
        return ChatHistory(**data) if data else None

    async def list_chats(self, user_id: str) -> List[ChatSession]:
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return []

        chats = []
        for chat_file in user_dir.glob("*.json"):
            data = await asyncio.to_thread(self._read_json, chat_file)
            if data:
                chats.append(ChatSession(**data["session"]))

        return sorted(chats, key=lambda x: x.updated_at, reverse=True)

    async def add_message(self, user_id: str, chat_id: str, message: ChatMessage):
        history = await self.get_chat(user_id, chat_id)
        if not history:
            raise ValueError(f"Chat {chat_id} not found")

        history.messages.append(message)
        history.session.message_count += 1
        history.session.updated_at = datetime.utcnow()

        chat_file = self._get_chat_file(user_id, chat_id)
        await asyncio.to_thread(self._write_json, chat_file, history.dict())

    async def delete_chat(self, user_id: str, chat_id: str):
        chat_file = self._get_chat_file(user_id, chat_id)
        if chat_file.exists():
            await asyncio.to_thread(os.remove, chat_file)

    def _read_json(self, file_path: Path) -> dict:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return None

    def _write_json(self, file_path: Path, data: dict):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
```

## 🎯 Chat Service Implementation

### Simple Chat Management Service

```python
# src/services/chat_service.py
from typing import List, Optional
from ..models.chat import ChatSession, ChatMessage, ChatHistory
from ..storage.file_storage import FileBasedChatStorage
from datetime import datetime

class ChatService:
    def __init__(self):
        self.storage = FileBasedChatStorage()

    async def create_chat(self, user_id: str, title: str, first_message: str = None) -> ChatSession:
        """Create a new chat session"""
        chat = ChatSession(user_id=user_id, title=title)
        await self.storage.create_chat(user_id, chat)

        # Add first message if provided
        if first_message:
            message = ChatMessage(role="user", content=first_message)
            await self.storage.add_message(user_id, chat.chat_id, message)

        return chat

    async def get_chat_history(self, user_id: str, chat_id: str) -> Optional[ChatHistory]:
        """Get complete chat history"""
        return await self.storage.get_chat(user_id, chat_id)

    async def list_user_chats(self, user_id: str) -> List[ChatSession]:
        """Get list of user's chats"""
        return await self.storage.list_chats(user_id)

    async def add_message(self, user_id: str, chat_id: str, message: ChatMessage):
        """Add message to chat"""
        await self.storage.add_message(user_id, chat_id, message)

    async def delete_chat(self, user_id: str, chat_id: str):
        """Delete a chat session"""
        await self.storage.delete_chat(user_id, chat_id)

    def build_context(self, messages: List[ChatMessage], max_messages: int = 5) -> str:
        """Build simple context from recent messages"""
        if not messages:
            return ""

        # Get last N messages (excluding the most recent user message)
        context_messages = messages[-(max_messages+1):-1] if len(messages) > 1 else []

        if not context_messages:
            return ""

        context_parts = ["Previous conversation:"]
        for msg in context_messages:
            role = "User" if msg.role == "user" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")

        return "\n".join(context_parts) + "\n\n"

# Global service instance
chat_service = ChatService()
```

## 🚀 API Endpoints (Simplified)

### Add to src/api/main.py

```python
# Add these imports at the top
from ..services.chat_service import chat_service
from ..models.chat import ChatMessage
from ..models import CreateChatRequest, ChatMessageRequest, ChatListResponse, ChatDetailResponse, EnhancedChatResponse

# Add these new endpoints

@app.post("/api/backend/chats", response_model=ChatSessionResponse)
async def create_chat(request: CreateChatRequest, current_user: dict = Depends(get_current_user)):
    """Create a new chat session"""
    try:
        chat = await chat_service.create_chat(
            user_id=current_user["username"],
            title=request.title,
            first_message=request.first_message
        )
        return ChatSessionResponse(
            chat_id=chat.chat_id,
            title=chat.title,
            message_count=chat.message_count,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backend/chats", response_model=ChatListResponse)
async def list_chats(current_user: dict = Depends(get_current_user)):
    """List user's chat sessions"""
    try:
        chats = await chat_service.list_user_chats(current_user["username"])
        chat_responses = [
            ChatSessionResponse(
                chat_id=chat.chat_id,
                title=chat.title,
                message_count=chat.message_count,
                created_at=chat.created_at,
                updated_at=chat.updated_at
            )
            for chat in chats
        ]
        return ChatListResponse(chats=chat_responses, total=len(chat_responses))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backend/chats/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    """Get chat details with message history"""
    try:
        history = await chat_service.get_chat_history(current_user["username"], chat_id)
        if not history:
            raise HTTPException(status_code=404, detail="Chat not found")

        return ChatDetailResponse(
            session=ChatSessionResponse(
                chat_id=history.session.chat_id,
                title=history.session.title,
                message_count=history.session.message_count,
                created_at=history.session.created_at,
                updated_at=history.session.updated_at
            ),
            messages=history.messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/backend/chats/{chat_id}")
async def delete_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a chat session"""
    try:
        await chat_service.delete_chat(current_user["username"], chat_id)
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update existing chat endpoint to support chat history
@app.post("/api/backend/chat", response_model=EnhancedChatResponse)
async def chat(request: ChatMessageRequest, current_user: dict = Depends(get_current_user)):
    """Enhanced chat with history support"""
    try:
        user_id = current_user["username"]

        # Get chat history for context
        history = await chat_service.get_chat_history(user_id, request.chat_id)
        if not history:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Add user message to history
        user_message = ChatMessage(role="user", content=request.message)
        await chat_service.add_message(user_id, request.chat_id, user_message)

        # Build context if requested
        query = request.message
        context_count = 0
        if request.include_context and history.messages:
            context = chat_service.build_context(history.messages)
            if context:
                query = context + f"Current question: {request.message}"
                context_count = min(len(history.messages), 5)

        # Get AI response
        ai_response = await cortex_client.rag_query(query)
        response_text = ai_response.get("result", "No response available")

        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response_text)
        await chat_service.add_message(user_id, request.chat_id, assistant_message)

        return EnhancedChatResponse(
            message_id=assistant_message.message_id,
            response=response_text,
            chat_id=request.chat_id,
            timestamp=assistant_message.timestamp,
            context_messages_used=context_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
```

## 📋 Implementation Workflow

### Phase 1: Setup (Day 1-2)

1. **Create directory structure**

    ```bash
    mkdir -p backend_gateway/src/storage
    mkdir -p backend_gateway/src/models  # if not exists
    mkdir -p backend_gateway/data/chats
    ```

2. **Implement data models**

    - Create `src/models/chat.py`
    - Update `src/models/requests.py` and `src/models/responses.py`
    - Update `src/models/__init__.py` imports

3. **Create storage layer**
    - Implement `src/storage/base.py`
    - Implement `src/storage/file_storage.py`
    - Create `src/storage/__init__.py`

### Phase 2: Core Service (Day 3-4)

1. **Implement chat service**

    - Create `src/services/chat_service.py`
    - Update `src/services/__init__.py`

2. **Basic testing**
    - Test file storage operations
    - Test chat service CRUD operations
    - Verify data persistence

### Phase 3: API Integration (Day 5-6)

1. **Add API endpoints**

    - Update `src/api/main.py` with new endpoints
    - Update imports and dependencies

2. **Enhanced chat endpoint**
    - Modify existing chat endpoint to support chat_id
    - Add context building logic

### Phase 4: Testing & Polish (Day 7)

1. **Comprehensive testing**

    - Test all endpoints with Postman/curl
    - Test user isolation
    - Test error handling

2. **Documentation update**
    - Update main README.md
    - Add API examples

## 🧪 Testing Commands

### Basic API Testing

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST "http://localhost:3003/api/backend/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')

# 2. Create a new chat
CHAT_ID=$(curl -s -X POST "http://localhost:3003/api/backend/chats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Copper Mining Research", "first_message": "Tell me about copper mining in Australia"}' \
  | jq -r '.chat_id')

# 3. List all chats
curl -X GET "http://localhost:3003/api/backend/chats" \
  -H "Authorization: Bearer $TOKEN"

# 4. Send message to chat (with context)
curl -X POST "http://localhost:3003/api/backend/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"$CHAT_ID\", \"message\": \"What about nickel mining?\", \"include_context\": true}"

# 5. Get chat history
curl -X GET "http://localhost:3003/api/backend/chats/$CHAT_ID" \
  -H "Authorization: Bearer $TOKEN"

# 6. Delete chat
curl -X DELETE "http://localhost:3003/api/backend/chats/$CHAT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Configuration Updates

### Add to src/core/config.py

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Chat settings
    chat_storage_path: str = "data/chats"
    max_context_messages: int = 5
    max_chat_title_length: int = 100
```

## 🔒 Simple Security

### User Isolation

-   All chat operations include user_id from JWT token
-   File storage organized by user_id directories
-   No cross-user access possible

### Basic Validation

-   Chat titles limited to 100 characters
-   Message content validation
-   Chat_id format validation (UUID)

## 📈 Monitoring & Maintenance

### Simple Logging

```python
# Add to chat_service.py
import logging

logger = logging.getLogger(__name__)

# Add logging to key operations
logger.info(f"Created chat {chat.chat_id} for user {user_id}")
logger.info(f"Added message to chat {chat_id}")
```

### Storage Cleanup

```python
# Future: Add cleanup script for old chats
def cleanup_old_chats(days_old: int = 90):
    # Remove chats older than X days
    pass
```

## 🎯 Success Criteria

### MVP Complete When:

-   [ ] Users can create multiple chat sessions
-   [ ] Messages persist between API calls
-   [ ] Chat endpoint includes context from previous messages
-   [ ] Users can list and view their chat history
-   [ ] Users can delete old chats
-   [ ] File storage works reliably
-   [ ] All endpoints have proper authentication
-   [ ] Basic error handling works

### Performance Goals:

-   Chat creation: < 100ms
-   Message addition: < 50ms
-   History retrieval: < 200ms
-   Context building: < 50ms

## 🚀 Next Steps (Future Enhancements)

Once MVP is working:

1. **Database Migration**: Move from files to SQLite/PostgreSQL
2. **Advanced Context**: Implement semantic similarity for context selection
3. **Search**: Add basic text search across chat history
4. **Export**: Add JSON export functionality
5. **UI Integration**: Build frontend chat management interface

---

This simplified implementation provides a solid foundation for chat history while remaining practical and achievable. The focus is on getting core functionality working quickly, then building upon it iteratively.
