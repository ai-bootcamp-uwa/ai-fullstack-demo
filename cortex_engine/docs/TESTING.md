# Testing Azure OpenAI Models

This guide explains how to test your Azure OpenAI configuration and the cortex_engine module.

## Prerequisites

1. **Environment Setup**: Ensure you have a properly configured `.env` file
2. **API Access**: Valid Azure OpenAI API key and correct deployment names
3. **Dependencies**: Install required packages (`pip install -r requirements.txt`)

## Quick Test (Bash Script)

### 🚀 Fast API Test with Curl

Use our automated bash script to quickly test both models:

```bash
# From cortex_engine directory
./tests/test_azure_openai.sh
```

**What it tests:**

- ✅ Configuration loading from `.env`
- ✅ API key validation
- ✅ Embedding model (`text-embedding-ada-002`)
- ✅ Chat model (`gpt-4.1-mini`)
- ✅ Network connectivity and authentication

**Expected Output:**

```
🧪 Testing Azure OpenAI Models...
=================================
✅ Loaded configuration from .env

Configuration:
  Endpoint: https://29192-md6s8lam-eastus2.openai.azure.com/
  API Version: 2024-02-01
  Chat Model: gpt-4.1-mini
  Embedding Model: text-embedding-ada-002

🔍 Testing Embedding Model (text-embedding-ada-002)...
================================================
✅ Embedding model test PASSED
📊 Response preview: [-0.027737359, -0.0040871273, ...]

💬 Testing Chat Model (gpt-4.1-mini)...
=======================================
✅ Chat model test PASSED
💬 Response: TEST SUCCESS

🏁 Testing complete!
```

## Python Module Testing

### 🐍 Test Embedding Module

```python
# Test the embedding functionality
python -c "
from src.embedding import EmbeddingModel
import os
from dotenv import load_dotenv

load_dotenv()
model = EmbeddingModel()
result = model.get_embedding('Hello, this is a test.')
print(f'✅ Embedding generated: {len(result)} dimensions')
print(f'📊 First 5 values: {result[:5]}')
"
```

### 🤖 Test Chat Module

```python
# Test the chat functionality
python -c "
from src.similarity import SimilarityAnalyzer
import os
from dotenv import load_dotenv

load_dotenv()
analyzer = SimilarityAnalyzer()
response = analyzer.chat_completion('Say hello world')
print(f'✅ Chat response: {response}')
"
```

### 🔍 Test Similarity Analysis

```python
# Test full similarity workflow
python -c "
from src.similarity import SimilarityAnalyzer
import os
from dotenv import load_dotenv

load_dotenv()
analyzer = SimilarityAnalyzer()

# Test similarity calculation
text1 = 'I love programming with Python'
text2 = 'Python programming is my favorite'
text3 = 'The weather is nice today'

sim_high = analyzer.calculate_similarity(text1, text2)
sim_low = analyzer.calculate_similarity(text1, text3)

print(f'✅ High similarity: {sim_high:.3f}')
print(f'✅ Low similarity: {sim_low:.3f}')
print(f'✅ Test passed: {sim_high > sim_low}')
"
```

## Troubleshooting Tests

### Common Issues & Solutions

#### 1. ❌ "Resource not found" (HTTP 404)

```bash
# Problem: Invalid API version or wrong endpoint
# Solution: Check your .env file

# Verify API version (should be 2024-02-01 or similar valid version)
grep "AZURE_OPENAI_API_VERSION" .env

# Verify endpoint format (should end with .openai.azure.com/)
grep "AZURE_OPENAI_ENDPOINT" .env
```

#### 2. ❌ "DeploymentNotFound"

```bash
# Problem: Deployment names don't match Azure OpenAI Studio
# Solution: Check exact deployment names in Azure Portal

# Verify deployment names
grep -E "(CHAT_MODEL|EMBEDDING_MODEL)" .env

# Expected format:
# CHAT_MODEL=gpt-4.1-mini
# EMBEDDING_MODEL=text-embedding-ada-002
```

#### 3. ❌ "Authentication failed"

```bash
# Problem: Invalid or missing API key
# Solution: Update API key in .env

# Check if API key is placeholder
grep "AZURE_OPENAI_API_KEY" .env

# Should NOT show: your_actual_api_key_here
```

#### 4. ❌ Python import errors

```bash
# Problem: Missing dependencies
# Solution: Install requirements

pip install -r requirements.txt

# Or specific packages:
pip install openai python-dotenv numpy
```

## Test Scenarios

### 🎯 Basic Functionality Tests

1. **Configuration Loading**

   ```bash
   python -c "from src.config import config; print('✅ Config loaded')"
   ```

2. **Environment Variables**

   ```bash
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ API Key:', 'SET' if os.getenv('AZURE_OPENAI_API_KEY') else 'MISSING')"
   ```

3. **Model Initialization**
   ```bash
   python -c "from src.embedding import EmbeddingModel; m = EmbeddingModel(); print('✅ Embedding model initialized')"
   python -c "from src.similarity import SimilarityAnalyzer; s = SimilarityAnalyzer(); print('✅ Similarity analyzer initialized')"
   ```

### 🔬 Advanced Integration Tests

1. **Batch Embeddings**

   ```python
   from src.embedding import EmbeddingModel

   model = EmbeddingModel()
   texts = ["Hello world", "Python programming", "Azure OpenAI"]
   embeddings = [model.get_embedding(text) for text in texts]
   print(f"✅ Generated {len(embeddings)} embeddings")
   ```

2. **Rate Limiting Test**

   ```python
   # Test multiple rapid requests (should handle rate limits gracefully)
   from src.embedding import EmbeddingModel
   import time

   model = EmbeddingModel()
   start = time.time()

   for i in range(5):
       result = model.get_embedding(f"Test message {i}")
       print(f"Request {i+1}: {len(result)} dimensions")

   print(f"✅ Completed 5 requests in {time.time() - start:.2f}s")
   ```

## Automated Test Suite

### 📋 Run All Tests

Create a comprehensive test script:

```bash
# Run all tests in sequence
./tests/test_azure_openai.sh  # API connectivity
python -m pytest tests/       # Python unit tests (if available)
```

### 🎪 Continuous Testing

For development, monitor your models:

```bash
# Watch for changes and auto-test
while true; do
    echo "🔄 Testing at $(date)"
    ./tests/test_azure_openai.sh
    sleep 300  # Test every 5 minutes
done
```

## Performance Benchmarks

### ⚡ Expected Response Times

- **Embedding requests**: 100-500ms
- **Chat completions**: 500-2000ms
- **Similarity calculations**: 200-800ms

### 📊 Rate Limits

Based on your Azure OpenAI configuration:

- **Embedding**: 120 requests/minute, 20,000 tokens/minute
- **Chat**: Standard Azure OpenAI limits (varies by deployment)

---

## Next Steps

Once all tests pass:

1. ✅ **Integration**: Use cortex_engine in your application
2. ✅ **Monitoring**: Set up logging and error tracking
3. ✅ **Scaling**: Configure for production workloads

For detailed setup instructions, see [AZURE_OPENAI_SETUP.md](AZURE_OPENAI_SETUP.md)
