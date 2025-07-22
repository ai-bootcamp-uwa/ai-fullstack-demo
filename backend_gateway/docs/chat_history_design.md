# Chat History Design for Backend Gateway (Module 3)

## 🎯 Overview

This document outlines the design for adding comprehensive chat history functionality to the Backend Gateway API (Module 3). The system will enable users to maintain multiple contextual conversations with persistent history, allowing for more intelligent and contextual AI interactions.

## 📋 Requirements

### Functional Requirements

-   **Multiple Chat Sessions**: Users can create and manage multiple independent chat conversations
-   **Persistent History**: All chat messages are stored and retrievable
-   **Contextual Queries**: New queries include relevant previous conversation context
-   **User Isolation**: Users can only access their own chat sessions
-   **Chat Management**: Create, list, view, update, and delete chat sessions
-   **Context Optimization**: Intelligent context window management for AI queries

### Non-Functional Requirements

-   **Performance**: Fast retrieval of chat history (< 200ms)
-   **Scalability**: Support for hundreds of chats per user
-   **Security**: Proper authorization and data isolation
-   **Storage Efficiency**: Optimized storage for conversation data
-   **Integration**: Seamless integration with existing Module 2 (Cortex Engine) AI capabilities

## 🏗️ Architecture Overview

### System Components

```
Frontend Application
       ↓
Backend Gateway (Module 3) - Chat History Layer
       ↓                              ↓
Chat Storage System              Context Manager
       ↓                              ↓
Cortex Engine (Module 2) ← Context-Enhanced Queries
       ↓
Data Foundation (Module 1)
```

### Core Components

1. **Chat Session Manager**: Handles chat lifecycle operations
2. **Message Storage**: Persistent storage for chat messages
3. **Context Builder**: Constructs context from chat history
4. **History Retrieval**: Efficient chat history queries
5. **Authorization Layer**: Ensures user data isolation

## 📊 Data Models

### Chat Session Model

```yaml
ChatSession:
    chat_id: string (UUID)
    user_id: string
    title: string
    description: string (optional)
    created_at: datetime
    updated_at: datetime
    message_count: integer
    last_activity: datetime
    metadata:
        tags: array[string] (optional)
        category: string (optional)
        favorite: boolean
    is_active: boolean
```

### Chat Message Model

```yaml
ChatMessage:
    message_id: string (UUID)
    chat_id: string (foreign key)
    role: enum[user, assistant, system]
    content: string
    timestamp: datetime
    metadata:
        token_count: integer (optional)
        processing_time: float (optional)
        ai_model_used: string (optional)
        confidence_score: float (optional)
    parent_message_id: string (optional, for threading)
    is_deleted: boolean
```

### Context Metadata Model

```yaml
ContextMetadata:
    total_messages: integer
    context_window_used: integer
    tokens_in_context: integer
    oldest_message_included: datetime
    context_summary: string (optional)
```

## 🚀 API Design

### Chat Management Endpoints

#### Create New Chat

```http
POST /api/backend/chats
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "title": "Copper Mining Discussion",
  "description": "Exploring copper deposits in WA",
  "tags": ["copper", "mining", "western-australia"]
}

Response:
{
  "chat_id": "uuid-1234",
  "title": "Copper Mining Discussion",
  "description": "Exploring copper deposits in WA",
  "created_at": "2024-01-15T10:30:00Z",
  "message_count": 0,
  "tags": ["copper", "mining", "western-australia"]
}
```

#### List User's Chats

```http
GET /api/backend/chats?limit=20&offset=0&sort=last_activity&order=desc
Authorization: Bearer {token}

Response:
{
  "chats": [
    {
      "chat_id": "uuid-1234",
      "title": "Copper Mining Discussion",
      "message_count": 15,
      "last_activity": "2024-01-15T14:22:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "tags": ["copper", "mining"]
    }
  ],
  "total": 5,
  "has_more": false
}
```

#### Get Chat Details with History

