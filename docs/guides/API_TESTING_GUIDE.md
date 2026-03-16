# FSS Hero Chatbot - Testing and Monitoring API Endpoints Guide

This guide demonstrates how to use the three critical testing and monitoring endpoints implemented for the FSS Hero Chatbot RAG system.

## Endpoints Overview

### 1. `/debug/retrieval-test` (POST) - HIGHEST PRIORITY
Test and debug RAG retrieval with detailed results including similarity scores, metadata, and query enhancement analysis.

### 2. `/health/detailed` (GET) - HIGH PRIORITY
Comprehensive health check for all system components including Qdrant, BGE-M3, Gemini API, Tavily, and DocumentProcessor.

### 3. `/debug/embedding-test` (POST) - MEDIUM PRIORITY
Test embedding generation and semantic similarity computation for debugging retrieval issues.

---

## 1. Retrieval Testing Endpoint

**Path**: `POST /debug/retrieval-test`

**Purpose**: Test RAG retrieval with detailed analysis

**Use Cases**:
- Verify new documents are indexed correctly
- Test different similarity thresholds
- Debug retrieval quality issues
- Compare original vs enhanced queries
- Analyze what documents are being retrieved

### Request Body Schema

```json
{
  "query": "string (required)",
  "similarity_threshold": 0.7,  // float 0.0-1.0, default 0.7
  "top_k": 5,                    // int 1-20, default 5
  "return_scores": true,         // bool, default true
  "return_metadata": true        // bool, default true
}
```

### Example 1: Basic Retrieval Test

**cURL**:
```bash
curl -X POST "http://localhost:8000/debug/retrieval-test" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to set stop loss?",
    "similarity_threshold": 0.7,
    "top_k": 5,
    "return_scores": true,
    "return_metadata": true
  }'
```

**Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/debug/retrieval-test",
    json={
        "query": "How to set stop loss?",
        "similarity_threshold": 0.7,
        "top_k": 5,
        "return_scores": True,
        "return_metadata": True
    }
)

data = response.json()
print(f"Retrieved {data['total_results']} results")
print(f"Retrieval latency: {data['retrieval_latency_ms']}ms")

if data.get('enhanced_query'):
    print(f"Query enhanced: {data['original_query']} → {data['enhanced_query']}")

for i, result in enumerate(data['results']):
    print(f"\nResult {i+1}:")
    print(f"  Score: {result['score']}")
    print(f"  Content: {result['content'][:200]}...")
    print(f"  Metadata: {result['metadata']}")
```

### Example 2: Test with Lower Threshold

```bash
curl -X POST "http://localhost:8000/debug/retrieval-test" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Chart not loading",
    "similarity_threshold": 0.5,
    "top_k": 10,
    "return_scores": true,
    "return_metadata": true
  }'
```

### Response Schema

```json
{
  "original_query": "How to set stop loss?",
  "enhanced_query": "How to set up and configure stop loss orders...",
  "query_enhancement_enabled": true,
  "results": [
    {
      "content": "Document content...",
      "score": 0.85,
      "metadata": {
        "file_name": "example.pdf",
        "source_type": "pdf",
        "chunk_index": 0,
        "total_chunks": 10
      },
      "chunk_info": {
        "chunk_index": 0,
        "total_chunks": 10,
        "file_name": "example.pdf",
        "source_type": "pdf"
      }
    }
  ],
  "total_results": 5,
  "retrieval_latency_ms": 150.5,
  "collection_stats": {
    "total_documents": 1000,
    "by_source_type": {"pdf": 500, "txt": 300},
    "by_upload_source": {"bulk": 800, "api": 200}
  },
  "search_parameters": {
    "similarity_threshold": 0.7,
    "top_k": 5,
    "return_scores": true,
    "return_metadata": true
  }
}
```

---

## 2. Detailed Health Check Endpoint

**Path**: `GET /health/detailed`

**Purpose**: Comprehensive health check for all system components

**Use Cases**:
- Monitor system health in production
- Debug connectivity issues
- Validate configuration changes
- Pre-deployment verification
- Identify component failures

### Example: Get System Health

**cURL**:
```bash
curl -X GET "http://localhost:8000/health/detailed"
```

**Python**:
```python
import requests

