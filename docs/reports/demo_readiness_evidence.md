# Demo Readiness Evidence

Generated: 2026-06-28 23:15 ICT  
Branch: `pretest/demo-readiness`  
Commit: `7d01297`

## Summary

The ECS chatbot project is ready for the final manual frontend demo test after running automated unit checks, API test preparation, and usage tracking verification. The system has test coverage for routing, response templates, query guardrails, usage tracking, and Bruno API workflows.

## Automated Verification

| Check | Result | Evidence |
|---|---:|---|
| Unit tests | Pass | `60 passed, 4 warnings` |
| Python syntax compile | Pass | `py_compile` passed for backend API, agent, templates, usage tracking, and run scripts |
| Backend preflight | Pass | Health, detailed health (`degraded` because Gemini quota is exhausted), retrieval, chat response, workflow trace, and source attribution passed |
| Frontend smoke check | Pass | Streamlit returned HTTP `200` at `http://127.0.0.1:8501` |
| Usage tracking summary script | Pass | `scripts/summarize_usage.py` runs successfully |
| API 50-question evidence | Pass | `50/50` answered successfully, average latency `6.44s` in FastAPI TestClient evaluation |
| Working tree before evidence generation | Clean | Branch was clean before evidence files were added |

Commands used:

```bash
.venv/bin/python -m pytest tests/unit -q
.venv/bin/python -m py_compile src/backend/api/main.py src/backend/core/agent.py src/backend/core/response_templates.py src/backend/utils/usage_tracking.py scripts/summarize_usage.py scripts/run_backend.py scripts/run_frontend.py
.venv/bin/python scripts/preflight_check.py
.venv/bin/python scripts/summarize_usage.py
```

Backend preflight result:

| Check | Result |
|---|---|
| Health | Pass |
| Detailed health | Pass, `overall_status=degraded` because Gemini quota is exhausted; OpenAI remains healthy |
| Retrieval test | Pass, `total_results=3` |
| Chat response | Pass, `response_length=554` |
| Workflow trace | Pass, `trace_events=3` |
| Source attribution | Pass, `sources=8` |

## Bruno API Test Coverage

The Bruno collection is prepared for API-level demo testing with 28 HTTP requests.

| Folder | Cases | Purpose |
|---|---:|---|
| `00 Health` | 2 | Basic and detailed system health |
| `01 Config` | 1 | LLM provider/model options |
| `02 Routing` | 11 | Greeting, contact, out-of-scope, and mixed-intent routing |
| `03 Domain` | 5 | In-domain RAG/web behavior and edge domain questions |
| `04 Debug` | 2 | Retrieval and embedding inspection |
| `05 General Query` | 7 | User-like demo questions: knowledge inventory, credits, lecturer research, admission web route |

Recommended Bruno order:

1. `00 Health`
2. `01 Config`
3. `02 Routing`
4. `03 Domain`
5. `05 General Query`
6. `04 Debug` only when retrieval/embedding details need inspection

## Usage Tracking Verification

Usage tracking writes chat metadata to:

```bash
logs/usage_events.jsonl
```

The log is intentionally stored under `logs/`, which is ignored by git. It is useful for local demo/report evidence but should not be committed.

Sample verification was run through `/chat/` with 4 shortcut requests plus 1 backend preflight chat request:

| Metric | Value |
|---|---:|
| Total sample chat requests | 5 |
| Success | 5 |
| Errors | 0 |
| Average latency | 1682.58 ms |
| Max latency | 8390.91 ms |
| Average source count | 1.00 |

Route distribution:

| Route | Count |
|---|---:|
| `end` | 4 |
| `rag` | 1 |

Intent distribution:

| Intent | Count |
|---|---:|
| `greeting` | 1 |
| `contact` | 1 |
| `capability` | 1 |
| `out_of_scope` | 1 |
| `domain_question` | 1 |

Note: These are sample tracking checks for the logging mechanism, not real user analytics. Real usage numbers will accumulate when the backend receives actual `/chat/` requests during Bruno or frontend testing.

To show updated usage statistics:

```bash
.venv/bin/python scripts/summarize_usage.py
```

## Key Readiness Improvements

| Area | Improvement |
|---|---|
| Response templates | Centralized greeting/contact/out-of-scope/capability templates for easier future edits |
| Contact answers | More focused contact responses, such as phone-only or Facebook-only answers |
| Mixed language handling | Thai/English language detection improved for mixed queries |
| Domain search evidence | Web relevance score is carried into `sources[].relevance_score` when available |
| Current public information | Admission/TCAS/latest score questions prefer official website search |
| Answer guardrails | Exact curriculum/course/lecturer details should only be answered when supported by retrieved context |
| API testing | Added Bruno `05 General Query` for realistic demo questions |
| Usage monitoring | Added lightweight JSONL usage tracking and summary script |
| Frontend session behavior | Fixed stale LangGraph checkpoint query state so each frontend message uses the current query |
| Answer grounding | Reduced over-abstention by answering supported context first and marking only specific missing details as unavailable |
| Retrieval breadth | Increased RAG answer context and added local priority sources for electrical communications and master's program queries |
| Staff detail retrieval | Prioritizes scraped lecturer detail pages for lecturer name, email, research, and expertise questions |

## Final Frontend Demo Checklist

Use the frontend after API/Bruno checks pass. The frontend test should confirm the full user experience, not only backend correctness.

| Step | What to Check | Expected Result |
|---|---|---|
| Open frontend | Page loads without Streamlit error | Chat UI is visible |
| Greeting | `สวัสดีครับ` | Fast template response, no sources required |
| Contact | `ขอเบอร์โทรภาควิชา` | Concise phone/contact answer |
| Knowledge inventory | `น้องไฟฟ้ามีข้อมูลอะไรบ้างในระบบ` | Explains available department/curriculum/staff knowledge |
| Stable curriculum | `หลักสูตร ECS ปี 2565 รวมกี่หน่วยกิต` | Mentions 147 credits with source evidence |
| Lecturer info | `ประธานหลักสูตร ECS คือใคร` | Answers from lecturer/staff source |
| Current admission | `TCAS รอบล่าสุดใช้คะแนนอะไรบ้าง` | Uses official website search or clearly says current official detail was not found |
| Out-of-scope | `วันนี้ฝนจะตกไหม` | Politely rejects or redirects to department scope |
| Trace/source panel | Inspect details after response | Route, trace events, and sources are visible when available |
| Usage tracking | Run summary after UI test | Request count increases in `logs/usage_events.jsonl` |

## Demo Commands

Backend:

```bash
.venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload
```

Preflight:

```bash
.venv/bin/python scripts/preflight_check.py
```

Frontend:

```bash
.venv/bin/python scripts/run_frontend.py
```

Usage summary:

```bash
.venv/bin/python scripts/summarize_usage.py
```
