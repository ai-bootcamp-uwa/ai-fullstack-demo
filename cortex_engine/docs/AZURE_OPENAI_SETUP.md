# Azure OpenAI Configuration Guide

**Strict Configuration Mode - No Defaults, Explicit Setup Required**

This guide provides step-by-step instructions for configuring the Cortex Engine with Azure OpenAI services using strict configuration mode where all required values must be explicitly set.

## 🎯 Overview

The Cortex Engine uses **strict configuration mode** which means:

- ❌ **No default values** for critical settings
- ✅ **All required values** must be set in `.env` file
- ✅ **Fail fast** if configuration is incomplete
- ✅ **Clear error messages** for missing configuration

## 📋 Prerequisites

Before starting, ensure you have:

1. **Azure OpenAI Resource** deployed and accessible
2. **Model Deployments** created in Azure OpenAI Studio:
   - An embedding model (e.g., text-embedding-ada-002)
   - A chat model (e.g., gpt-4o-mini)
3. **API Key** from your Azure OpenAI resource
4. **Python 3.8+** with required dependencies

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
cd cortex_engine
pip install -r requirements.txt
```

### Step 2: Create Configuration File

```bash
# Copy the template
cp env.example .env

# Edit with your actual values
nano .env  # or use your preferred editor
```

### Step 3: Configure Required Values

Edit `.env` and set **ALL** required values:

```bash
# REQUIRED - No defaults, all must be set
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-01
EMBEDDING_MODEL=your_exact_embedding_deployment_name
CHAT_MODEL=your_exact_chat_deployment_name
```

### Step 4: Test Configuration

```bash
python tests/test_deployments.py
```

### Step 5: Start the Service

```bash
uvicorn src.main:app --reload --port 3002
```

## 🔧 Detailed Configuration

### Required Environment Variables

| Variable                   | Description                          | Example                                           | Required |
| -------------------------- | ------------------------------------ | ------------------------------------------------- | -------- |
| `AZURE_OPENAI_ENDPOINT`    | Your Azure OpenAI resource endpoint  | `https://myresource.cognitiveservices.azure.com/` | ✅ Yes   |
| `AZURE_OPENAI_API_KEY`     | API key from Azure Portal            | `abc123def456...`                                 | ✅ Yes   |
| `AZURE_OPENAI_API_VERSION` | API version to use                   | `2024-02-01`                                      | ✅ Yes   |
| `EMBEDDING_MODEL`          | Exact deployment name for embeddings | `text-embedding-ada-002`                          | ✅ Yes   |
| `CHAT_MODEL`               | Exact deployment name for chat       | `gpt-4o-mini`                                     | ✅ Yes   |

### Optional Environment Variables

| Variable                            | Description                       | Default | Required |
| ----------------------------------- | --------------------------------- | ------- | -------- |
| `MAX_EMBEDDING_REQUESTS_PER_MINUTE` | Rate limit for embedding requests | `120`   | ❌ No    |
| `MAX_EMBEDDING_TOKENS_PER_MINUTE`   | Token limit for embeddings        | `20000` | ❌ No    |
| `MAX_RETRIES`                       | Number of retry attempts          | `3`     | ❌ No    |
| `RETRY_DELAY_SECONDS`               | Delay between retries             | `1`     | ❌ No    |

## 🔍 Getting Your Configuration Values

### 1. Azure OpenAI Endpoint

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Click **"Keys and Endpoint"** in the left menu
4. Copy the **Endpoint** URL

**Common endpoint formats:**

- `https://your-resource.cognitiveservices.azure.com/`
- `https://your-resource.openai.azure.com/`
- `https://your-resource.services.ai.azure.com/`

### 2. API Key

1. In the same **"Keys and Endpoint"** section
2. Copy **Key 1** or **Key 2**
3. ⚠️ **Never commit this to version control!**

### 3. Deployment Names (Most Important!)