response = requests.get("http://localhost:8000/health/detailed")
data = response.json()

print(f"Overall Status: {data['overall_status']}")
print(f"Timestamp: {data['timestamp']}")

print("\nComponent Health:")
for component in data['components']:
    status_symbol = {'healthy': '✓', 'degraded': '⚠', 'unhealthy': '✗'}[component['status']]
    print(f"{status_symbol} {component['name']}: {component['status']}")
    if component.get('latency_ms'):
        print(f"  Latency: {component['latency_ms']}ms")
    if component.get('error'):
        print(f"  Error: {component['error']}")
```

### Response Schema

```json
{
  "overall_status": "healthy",  // "healthy" | "degraded" | "unhealthy"
  "timestamp": "2025-10-01T10:30:00.123456",
  "components": [
    {
      "name": "Qdrant Vector Database",
      "status": "healthy",
      "latency_ms": 45.2,
      "details": "Collection 'fsshero-chatbot-bge-m3' found with 1000 documents",
      "error": null
    },
    {
      "name": "BGE-M3 Embeddings",
      "status": "healthy",
      "latency_ms": 120.5,
      "details": "Generated 1024-dimensional embedding",
      "error": null
    },
    {
      "name": "Google Gemini API",
      "status": "healthy",
      "latency_ms": 800.3,
      "details": "Successfully connected to gemini-2.5-flash",
      "error": null
    },
    {
      "name": "Tavily Web Search",
      "status": "healthy",
      "latency_ms": 500.7,
      "details": "Successfully executed test search",
      "error": null
    },
    {
      "name": "DocumentProcessor",
      "status": "healthy",
      "latency_ms": 1.2,
      "details": "Initialized with 5 supported formats, chunk_size=1000",
      "error": null
    }
  ],
  "summary": {
    "total_components": 5,
    "healthy": 5,
    "degraded": 0,
    "unhealthy": 0,
    "critical_failures": 0,
    "non_critical_failures": 0
  }
}
```

### Status Levels

- **healthy**: All components operational
- **degraded**: Some non-critical components failing (e.g., Tavily not configured)
- **unhealthy**: Critical components failing (e.g., Qdrant connection failed)

---

## 3. Embedding Testing Endpoint

**Path**: `POST /debug/embedding-test`

**Purpose**: Test embedding generation and semantic similarity

**Use Cases**:
- Test if similar texts produce high similarity scores
- Verify embedding dimensions are correct
- Debug why certain queries don't match expected documents
- Analyze semantic relationships
- Validate BGE-M3 model is working correctly

### Request Body Schema

```json
{
  "texts": ["text1", "text2"],  // array (1-10 items required)
  "reference_text": "string",    // optional
  "compute_similarities": false  // bool, default false
}
```

### Example 1: Basic Embedding Test with Similarity Matrix

**cURL**:
```bash
curl -X POST "http://localhost:8000/debug/embedding-test" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "How to set stop loss?",
      "Stop loss configuration guide",
      "Account management features"
    ],
    "compute_similarities": true
  }'
```

**Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/debug/embedding-test",
    json={
        "texts": [
            "How to set stop loss?",
            "Stop loss configuration guide",
            "Account management features"
        ],
        "compute_similarities": True
    }
)

data = response.json()
print(f"Generated embeddings for {data['total_texts']} texts")
print(f"Processing time: {data['processing_time_ms']}ms")
print(f"Model: {data['embedding_model']}")

# Print similarity matrix
if data['similarity_matrix']:
    print("\nSimilarity Matrix:")
    for i, row in enumerate(data['similarity_matrix']):
        print(f"Text {i+1}: {[f'{s:.3f}' for s in row]}")
```

