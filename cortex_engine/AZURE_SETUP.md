# Azure OpenAI Integration Setup

This guide explains how to configure the cortex_engine to use your Azure OpenAI deployments.

## Prerequisites

1. Azure OpenAI resource deployed (you have this)
2. GPT-4o-mini model deployed (you have this)
3. text-embedding-ada-002 model deployed (you have this)
4. API key from your Azure OpenAI resource

## Configuration

### Option 1: Environment Variables (Recommended)

Set the following environment variables in your shell:

```bash
export AZURE_OPENAI_ENDPOINT="https://22965-md5ohpse-eastus2.cognitiveservices.azure.com/"
export AZURE_OPENAI_API_KEY="your_actual_api_key_here"
export AZURE_OPENAI_API_VERSION="2024-02-01"
```

### Option 2: Create .env file

Create a `.env` file in the cortex_engine directory:

```
AZURE_OPENAI_ENDPOINT=https://22965-md5ohpse-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-01
```

**Important:** Never commit your API key to version control!

## Getting Your API Key

1. Go to the Azure Portal
2. Navigate to your Azure OpenAI resource (22965-md5ohpse-eastus2)
3. Go to "Keys and Endpoint" in the left menu
4. Copy one of the keys

## Your Model Deployments

Based on your Azure AI Foundry setup:
- **Embedding Model**: `text-embedding-ada-002` (1536 dimensions)
- **Chat Model**: `gpt-4o-mini`
- **Endpoint**: `https://22965-md5ohpse-eastus2.cognitiveservices.azure.com/`

## Testing the Integration

1. Set your API key in the environment
2. Start the server:
   ```bash
   uvicorn main:app --reload --port 3002
   ```

3. Test embedding generation with real Azure OpenAI:
   ```bash
   curl -X POST http://127.0.0.1:3002/embed \
     -H "Content-Type: application/json" \
     -d '{"data": ["geological sample from Western Australia", "copper mining report", "iron ore deposit analysis"]}'
   ```

4. Test RAG functionality with real GPT-4o-mini:
   ```bash
   curl -X POST http://127.0.0.1:3002/rag-query \
     -H "Content-Type: application/json" \
     -d '{"query": "What geological samples are available for analysis?"}'
   ```

## Model Configuration

The current configuration uses your exact Azure deployments:
- **Embedding Model**: `text-embedding-ada-002` 
  - Dimensions: 1536
  - Rate limit: 120 requests/minute
  - Token limit: 20,000 tokens/minute
- **Chat Model**: `gpt-4o-mini` (your deployed model)

## Troubleshooting

### "Using placeholder random embeddings"
- Your API key is not set or incorrect
- Check your environment variables
- Verify the endpoint URL matches: `https://22965-md5ohpse-eastus2.cognitiveservices.azure.com/`

### "RAG not available - Azure OpenAI not configured"
- Same as above - API key/endpoint issues
- Check that your deployment names match exactly:
  - `text-embedding-ada-002` for embeddings
  - `gpt-4o-mini` for chat

### Rate Limiting
- text-embedding-ada-002: 120 requests/minute, 20K tokens/minute
- Stay within these limits for smooth operation

### Dimension mismatch warnings
- Normal when transitioning from placeholder (128-dim) to real embeddings (1536-dim)
- The system handles this automatically

## Production Considerations

1. Monitor your Azure OpenAI usage and costs in the Azure portal
2. Use Azure Key Vault for API key management
3. Implement proper error handling and retries
4. Add request rate limiting to stay within Azure limits
5. Consider using managed identity authentication
6. Monitor the model retirement date (Apr 30, 2026 for text-embedding-ada-002) 