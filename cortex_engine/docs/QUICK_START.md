# Quick Start - Cortex Engine Setup

**⚡ 5-Minute Setup for Azure OpenAI Integration**

## Prerequisites Checklist

- [ ] Azure OpenAI resource with API key
- [ ] Model deployments created (embedding + chat)
- [ ] Python 3.8+ installed

## Setup Commands

```bash
# 1. Install dependencies
cd cortex_engine
pip install -r requirements.txt

# 2. Create config file
cp env.example .env

# 3. Edit .env with YOUR values
nano .env  # Set all 5 required variables

# 4. Test configuration
python tests/test_deployments.py

# 5. Start service
uvicorn src.main:app --reload --port 3002
```

## Required .env Variables

```bash
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-01
EMBEDDING_MODEL=your_embedding_deployment_name
CHAT_MODEL=your_chat_deployment_name
```

## Test Your Setup

```bash
# Health check
curl http://localhost:3002/health

# Generate embeddings
curl -X POST http://localhost:3002/embed \
  -H "Content-Type: application/json" \
  -d '{"data": ["test"]}'
```

## Need Help?

- �� **Full Guide:** [`docs/AZURE_OPENAI_SETUP.md`](./AZURE_OPENAI_SETUP.md)
- 🔧 **Troubleshooting:** Check deployment names in Azure OpenAI Studio
- ✅ **Test Script:** `python tests/test_deployments.py`

---

**🎯 Goal:** See `✅ Configuration test completed successfully!` from the test script.
