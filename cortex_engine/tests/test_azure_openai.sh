#!/bin/bash

# Test Azure OpenAI Models
# Make sure you've updated .env with your actual API key!

set -e  # Exit on any error

echo "🧪 Testing Azure OpenAI Models..."
echo "================================="

# Load environment variables from .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
    echo "✅ Loaded configuration from .env"
else
    echo "❌ .env file not found! Please create it from env.example"
    exit 1
fi

# Check required variables
if [ -z "$AZURE_OPENAI_ENDPOINT" ] || [ -z "$AZURE_OPENAI_API_KEY" ] || [ -z "$AZURE_OPENAI_API_VERSION" ]; then
    echo "❌ Missing required environment variables. Please check your .env file."
    exit 1
fi

if [ "$AZURE_OPENAI_API_KEY" = "your_actual_api_key_here" ]; then
    echo "❌ Please update AZURE_OPENAI_API_KEY in .env with your actual API key!"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  Endpoint: $AZURE_OPENAI_ENDPOINT"
echo "  API Version: $AZURE_OPENAI_API_VERSION"
echo "  Chat Model: $CHAT_MODEL"
echo "  Embedding Model: $EMBEDDING_MODEL"
echo ""

# Test 1: Embedding Model
echo "🔍 Testing Embedding Model ($EMBEDDING_MODEL)..."
echo "================================================"

EMBEDDING_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -d '{
    "input": "Hello, this is a test embedding request.",
    "model": "'$EMBEDDING_MODEL'"
  }' \
  "${AZURE_OPENAI_ENDPOINT}openai/deployments/${EMBEDDING_MODEL}/embeddings?api-version=${AZURE_OPENAI_API_VERSION}")

HTTP_STATUS=$(echo $EMBEDDING_RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
EMBEDDING_BODY=$(echo $EMBEDDING_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Embedding model test PASSED"
    echo "📊 Response preview:"
    echo "$EMBEDDING_BODY" | jq '.data[0].embedding[0:5]' 2>/dev/null || echo "$EMBEDDING_BODY"
else
    echo "❌ Embedding model test FAILED (HTTP $HTTP_STATUS)"
    echo "📋 Error response:"
    echo "$EMBEDDING_BODY" | jq . 2>/dev/null || echo "$EMBEDDING_BODY"
fi

echo ""

# Test 2: Chat Model
echo "💬 Testing Chat Model ($CHAT_MODEL)..."
echo "======================================="

CHAT_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello! Please respond with just: TEST SUCCESS"
      }
    ],
    "max_tokens": 10,
    "temperature": 0
  }' \
  "${AZURE_OPENAI_ENDPOINT}openai/deployments/${CHAT_MODEL}/chat/completions?api-version=${AZURE_OPENAI_API_VERSION}")

HTTP_STATUS=$(echo $CHAT_RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
CHAT_BODY=$(echo $CHAT_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Chat model test PASSED"
    echo "💬 Response:"
    echo "$CHAT_BODY" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$CHAT_BODY"
else
    echo "❌ Chat model test FAILED (HTTP $HTTP_STATUS)"
    echo "📋 Error response:"
    echo "$CHAT_BODY" | jq . 2>/dev/null || echo "$CHAT_BODY"
fi

echo ""
echo "�� Testing complete!"
