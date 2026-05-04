# Session Management

## Project

- Current working title: `AI Assistant/Support Chatbot for Department of Electrical Engineering`
- Target domain:
  - `สาขาวิชาวิศวกรรมอิเล็กทรอนิกส์และระบบคอมพิวเตอร์`
  - `วิศวกรรมไฟฟ้า`
  - `Electronic and Computer System Engineering`
- Primary demo stack:
  - `Streamlit` frontend
  - `FastAPI` backend
  - `LangGraph` agent workflow
  - `Qdrant` vector store

## Agreed Scope

- Keep the current architecture as the working base.
- Thai is the default language, with bilingual support where needed.
- Answers must prioritize official local data before any fallback path.
- The chatbot should answer department, curriculum, lecturer, staff, and contact questions.
- Unsupported or non-department questions should be declined clearly.

## Current Status

- Department-domain rebrand has already been applied to the codebase.
- Department/faculty web scraping outputs already exist under `data/web/`.
- The project already has session handling on the frontend side via `src/frontend/state/session_manager.py`.
- The main remaining operational blocker is still ingestion/runtime validation against the configured `Qdrant` endpoint.
- Test question assets have now been reorganized into a maintainable structure for repeated validation.

## Completed Work

- Replaced the old single-purpose planning list with a tracked completion-oriented planning file.
- Created canonical categorized question sets under `docs/testing/question_sets/`.
- Added one master CSV for full regression-style testing across all categories.
- Normalized question coverage around five categories:
  - general
  - department info
  - lecturer
  - contact
  - out of scope
- Verified that the new question sets reference real sources already present in the repo.

## Canonical Data And Test Assets

- Canonical planning file: `PLANNING_MANAGEMENT.md`
- Canonical session log: `SESSION_MANAGEMENT.md`
- Canonical test question location: `docs/testing/question_sets/`
- Legacy question file retained for history only: `docs/reports/department_chatbot_test_questions.csv`

## Source Coverage Used For Testing

- Department contact:
  - `data/web/clean/department_contact.md`
  - `data/web/clean/faculty_department_overview.md`
- Department overview and program information:
  - `data/web/clean/faculty_department_overview.md`
  - `data/web/clean/program_ecs.md`
  - `data/web/clean/program_electrical_communications.md`
  - `data/web/clean/program_master_ece.md`
- Lecturer information:
  - `data/web/clean/department_lecturers.md`
  - `data/web/clean/staff_details/`
- Support staff information:
  - `data/web/clean/department_support_staff.md`

## Current Focus

1. Use the new categorized question sets to run actual chatbot validation.
2. Confirm routing behavior for `answer`, `rag`, and `end` cases.
3. Re-run ingestion/runtime validation once the `Qdrant` configuration issue is resolved.
4. Summarize response quality, coverage, and failure cases for the next report/testing pass.

## Next Validation Step

- Run the chatbot against `docs/testing/question_sets/master_department_chatbot_test_questions.csv`
- Check:
  - retrieval coverage from local sources
  - accuracy of lecturer/contact answers
  - refusal quality for out-of-scope questions
  - response consistency across repeated sessions

## Working Notes

- This file should be updated after each substantial work session.
- Before creating new test assets, check `docs/testing/question_sets/` first.
- Before starting new planning work, check `PLANNING_MANAGEMENT.md` first.

### 2026-03-27

- Added targeted scraper script: `scripts/scrape_department_sources.py`
- Added scraping usage guide: `docs/guides/WEB_SCRAPING_GUIDE.md`
- Updated `README.md` with scraping step before ingestion
- Added `beautifulsoup4` to `requirements.txt`
- Current scraper targets:
  - department contact page
  - lecturer directory
  - support staff directory
  - program pages
  - faculty department overview page
- Scraper validated against live official sites
- Current scrape result:
  - 7 sources succeeded
  - 0 sources failed
- Added lecturer detail scraping for all academic staff pages via `StaffDetail.aspx`
- Generated per-lecturer files under:
  - `data/web/raw/staff_details/`
  - `data/web/clean/staff_details/`
- Updated chat agent/domain behavior:
  - rebranded assistant identity to department domain
  - changed routing and answer prompts away from trading platform behavior
  - added source-aware RAG trace payloads for frontend display
- Updated ingestion workflow to skip raw scrape artifacts and prefer curated content
- Updated Streamlit UI copy for department demo usage
- Runtime validation:
  - BGE-M3 model download/load succeeded when run with network access
  - Qdrant connection reached the configured host
  - Collection create/access currently fails with `404 page not found`, so ingestion is blocked on Qdrant configuration

### 2026-04-22

- Rebuilt `PLANNING_MANAGEMENT.md` into a completion-tracking format with explicit done markers
- Created `docs/testing/question_sets/` as the canonical location for chatbot validation questions
- Added categorized CSV files:
  - `general_questions.csv`
  - `department_info_questions.csv`
  - `lecturer_questions.csv`
  - `contact_questions.csv`
  - `out_of_scope_questions.csv`
  - `master_department_chatbot_test_questions.csv`
- New master test set now covers 70 questions total across greeting/scope, department data, lecturers, contact details, and out-of-scope refusal cases
- Legacy file `docs/reports/department_chatbot_test_questions.csv` is now treated as historical only and should not be extended further

### 2026-04-23

- Repaired `.venv` after finding that `.venv/bin/python` and `.venv/bin/python3` were empty files and recreated the virtual environment
- Installed project dependencies into `.venv` and confirmed backend imports can run in the intended environment
- Added centralized backend logging with console + rotating file output
- New backend log file path: `logs/backend.log`
- Verified `GET /health/detailed` with network access:
  - `BGE-M3 Embeddings`: healthy
  - `Google Gemini API`: healthy
  - `Tavily Web Search`: healthy
  - `DocumentProcessor`: healthy
  - `Qdrant`: initially degraded because collection `ECS-Chatbot-ProjectTesting` did not exist
- Verified the new Qdrant API key can connect successfully to the configured Qdrant cloud instance
- Ran smoke retrieval and chat tests:
  - retrieval failed before ingestion because the Qdrant collection was missing
  - chat endpoint still returned a fallback answer, but not from real retrieval
- Started ingestion with `scripts/process_documents.py`
  - created collection `ECS-Chatbot-ProjectTesting`
  - ingestion began uploading document chunks to Qdrant successfully
  - confirmed collection status turned `green`
  - confirmed points started entering the collection during upload
- Residual issue during ingestion:
  - some `.json` files were skipped because Python package `jq` is not installed in `.venv`
  - markdown and PDF sources were still processed, so ingestion is not fully blocked
