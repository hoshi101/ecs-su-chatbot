# Repository Guidelines

## Project Structure & Module Organization
Source code lives in `src/`. Backend API and agent logic are under `src/backend/` (`api/`, `core/`, `services/`, `utils/`). The Streamlit frontend is under `src/frontend/` (`api/`, `components/`, `config/`, `state/`). Utility scripts live in `scripts/`, tests in `tests/` (`unit/`, `integration/`, `migration/`), API collections in `bruno/ecs-chatbot/`, and project documentation in `docs/`. Knowledge-base inputs and scraped content are stored in `data/`.

## Build, Test, and Development Commands
Install dependencies:
```bash
pip install -r requirements.txt
```
Run the backend locally:
```bash
.venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload
```
Run the frontend:
```bash
.venv/bin/python scripts/run_frontend.py
```
Populate or refresh the vector store:
```bash
.venv/bin/python scripts/process_documents.py
```
Run tests:
```bash
.venv/bin/python -m pytest
.venv/bin/python -m pytest tests/unit
.venv/bin/python -m pytest tests/integration -v
```

## Coding Style & Naming Conventions
Use Python 3.10+ with 4-space indentation and PEP 8 naming. Prefer `snake_case` for functions, variables, and modules; `PascalCase` for Pydantic models and classes. Keep API schemas near `src/backend/api/main.py`, shared configuration in `src/backend/core/config.py`, and UI-specific logic inside `src/frontend/components/`. Favor small, direct functions over broad utility wrappers.

## Testing Guidelines
Pytest is the test framework. Name files `test_*.py` and keep new tests close to the affected layer: routing logic in `tests/unit/`, endpoint behavior in `tests/integration/`. When changing chat behavior, verify both automated tests and the Bruno collection in `bruno/ecs-chatbot/`. For regression work, add at least one failing input case before changing routing rules.

## Commit & Pull Request Guidelines
Follow the repository’s short imperative commit style, for example: `Refine contact and out-of-scope shortcuts` or `Add Bruno API test collection`. Keep commits scoped to one concern. PRs should include: a short summary, affected paths, test evidence (`pytest`, Bruno, or manual API checks), and screenshots only for frontend-visible changes.

## Security & Configuration Tips
Never commit `.env` or live API keys. Start from `.env.example`, and prefer OpenAI/Gemini model defaults defined in config rather than hardcoding them in tests. Keep Qdrant and external API credentials local to your environment.
