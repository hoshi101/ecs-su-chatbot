# API Demo Checklist

Use this checklist before testing the chatbot in front of an evaluator.

## 1. Start backend

```bash
.venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload
```

Open:

- Swagger UI: http://localhost:8001/docs
- Health: http://localhost:8001/health

## 2. Run automated checks

```bash
.venv/bin/python -m pytest tests/unit -q
.venv/bin/python scripts/preflight_check.py
```

Expected result:

- Unit tests pass.
- Health returns `status=ok`.
- Detailed health is `healthy` or `degraded`.
- Retrieval returns at least one source.
- Chat returns a non-empty answer with trace events and sources.

## 3. Manual API smoke tests

### Health

```bash
curl http://127.0.0.1:8001/health
```

### Detailed health

```bash
curl http://127.0.0.1:8001/health/detailed
```

### Retrieval debug

```bash
curl -X POST http://127.0.0.1:8001/debug/retrieval-test \
  -H "Content-Type: application/json" \
  -d '{"query":"เบอร์ติดต่อภาควิชาวิศวกรรมไฟฟ้าคืออะไร","top_k":3,"similarity_threshold":0.7}'
```

### Chat

```bash
curl -X POST http://127.0.0.1:8001/chat/ \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo","query":"เบอร์ติดต่อภาควิชาวิศวกรรมไฟฟ้าคืออะไร","enable_web_search":true,"force_web_search":false,"similarity_threshold":0.7}'
```

## 4. Demo order

1. Show `/health` to prove the API is running.
2. Show `/health/detailed` to prove Qdrant, embeddings, LLM, and document processor are connected.
3. Show `/debug/retrieval-test` to prove the answer is grounded in knowledge-base documents.
4. Show `/chat/` to prove the real chatbot workflow returns answer, trace events, and sources.
5. Open the frontend only after API checks pass.