```http
GET /api/backend/chats/{chat_id}?include_messages=true&limit=50
Authorization: Bearer {token}

Response:
{
  "chat": {
    "chat_id": "uuid-1234",
    "title": "Copper Mining Discussion",
    "description": "Exploring copper deposits in WA",
    "created_at": "2024-01-15T10:30:00Z",
    "message_count": 15,
    "tags": ["copper", "mining"]
  },
  "messages": [
    {
      "message_id": "msg-001",
      "role": "user",
      "content": "Tell me about copper mining in Western Australia",
      "timestamp": "2024-01-15T10:31:00Z"
    },
    {
      "message_id": "msg-002",
      "role": "assistant",
      "content": "Western Australia is one of the world's largest copper producers...",
      "timestamp": "2024-01-15T10:31:15Z",
      "metadata": {
        "processing_time": 1.2,
        "token_count": 150
      }
    }
  ],
  "context_metadata": {
    "total_messages": 15,
    "tokens_in_context": 2500
  }
}
```

#### Update Chat Metadata

```http
PUT /api/backend/chats/{chat_id}
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "title": "Updated Chat Title",
  "description": "New description",
  "tags": ["updated", "tags"]
}
```

#### Delete Chat

```http
DELETE /api/backend/chats/{chat_id}
Authorization: Bearer {token}

Response:
{
  "message": "Chat deleted successfully",
  "deleted_at": "2024-01-15T15:30:00Z"
}
```

### Enhanced Chat Endpoint

#### Context-Aware Chat Message

```http
POST /api/backend/chat
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "chat_id": "uuid-1234",
  "message": "What about nickel deposits in the same region?",
  "context_options": {
    "include_previous_messages": true,
    "max_context_messages": 10,
    "context_strategy": "relevant_only" // or "recent_only", "all"
  }
}

Response:
{
  "message_id": "msg-003",
  "response": "Based on our previous discussion about copper mining in Western Australia, nickel deposits in the region are also significant...",
  "chat_id": "uuid-1234",
  "timestamp": "2024-01-15T14:22:00Z",
  "context_used": {
    "messages_included": 3,
    "tokens_in_context": 450,
    "context_summary": "Previous discussion covered copper mining locations and production methods"
  },
  "sources": ["geological_report_123", "mining_survey_456"]
}
```

### Search and Export Endpoints

#### Search Chat History

```http
GET /api/backend/chats/search?q=copper+mining&chat_id=uuid-1234
Authorization: Bearer {token}

Response:
{
  "results": [
    {
      "message_id": "msg-001",
      "chat_id": "uuid-1234",
      "chat_title": "Copper Mining Discussion",
      "content": "Tell me about copper mining in Western Australia",
      "timestamp": "2024-01-15T10:31:00Z",
      "relevance_score": 0.95
    }
  ],
  "total_results": 5
}
```

#### Export Chat History

```http
GET /api/backend/chats/{chat_id}/export?format=json
Authorization: Bearer {token}

Response: Complete chat history in requested format
```

## 🔧 Implementation Strategy

### Phase 1: Foundation (Week 1-2)

1. **Data Models Implementation**

    - Create Pydantic models for ChatSession and ChatMessage
    - Add database schema (or in-memory storage structures)
    - Implement basic CRUD operations

2. **Core Chat Management**

    - Create, list, view, delete chat sessions
    - Basic message storage and retrieval
    - User authorization for chat access

3. **Modified Chat Endpoint**
    - Update existing `/api/backend/chat` to use chat_id
    - Basic message persistence
    - Simple context inclusion (last N messages)

### Phase 2: Context Intelligence (Week 3-4)

1. **Context Builder Implementation**

    - Intelligent context selection algorithms
    - Token counting and management
    - Context optimization for AI queries

2. **Enhanced Integration**

    - Pass context to Module 2 (Cortex Engine) efficiently
    - Context summarization for long conversations
    - Relevance-based message selection

3. **Performance Optimization**
    - Efficient message retrieval
    - Caching strategies for frequently accessed chats
    - Pagination for large chat histories

### Phase 3: Advanced Features (Week 5-6)

1. **Search and Discovery**

    - Full-text search across chat history
    - Semantic search using embeddings
    - Advanced filtering and sorting

2. **Export and Sharing**

    - Multiple export formats (JSON, PDF, CSV)
    - Chat sharing capabilities
    - Integration with external systems

3. **Analytics and Insights**
    - Chat usage statistics
    - Popular topics and trends
    - User engagement metrics

## 💾 Storage Strategy

