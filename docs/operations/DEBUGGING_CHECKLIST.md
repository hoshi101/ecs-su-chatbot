# ECS Chatbot Debugging Checklist

## Main places to inspect

- Backend log file: `logs/backend.log`
- Basic health: `GET /health`
- Detailed health: `GET /health/detailed`
- Retrieval debug: `POST /debug/retrieval-test`
- Preflight script: `./.venv/bin/python scripts/preflight_check.py`

## When chat looks wrong

1. Check backend is alive.
   - `curl http://127.0.0.1:8000/health`
2. Check system dependencies.
   - `curl http://127.0.0.1:8000/health/detailed`
3. Check whether retrieval is finding the expected documents.
   - `./.venv/bin/python scripts/preflight_check.py`
   - or call `POST /debug/retrieval-test` with the user question
4. Open `logs/backend.log` and inspect:
   - router decision
   - streamed trace events
   - retrieval counts
   - exceptions or stack traces
5. In the frontend, inspect:
   - `Assistant Workflow Trace`
   - `Source Documents`

## How to read `logs/backend.log`

- `Starting agent stream`
  - new chat request started
- `Streamed event`
  - one workflow step was emitted to the frontend
- `Agent stream completed`
  - response completed successfully
- `Retrieval test started/completed`
  - debug retrieval endpoint activity
- `Uploading batch`
  - Qdrant ingestion is in progress

## Document ingestion behavior

- Default behavior of `scripts/process_documents.py`
  - skips files that are already indexed in Qdrant
- Reprocess everything only when needed
  - `./.venv/bin/python scripts/process_documents.py --reprocess-existing`

## Expected operator flow before manual testing

1. Start backend
2. Run preflight
3. Open frontend
4. Ask one contact question, one lecturer question, and one curriculum question
5. Confirm both trace and source panels are populated