1. Go to [Azure OpenAI Studio](https://oai.azure.com/)
2. Select your resource
3. Click **"Deployments"** tab
4. Copy the exact **deployment names** (not model names)

**Example:**

- Model: `text-embedding-ada-002`
- Deployment Name: `my-embedding-deployment` ← Use this!

## 🧪 Testing Your Configuration

### Automated Test Script

```bash
cd cortex_engine
python tests/test_deployments.py
```

**Expected Output:**

```
=== Azure OpenAI Configuration Test (STRICT MODE) ===
Endpoint: https://myresource.cognitiveservices.azure.com/
API Version: 2024-02-01
Embedding Model: text-embedding-ada-002
Chat Model: gpt-4o-mini
API Key: ✓ Set

✅ Azure OpenAI client initialized successfully

🧪 Testing embedding deployment: text-embedding-ada-002
✅ Embedding deployment 'text-embedding-ada-002' works!
   Embedding dimensions: 1536

🧪 Testing chat deployment: gpt-4o-mini
✅ Chat deployment 'gpt-4o-mini' works!
   Response: Hello! How can I assist you today?

🎉 Configuration test completed successfully!
```

### Manual API Tests

```bash
# Test health endpoint
curl http://localhost:3002/health

# Test configuration endpoint
curl http://localhost:3002/config

# Test embedding generation
curl -X POST http://localhost:3002/embed \
  -H "Content-Type: application/json" \
  -d '{"data": ["test geological sample"]}'
```

## 🔥 Troubleshooting

### Common Errors and Solutions

#### ❌ "AZURE_OPENAI_API_KEY is required but not set in .env"

**Solution:**

1. Ensure `.env` file exists in `cortex_engine/` directory
2. Check that `AZURE_OPENAI_API_KEY=your_key_here` is uncommented
3. Verify no extra spaces around the `=`

#### ❌ "DeploymentNotFound"

**Solution:**

1. Go to Azure OpenAI Studio → Deployments
2. Copy the exact deployment name (not model name)
3. Update `EMBEDDING_MODEL` and `CHAT_MODEL` in `.env`

#### ❌ "401 Unauthorized"

**Solution:**

1. Verify your API key is correct
2. Check if the key has expired
3. Ensure you're using the right resource

#### ❌ "404 Not Found"

**Solution:**

1. Verify your endpoint URL is correct
2. Ensure it ends with `/`
3. Check the endpoint format matches your Azure setup

#### ❌ "Missing required environment variables"

**Solution:**

1. Run the test script to see which values are missing
2. Set ALL required values in `.env`
3. Double-check spelling and formatting

### Validation Checklist

- [ ] `.env` file exists in `cortex_engine/` directory
- [ ] All 5 required variables are set and uncommented
- [ ] API key is valid and not expired
- [ ] Endpoint URL is correct and ends with `/`
- [ ] Deployment names match exactly what's in Azure OpenAI Studio
- [ ] Test script passes all checks
- [ ] Health endpoint returns `"configuration_valid": true`

## 🎮 Usage Examples

### Basic Embedding Generation

```python
import requests

response = requests.post("http://localhost:3002/embed", json={
    "data": ["geological sample from Western Australia", "copper mining report"]
})
embeddings = response.json()["embeddings"]
print(f"Generated {len(embeddings)} embeddings")
```

### RAG Query

```python
response = requests.post("http://localhost:3002/rag-query", json={
    "query": "What geological samples are available for analysis?"
})
result = response.json()
print(f"Answer: {result['result']}")
```

### Health Check

```python
response = requests.get("http://localhost:3002/health")
status = response.json()
print(f"Azure OpenAI configured: {status['azure_openai_configured']}")
print(f"Configuration valid: {status['configuration_valid']}")
```

## 🏗️ Architecture

### Configuration Flow

```
.env file → config.py → embedding.py/similarity.py → Azure OpenAI
```

### Key Components

- **`config.py`**: Centralized configuration with strict validation
- **`embedding.py`**: Embedding generation using Azure OpenAI
- **`similarity.py`**: Vector search and RAG functionality
- **`test_deployments.py`**: Configuration validation script

## 🔒 Security Best Practices

1. **Never commit `.env` to version control**

   ```bash
   # Ensure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment-specific configurations**

   ```bash
   # Development
   cp env.example .env.dev

   # Production
   cp env.example .env.prod
   ```

3. **Rotate API keys regularly**
   - Set up key rotation schedule
   - Monitor usage in Azure Portal
   - Use Azure Key Vault for production

## 📞 Support

### Documentation

- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

### Common Resources

- Azure OpenAI Studio: https://oai.azure.com/
- Azure Portal: https://portal.azure.com/
- API Reference: https://docs.microsoft.com/en-us/azure/cognitive-services/openai/reference

---

**🎉 You're all set!** Your Cortex Engine is now configured with Azure OpenAI in strict mode for reliable, production-ready operation.