### Option 1: In-Memory Storage (Development/MVP)

```python
# Simple in-memory storage for rapid prototyping
chat_sessions_db = {}  # {user_id: {chat_id: ChatSession}}
chat_messages_db = {}  # {chat_id: [ChatMessage]}
```

**Pros**: Fast development, no external dependencies
**Cons**: Data loss on restart, limited scalability

### Option 2: File-Based Storage (Intermediate)

```python
# JSON file storage with efficient indexing
# Structure: /data/chats/{user_id}/{chat_id}/
#   - metadata.json (chat session info)
#   - messages.jsonl (one message per line)
#   - index.json (search index)
```

**Pros**: Persistent, human-readable, version controllable
**Cons**: Limited concurrent access, scaling challenges

### Option 3: Database Storage (Production)

```sql
-- PostgreSQL/SQLite schema
CREATE TABLE chat_sessions (
    chat_id UUID PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata JSONB
);

CREATE TABLE chat_messages (
    message_id UUID PRIMARY KEY,
    chat_id UUID REFERENCES chat_sessions(chat_id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP,
    metadata JSONB
);
```

**Pros**: ACID compliance, advanced querying, scalability
**Cons**: Additional infrastructure complexity

### Recommended Approach

-   **Start with Option 2** (File-based) for rapid development
-   **Migrate to Option 3** (Database) for production deployment
-   **Abstract storage layer** to make migration seamless

## 🧠 Context Management Strategy

### Context Building Algorithm

1. **Recent Messages Strategy** (Default)

    ```python
    def build_recent_context(chat_id, max_messages=10, max_tokens=2000):
        # Get last N messages, respecting token limits
        # Format for AI consumption
        # Include role information (user/assistant)
    ```

2. **Relevant Messages Strategy** (Advanced)

    ```python
    def build_relevant_context(chat_id, current_query, max_tokens=2000):
        # Use semantic similarity to find relevant previous messages
        # Combine with recent messages
        # Prioritize by relevance score and recency
    ```

3. **Summarized Context Strategy** (Efficient)
    ```python
    def build_summarized_context(chat_id, max_tokens=1000):
        # Generate summary of older conversation
        # Include recent messages in full
        # Maintain conversation flow
    ```

### Context Formatting for AI

````python
def format_context_for_ai(messages, current_query):
    """
    Format conversation history for AI consumption

    Output format:
    ```
    Previous conversation:
    User: Tell me about copper mining in Western Australia
    Assistant: Western Australia is one of the world's largest copper producers...
    User: What are the main mining companies there?
    Assistant: The major copper mining companies in WA include...

    Current question: {current_query}
    ```
    """
````

## 🔒 Security and Privacy

### Data Isolation

-   **User-based access control**: Users can only access their own chats
-   **Role-based permissions**: Admin users can have broader access
-   **Chat sharing controls**: Optional sharing mechanisms with proper authorization

### Data Encryption

-   **At-rest encryption**: Sensitive chat content encrypted in storage
-   **In-transit encryption**: HTTPS for all API communications
-   **Key management**: Proper encryption key rotation and management

### Audit Trail

-   **Access logging**: Track who accessed which chats when
-   **Modification history**: Track changes to chat metadata
-   **Deletion tracking**: Soft deletes with audit trail

## 📈 Performance Considerations

### Caching Strategy

```python
# Multi-level caching approach
1. In-memory cache for active chats (Redis/local)
2. Message pagination to avoid loading large histories
3. Context caching for frequently accessed conversations
4. Precomputed summaries for long chats
```

### Database Optimization

```sql
-- Efficient indexing strategy
CREATE INDEX idx_chat_sessions_user_activity ON chat_sessions(user_id, last_activity);
CREATE INDEX idx_chat_messages_chat_time ON chat_messages(chat_id, timestamp);
CREATE INDEX idx_chat_messages_content ON chat_messages USING GIN(to_tsvector('english', content));
```

### API Response Optimization

-   **Pagination**: All list endpoints support pagination
-   **Selective loading**: Optional message inclusion in chat details
-   **Compression**: GZIP compression for large responses
-   **Async processing**: Non-blocking operations for better throughput

## 🔄 Integration with Existing System

### Module 2 (Cortex Engine) Integration

