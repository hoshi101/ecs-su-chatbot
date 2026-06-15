# Postman Testing Guide for ECS Chatbot API

Complete guide to testing the new testing/monitoring endpoints using Postman.

---

## Table of Contents
1. [Setup](#setup)
2. [Endpoint 1: Retrieval Testing](#endpoint-1-retrieval-testing-post-debugretrieval-test)
3. [Endpoint 2: System Health Check](#endpoint-2-system-health-check-get-healthdetailed)
4. [Endpoint 3: Embedding Testing](#endpoint-3-embedding-testing-post-debugembedding-test)
5. [Common Issues](#common-issues)

---

## Setup

### Prerequisites
1. **Start your FastAPI server:**
   ```bash
   .venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload
   ```

2. **Verify server is running:**
   - Open browser: http://localhost:8001/docs
   - You should see the FastAPI Swagger documentation

3. **Install Postman:**
   - Download from: https://www.postman.com/downloads/
   - Or use web version: https://web.postman.com/

### Base URL
All endpoints use: `http://localhost:8001`

---

## Endpoint 1: Retrieval Testing (POST /debug/retrieval-test)

### Purpose
Test your RAG retrieval system to see which documents are being retrieved for a query, with similarity scores and metadata.

### When to Use
- Verify new documents are indexed correctly
- Debug why certain queries don't find expected documents
- Test different similarity thresholds
- Compare original vs enhanced queries
- Analyze retrieval quality

---

### Step-by-Step Postman Setup

#### Step 1: Create New Request
1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Set method to **POST**
4. Enter URL: `http://localhost:8000/debug/retrieval-test`

#### Step 2: Configure Headers
1. Click the **"Headers"** tab
2. Add header:
   - **Key:** `Content-Type`
   - **Value:** `application/json`

#### Step 3: Configure Request Body
1. Click the **"Body"** tab
2. Select **"raw"**
3. Select **"JSON"** from dropdown (right side)
4. Paste this example:

```json
{
  "query": "How to set stop loss?",
  "similarity_threshold": 0.7,
  "top_k": 5,
  "return_scores": true,
  "return_metadata": true
}
```

#### Step 4: Send Request
1. Click **"Send"** button
2. View response in bottom panel

---

### Request Parameters Explained

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *required* | The search query to test |
| `similarity_threshold` | float | 0.7 | Minimum similarity score (0.0-1.0). Lower = more results |
| `top_k` | integer | 5 | Maximum number of results to return (1-20) |
| `return_scores` | boolean | true | Include similarity scores in response |
| `return_metadata` | boolean | true | Include document metadata in response |

---

### Example Requests

#### Example 1: Basic Retrieval Test
```json
{
  "query": "How do I use stop loss orders?",
  "similarity_threshold": 0.7,
  "top_k": 5,
  "return_scores": true,
  "return_metadata": true
}
```

**What it does:** Searches for top 5 documents about stop loss orders with minimum 0.7 similarity.

---

#### Example 2: Lower Threshold (More Results)
```json
{
  "query": "trading features",
  "similarity_threshold": 0.5,
  "top_k": 10,
  "return_scores": true,
  "return_metadata": true
}
```

**What it does:** Lower threshold (0.5) will return more results, useful for debugging when no results are found.

---

#### Example 3: Test Query Enhancement
```json
{
  "query": "stop loss",
  "similarity_threshold": 0.7,
  "top_k": 5,
  "return_scores": true,
  "return_metadata": true
}
```

**What to look for:** Compare `original_query` vs `enhanced_query` in response to see how the assistant enhances short queries.

---

### Response Structure

```json
{
  "original_query": "How to set stop loss?",
  "enhanced_query": "How to set up and configure stop loss orders in the Finansia Hero trading platform?",
  "query_enhancement_enabled": true,
  "results": [
    {
      "content": "Stop loss orders allow you to automatically sell...",
      "score": 0.87,
      "metadata": {
        "file_name": "trading_guide.pdf",
        "source_type": "pdf",
        "upload_source": "api",
        "document_id": "abc123",
        "chunk_index": 5,
        "total_chunks": 23
      },
      "chunk_info": {
        "chunk_index": 5,
        "total_chunks": 23,
        "file_name": "trading_guide.pdf",
        "source_type": "pdf"
      }
    }
  ],
  "total_results": 5,
  "retrieval_latency_ms": 142.35,
  "collection_stats": {
    "total_documents": 1250,
    "by_source_type": {
      "pdf": 800,
      "csv": 200,
      "json": 150,
      "txt": 100
    }
  },
  "search_parameters": {
    "similarity_threshold": 0.7,
    "top_k": 5,
    "return_scores": true,
    "return_metadata": true
  }
}
```

### What to Analyze in Response

✅ **Good Signs:**
- `score` values above 0.7 (high relevance)
- `results` contains expected documents
- `enhanced_query` is more specific than `original_query`
- `retrieval_latency_ms` is under 500ms

⚠️ **Warning Signs:**
- `total_results` is 0 (nothing found)
- All `score` values below 0.5 (poor matches)
- `retrieval_latency_ms` over 2000ms (slow)

---

## Endpoint 2: System Health Check (GET /health/detailed)

### Purpose
Check if all system components (Qdrant, BGE-M3, Gemini, Tavily, DocumentProcessor) are working correctly.

### When to Use
- Before deploying to production
- Debugging connectivity issues
- Regular monitoring checks
- After configuration changes
- Troubleshooting system issues

---

### Step-by-Step Postman Setup

#### Step 1: Create New Request
1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Set method to **GET**
4. Enter URL: `http://localhost:8000/health/detailed`

#### Step 2: Send Request
1. Click **"Send"** button (no body or headers needed)
2. View response in bottom panel

That's it! GET requests are simple - no body required.

---

### Response Structure

```json
{
  "overall_status": "healthy",
  "timestamp": "2025-10-01T14:30:45.123456",
  "components": [
    {
      "name": "Qdrant Vector Database",
      "status": "healthy",
      "latency_ms": 45.23,
      "details": "Collection 'ecs-su-chatbot-bge-m3' found with 1250 documents",
      "error": null
    },
    {
      "name": "BGE-M3 Embeddings",
      "status": "healthy",
      "latency_ms": 89.12,
      "details": "Generated 1024-dimensional embedding",
      "error": null
    },
    {
      "name": "Google Gemini API",
      "status": "healthy",
      "latency_ms": 567.45,
      "details": "Successfully connected to gemini-2.5-flash",
      "error": null
    },
    {
      "name": "Tavily Web Search",
      "status": "healthy",
      "latency_ms": 234.67,
      "details": "Successfully executed test search",
      "error": null
    },
    {
      "name": "DocumentProcessor",
      "status": "healthy",
      "latency_ms": 1.23,
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

### Status Levels Explained

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **healthy** | Component working perfectly | None - all good ✅ |
| **degraded** | Component has issues but system still works | Investigate soon ⚠️ |
| **unhealthy** | Critical failure - component not working | Fix immediately ❌ |

### Component Criticality

**Critical Components** (Must be healthy):
- ✅ Qdrant Vector Database
- ✅ BGE-M3 Embeddings
- ✅ Google Gemini API
- ✅ DocumentProcessor

**Non-Critical Components** (Can be degraded):
- ⚠️ Tavily Web Search (system works without it)

---

### Common Health Check Scenarios

#### Scenario 1: All Healthy ✅
```json
{
  "overall_status": "healthy",
  "summary": {
    "healthy": 5,
    "degraded": 0,
    "unhealthy": 0
  }
}
```
**Action:** None needed. System is production-ready.

---

#### Scenario 2: Tavily Not Configured ⚠️
```json
{
  "overall_status": "degraded",
  "components": [
    {
      "name": "Tavily Web Search",
      "status": "degraded",
      "details": "Tavily API key not configured",
      "error": "TAVILY_API_KEY not set"
    }
  ]
}
```
**Action:** Add `TAVILY_API_KEY` to `.env` file if you want web search.

---

#### Scenario 3: Qdrant Connection Failed ❌
```json
{
  "overall_status": "unhealthy",
  "components": [
    {
      "name": "Qdrant Vector Database",
      "status": "unhealthy",
      "details": "Failed to connect to Qdrant",
      "error": "Connection refused at https://your-qdrant-url.com"
    }
  ]
}
```
**Action:** Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env` file. Verify Qdrant is running.

---

## Endpoint 3: Embedding Testing (POST /debug/embedding-test)

### Purpose
Test how well your BGE-M3 embedding model understands semantic similarity between texts.

### When to Use
- Verify embeddings are working correctly
- Test if similar texts have high similarity scores
- Debug why queries don't match expected documents
- Analyze semantic relationships
- Validate embedding dimensions (should be 1024)

---

### Step-by-Step Postman Setup

#### Step 1: Create New Request
1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Set method to **POST**
4. Enter URL: `http://localhost:8000/debug/embedding-test`

#### Step 2: Configure Headers
1. Click the **"Headers"** tab
2. Add header:
   - **Key:** `Content-Type`
   - **Value:** `application/json`

#### Step 3: Configure Request Body
1. Click the **"Body"** tab
2. Select **"raw"**
3. Select **"JSON"** from dropdown
4. Choose one of the examples below

---

### Example Requests

#### Example 1: Test Similarity Between Texts (Matrix Mode)
```json
{
  "texts": [
    "How to set stop loss?",
    "Stop loss configuration guide",
    "Account management features"
  ],
  "compute_similarities": true
}
```

**What it does:**
- Generates embeddings for all 3 texts
- Computes pairwise similarity matrix
- Shows how similar each text is to every other text

**Expected Result:**
- Texts 1 and 2 should have high similarity (both about stop loss)
- Text 3 should have lower similarity (different topic)

---

#### Example 2: Compare Against Reference Text
```json
{
  "texts": [
    "Trading platform features",
    "Account management",
    "Stop loss orders"
  ],
  "reference_text": "How to use the trading platform?",
  "compute_similarities": false
}
```

**What it does:**
- Generates embeddings for all 3 texts AND the reference text
- Computes similarity of each text to the reference
- Shows which text is most similar to your reference

**Expected Result:**
- "Trading platform features" should have highest similarity to reference
- "Account management" should have medium similarity
- "Stop loss orders" should have lower similarity

---

#### Example 3: Simple Embedding Generation
```json
{
  "texts": [
    "How to set stop loss?"
  ],
  "compute_similarities": false
}
```

**What it does:**
- Just generates embeddings without computing similarities
- Useful for verifying embedding dimensions (should be 1024)

---

### Request Parameters Explained

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `texts` | array | *required* | List of texts to embed (1-10 texts max) |
| `reference_text` | string | null | Optional reference text to compare against |
| `compute_similarities` | boolean | false | Compute pairwise similarity matrix |

**Note:** You can use EITHER `compute_similarities: true` OR `reference_text`, not both together.

---

### Response Structure (Matrix Mode)

```json
{
  "results": [
    {
      "text": "How to set stop loss?",
      "text_preview": "How to set stop loss?",
      "embedding_dimensions": 1024,
      "similarity_to_reference": null
    },
    {
      "text": "Stop loss configuration guide",
      "text_preview": "Stop loss configuration guide",
      "embedding_dimensions": 1024,
      "similarity_to_reference": null
    },
    {
      "text": "Account management features",
      "text_preview": "Account management features",
      "embedding_dimensions": 1024,
      "similarity_to_reference": null
    }
  ],
  "total_texts": 3,
  "processing_time_ms": 245.67,
  "embedding_model": "BAAI/bge-m3",
  "similarity_matrix": [
    [1.0, 0.82, 0.34],
    [0.82, 1.0, 0.31],
    [0.34, 0.31, 1.0]
  ]
}
```

### Understanding the Similarity Matrix

The matrix shows similarity between all text pairs:

```
              Text 0    Text 1    Text 2
Text 0 (stop loss)  1.00     0.82      0.34
Text 1 (config)     0.82     1.00      0.31
Text 2 (account)    0.34     0.31      1.00
```

**How to read it:**
- **1.0** = Perfect similarity (text compared to itself)
- **0.82** = High similarity (Text 0 and Text 1 are very similar)
- **0.34** = Low similarity (Text 0 and Text 2 are different topics)

**Similarity Score Ranges:**
- **0.9-1.0** = Nearly identical meaning
- **0.7-0.9** = Very similar, same topic
- **0.5-0.7** = Somewhat related
- **0.3-0.5** = Different topics, some overlap
- **0.0-0.3** = Completely unrelated

---

### Response Structure (Reference Mode)

```json
{
  "results": [
    {
      "text": "Trading platform features",
      "text_preview": "Trading platform features",
      "embedding_dimensions": 1024,
      "similarity_to_reference": 0.87
    },
    {
      "text": "Account management",
      "text_preview": "Account management",
      "embedding_dimensions": 1024,
      "similarity_to_reference": 0.64
    },
    {
      "text": "Stop loss orders",
      "text_preview": "Stop loss orders",
      "embedding_dimensions": 1024,
      "similarity_to_reference": 0.52
    }
  ],
  "total_texts": 3,
  "processing_time_ms": 198.45,
  "embedding_model": "BAAI/bge-m3",
  "similarity_matrix": null
}
```

**How to interpret:**
- Each text has `similarity_to_reference` score
- Higher score = more similar to reference text
- Use this to find which text best matches your query

---

## Common Testing Workflows

### Workflow 1: New Document Upload Verification

**Goal:** Verify a newly uploaded document is retrievable

1. **Upload document** (use existing `/documents/upload` endpoint)
2. **Test retrieval:**
   ```json
   POST /debug/retrieval-test
   {
     "query": "content from my document",
     "similarity_threshold": 0.6,
     "top_k": 10,
     "return_scores": true,
     "return_metadata": true
   }
   ```
3. **Check response:**
   - Look for your document in results
   - Check similarity score (should be > 0.7)
   - Verify metadata has correct file_name

---

### Workflow 2: System Pre-Deployment Check

**Goal:** Ensure all components are ready for production

1. **Check overall health:**
   ```
   GET /health/detailed
   ```
2. **Verify response:**
   - `overall_status` should be "healthy"
   - All components should be "healthy"
   - No critical_failures

---

### Workflow 3: Similarity Threshold Tuning

**Goal:** Find optimal similarity threshold for your use case

1. **Test with HIGH threshold (0.9):**
   ```json
   POST /debug/retrieval-test
   {
     "query": "your test query",
     "similarity_threshold": 0.9,
     "top_k": 10,
     "return_scores": true
   }
   ```
   - Very strict - may return few or no results

2. **Test with MEDIUM threshold (0.7):**
   ```json
   {
     "query": "your test query",
     "similarity_threshold": 0.7,
     "top_k": 10
   }
   ```
   - Balanced - recommended default

3. **Test with LOW threshold (0.5):**
   ```json
   {
     "query": "your test query",
     "similarity_threshold": 0.5,
     "top_k": 10
   }
   ```
   - Permissive - returns more results but less relevant

4. **Analyze results:**
   - Check score distribution
   - Find threshold where relevant documents appear
   - Balance precision (relevant results) vs recall (number of results)

---

### Workflow 4: Query Enhancement Testing

**Goal:** See how the assistant enhances queries

1. **Test with short query:**
   ```json
   POST /debug/retrieval-test
   {
     "query": "stop loss",
     "similarity_threshold": 0.7,
     "top_k": 5,
     "return_scores": true
   }
   ```

2. **Compare in response:**
   - `original_query`: "stop loss"
   - `enhanced_query`: "How to set up and configure stop loss orders in the Finansia Hero trading platform..."

3. **Check results:**
   - Enhanced query should retrieve more relevant platform-specific documents

---

## Common Issues and Solutions

### Issue 1: "Connection refused" error

**Symptoms:**
```json
{
  "detail": "Connection refused at http://localhost:8000"
}
```

**Solution:**
1. Check if server is running: `python -m uvicorn src.backend.api.main:app --reload`
2. Verify port is 8000
3. Check firewall settings

---

### Issue 2: Zero results from retrieval test

**Symptoms:**
```json
{
  "total_results": 0,
  "results": []
}
```

**Solutions:**
1. **Lower similarity threshold:**
   ```json
   {
     "similarity_threshold": 0.5
   }
   ```

2. **Check if documents are indexed:**
   ```
   GET /documents/stats
   ```

3. **Verify query matches document content:**
   - Try broader query terms
   - Check document content with `/documents/` endpoint

---

### Issue 3: Qdrant unhealthy in health check

**Symptoms:**
```json
{
  "name": "Qdrant Vector Database",
  "status": "unhealthy",
  "error": "Connection refused"
}
```

**Solutions:**
1. Check `.env` file has correct values:
   ```
   QDRANT_URL=https://your-qdrant-url.com
   QDRANT_API_KEY=your_api_key
   ```

2. Verify Qdrant collection exists:
   - Log into Qdrant dashboard
   - Check collection name matches `QDRANT_COLLECTION_NAME`

3. Run bulk processing script if collection is empty:
   ```bash
   python process_documents.py
   ```

---

### Issue 4: Embeddings dimension is not 1024

**Symptoms:**
```json
{
  "embedding_dimensions": 384
}
```

**Solution:**
- Wrong embedding model is loaded
- Check `EMBED_MODEL` in `.env`:
  ```
  EMBED_MODEL=BAAI/bge-m3
  ```
- Restart server to reload configuration

---

### Issue 5: Slow retrieval (>2 seconds)

**Symptoms:**
```json
{
  "retrieval_latency_ms": 2500.45
}
```

**Solutions:**
1. **Large collection:** Consider optimizing Qdrant indexes
2. **Slow embeddings:** BGE-M3 runs on CPU by default
   - Consider GPU acceleration
   - Use smaller batch sizes
3. **Network latency:** If using cloud Qdrant, check connection speed

---

## Tips for Effective Testing

### 1. Save Requests as Collection
- Create a Postman Collection for all test endpoints
- Save common test scenarios
- Use variables for base URL

### 2. Use Environment Variables
- Set `{{base_url}}` = `http://localhost:8000`
- Easy to switch between dev/staging/prod

### 3. Document Expected Results
- Add descriptions to each saved request
- Note expected similarity scores
- Track threshold tuning results

### 4. Automate with Postman Tests
Add test scripts to verify responses:

```javascript
// Test for successful retrieval
pm.test("Retrieval successful", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.total_results).to.be.above(0);
});

// Test similarity scores
pm.test("Similarity scores are reasonable", function () {
    var jsonData = pm.response.json();
    jsonData.results.forEach(function(result) {
        pm.expect(result.score).to.be.above(0.5);
    });
});
```

---

## Quick Reference

### All Endpoints Summary

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `/debug/retrieval-test` | POST | Test RAG retrieval | query, similarity_threshold, top_k |
| `/health/detailed` | GET | System health check | None (no parameters) |
| `/debug/embedding-test` | POST | Test embeddings | texts, reference_text, compute_similarities |

---

## Next Steps

After testing these endpoints, consider:

1. **Set up monitoring:**
   - Schedule regular health checks
   - Alert on unhealthy status
   - Track retrieval performance over time

2. **Optimize retrieval:**
   - Use retrieval test to tune similarity threshold
   - Test different query formulations
   - Analyze which documents are frequently retrieved

3. **Document baselines:**
   - Record typical similarity scores for good matches
   - Note acceptable latency ranges
   - Track system capacity limits

4. **Build dashboards:**
   - Visualize health check data
   - Graph retrieval performance
   - Monitor embedding quality trends

---

## Support

If you encounter issues not covered here:
1. Check server logs for detailed error messages
2. Verify `.env` configuration
3. Review FastAPI docs at http://localhost:8000/docs
4. Check system resource usage (CPU, memory)

---

**Last Updated:** 2025-10-01
**API Version:** 2.0.0
**FastAPI Documentation:** http://localhost:8000/docs