### Example 2: Compare Against Reference Text

**cURL**:
```bash
curl -X POST "http://localhost:8000/debug/embedding-test" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Trading platform features",
      "Market analysis tools",
      "Risk management strategies"
    ],
    "reference_text": "How to use the trading platform?",
    "compute_similarities": false
  }'
```

**Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/debug/embedding-test",
    json={
        "texts": [
            "Trading platform features",
            "Market analysis tools",
            "Risk management strategies"
        ],
        "reference_text": "How to use the trading platform?",
        "compute_similarities": False
    }
)

data = response.json()

print("Similarities to Reference:")
for result in data['results']:
    similarity = result['similarity_to_reference']
    print(f"{result['text_preview']}: {similarity:.3f}")
```

### Response Schema

```json
{
  "results": [
    {
      "text": "How to set stop loss?",
      "text_preview": "How to set stop loss?",
      "embedding_dimensions": 1024,
      "similarity_to_reference": 0.85
    }
  ],
  "total_texts": 3,
  "processing_time_ms": 250.5,
  "embedding_model": "BAAI/bge-m3",
  "similarity_matrix": [
    [1.0, 0.85, 0.45],
    [0.85, 1.0, 0.50],
    [0.45, 0.50, 1.0]
  ]
}
```

---

## Running the Test Script

A comprehensive test script is provided in `test_api_endpoints.py`:

### Run All Tests
```bash
python test_api_endpoints.py
```

### Run Individual Tests
```bash
# Health check only
python test_api_endpoints.py health

# Retrieval test only
python test_api_endpoints.py retrieval

# Basic embedding test
python test_api_endpoints.py embeddings

# Embedding test with reference
python test_api_endpoints.py embeddings-ref
```

---

## Debugging Common Issues

### Issue 1: No Results Retrieved
**Symptom**: `total_results: 0` in retrieval test

**Solutions**:
1. Lower the similarity threshold: `"similarity_threshold": 0.5`
2. Check if documents are indexed: `/documents/stats`
3. Verify collection exists: `/health/detailed`
4. Test embedding generation: `/debug/embedding-test`

### Issue 2: Low Similarity Scores
**Symptom**: All scores below 0.5

**Solutions**:
1. Check if query enhancement is working
2. Test embedding quality with `/debug/embedding-test`
3. Verify documents were chunked correctly
4. Check if embeddings were generated with correct model

### Issue 3: Component Unhealthy
**Symptom**: Component shows `"status": "unhealthy"` in health check

**Solutions**:
1. Check environment variables (API keys, URLs)
2. Verify network connectivity
3. Check logs for detailed error messages
4. Restart services if needed

---

## Integration with Monitoring

These endpoints can be integrated with monitoring tools:

### Prometheus/Grafana
```python
# Example: Export health metrics
health = requests.get("http://localhost:8000/health/detailed").json()

# Create metrics
overall_status = 1 if health['overall_status'] == 'healthy' else 0
component_health = {c['name']: 1 if c['status'] == 'healthy' else 0
                   for c in health['components']}
component_latency = {c['name']: c.get('latency_ms', 0)
                    for c in health['components']}
```

### Automated Testing
```bash
# Run health check before deployment
curl -f http://localhost:8000/health/detailed || exit 1

# Verify retrieval is working
curl -X POST http://localhost:8000/debug/retrieval-test \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}' \
  | jq -e '.total_results > 0'
```

---

## API Documentation

These endpoints are automatically documented in FastAPI's interactive docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both interfaces provide:
- Interactive testing
- Request/response schemas
- Example values
- Parameter descriptions

---

## Next Steps

1. **Set Up Monitoring**: Integrate `/health/detailed` with your monitoring system
2. **Create Alerts**: Set up alerts for unhealthy components
3. **Regular Testing**: Schedule periodic retrieval tests to verify quality
4. **Document Baselines**: Record typical similarity scores and latencies
5. **Automate Tests**: Add these endpoints to your CI/CD pipeline