```python
# Enhanced RAG query with context
async def rag_query_with_context(query: str, context_messages: List[ChatMessage]):
    # Build context string from message history
    context = format_context_for_ai(context_messages, query)

    # Send enhanced query to Module 2
    enhanced_query = f"{context}\n\nCurrent question: {query}"

    # Process through existing Cortex Engine RAG pipeline
    return await cortex_client.rag_query(enhanced_query)
```

### Backward Compatibility

-   **Existing `/api/backend/chat` endpoint**: Maintain compatibility with optional chat_id
-   **Default behavior**: Create temporary chat session if no chat_id provided
-   **Migration path**: Convert single-message interactions to multi-message chats

### Frontend Integration Points

```javascript
// New frontend capabilities enabled
1. Chat session management UI
2. Context-aware message composer
3. Chat history viewer with search
4. Export and sharing features
5. Multi-chat management dashboard
```

## 🧪 Testing Strategy

### Unit Tests

-   Chat session CRUD operations
-   Message storage and retrieval
-   Context building algorithms
-   Authorization and access control

### Integration Tests

-   End-to-end chat conversation flows
-   Context passing to Module 2
-   Multi-user chat isolation
-   Performance under load

### API Tests

```python
# Example test cases
def test_create_chat_session():
    # Test chat creation with various parameters

def test_chat_message_with_context():
    # Test context inclusion in AI queries

def test_user_chat_isolation():
    # Ensure users can't access others' chats

def test_context_token_limits():
    # Verify token limit enforcement
```

## 📋 Migration Plan

### Database Migration

```python
# Migration script structure
class ChatHistoryMigration:
    def migrate_existing_data():
        # Convert existing single-message chats to sessions
        # Preserve message timestamps and content
        # Maintain user associations

    def create_default_sessions():
        # Create default chat sessions for existing users
        # Group related messages by timestamp/topic
```

### API Versioning

-   **v1 APIs**: Maintain existing endpoints for backward compatibility
-   **v2 APIs**: New chat history endpoints with enhanced features
-   **Deprecation timeline**: Gradual migration over 6 months

## 🔮 Future Enhancements

### Advanced AI Features

-   **Conversation summarization**: AI-generated chat summaries
-   **Topic extraction**: Automatic tagging based on conversation content
-   **Sentiment analysis**: Track conversation sentiment over time
-   **Intent recognition**: Understand user goals across conversation

### Collaboration Features

-   **Chat sharing**: Share conversations with team members
-   **Collaborative chats**: Multiple users in same conversation
-   **Comment system**: Add notes and comments to chat messages
-   **Version history**: Track changes to shared conversations

### Analytics and Insights

-   **Usage analytics**: Chat frequency, popular topics, user engagement
-   **Content analysis**: Most discussed geological topics, query patterns
-   **Performance metrics**: Response times, context effectiveness
-   **User behavior**: Chat session patterns, feature usage

### Integration Expansions

-   **External chat platforms**: Slack, Teams integration
-   **API ecosystem**: Third-party chat history access
-   **Webhook support**: Real-time chat events
-   **Mobile optimization**: Enhanced mobile chat experience

## 📝 Implementation Checklist

### Core Components

-   [ ] Chat session data models
-   [ ] Message storage system
-   [ ] Context builder implementation
-   [ ] Enhanced chat endpoint
-   [ ] Chat management endpoints
-   [ ] User authorization layer

### Security & Privacy

-   [ ] Data encryption implementation
-   [ ] Access control validation
-   [ ] Audit logging system
-   [ ] Privacy compliance review

### Performance & Scalability

-   [ ] Caching implementation
-   [ ] Database optimization
-   [ ] API response optimization
-   [ ] Load testing completion

### Testing & Quality

-   [ ] Unit test coverage (>80%)
-   [ ] Integration test suite
-   [ ] API documentation updates
-   [ ] User acceptance testing

### Deployment & Monitoring

-   [ ] Production deployment strategy
-   [ ] Monitoring and alerting setup
-   [ ] Backup and recovery procedures
-   [ ] Performance monitoring dashboard

---

This design provides a comprehensive foundation for implementing chat history functionality in the Backend Gateway module, enabling rich, contextual conversations while maintaining security, performance, and scalability requirements.
