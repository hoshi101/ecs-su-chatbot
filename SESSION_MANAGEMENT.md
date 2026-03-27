# Session Management

## Project

- Current working title: `AI Assistant/Support Chatbot for Department of Electrical Engineering`
- Target domain:
  - `สาขาวิชาวิศวกรรมอิเล็กทรอนิกส์และระบบคอมพิวเตอร์`
  - `วิศวกรรมไฟฟ้า`
  - `Electronic and Computer System Engineering`
- Deadline target:
  - First usable delivery by `2026-03-26`
  - Latest acceptable delivery by `2026-03-27`

## Agreed Scope

- Keep current architecture as base instead of rebuilding from scratch.
- Keep `Streamlit` for demo UI.
- Support Thai and English, with Thai as the default language.
- Tone should be friendly and staff-like.
- Keep `Web Search`, but use it as a constrained fallback instead of the primary source.
- Answers must prioritize department documents and must not guess.
- Sensitive or unsupported questions should be declined clearly.
- Knowledge base updates can be handled through backend/developer workflow.

## Demo Priorities

1. Answer questions about curriculum and courses.
2. Answer questions about lecturers and staff.
3. Answer questions about rules, regulations, and department information.
4. Provide core chatbot functionality reliably for a live demo.

## Current Local Data Inventory

Current files found in `data/`:

- `data/มคอ.2.pdf`
- `data/รายละเอียดของหลักสูตร_2565.pdf`

Status:

- The current local knowledge base is still very small.
- More source documents should be added before final ingestion and testing.

## Confirmed External Sources

- Department website: `https://ee-eng.su.ac.th/`
- Faculty website: `https://eng2.su.ac.th/index.php`

Useful pages identified:

- Department about/contact page
- Department lecturer page
- Department support staff page
- Department curriculum pages
- Faculty department page for electrical engineering

## Confirmed Contact Information

From the user and official pages:

- Phone: `034-219364-66 ext. 25520`
- Phone: `089-979-7911`
- Phone/Fax: `034-241971`
- Facebook: `Department of Electrical Engineering - Silpakorn University`

Additional contact details found on official pages:

- Address: `เลขที่ 6 ถ.ราชมรรคาใน ต.พระปฐมเจดีย์ อ.เมือง จ.นครปฐม 73000`

## Website Findings

The following information appears to be available from the official sites and should be considered for ingestion:

- Department history/about information
- Curriculum and degree program descriptions
- Lecturer names, roles, and emails
- Support staff names, roles, and emails
- Contact information
- Internship / cooperative education pages
- Project and research pages

Examples already verified during discovery:

- Lecturer page contains names, roles, and emails.
- Support staff page contains names, roles, and emails.
- Contact page contains address and phone numbers.
- Department/faculty pages contain summary information about programs and history.

## Recommended Additional Sources To Collect

- Curriculum and study-plan PDFs for all active programs
- Course catalog / syllabus / prerequisite documents
- Internship and cooperative education guides
- Department regulations or student handbook documents
- Faculty/department staff directory pages exported to PDF or text
- Admission pages if the chatbot should answer applicant questions
- Research/project pages if the chatbot should answer broader department questions

## Technical Adaptation Plan

### 1. Rebrand and re-scope the assistant

- Remove Finansia Hero identity from prompts, config, API description, and UI wording.
- Replace domain language with department-specific assistant behavior.

### 2. Adjust agent behavior

- Make RAG the default path.
- Keep web search as a guarded fallback limited to trusted domains.
- Add stronger refusal behavior for unsupported or sensitive requests.
- Improve source-aware answer generation.

### 3. Rebuild the knowledge base

- Organize incoming documents by category:
  - `academic`
  - `faculty`
  - `policy`
  - `facilities`
  - `student_services`
- Improve metadata quality so answers can cite source names more clearly.

### 4. Update the demo UI

- Keep Streamlit.
- Change project name and copywriting.
- Default to Thai-friendly UX.
- Preserve source display for testing, but improve clarity where possible.

### 5. Improve observability

- Add practical logging around:
  - environment/config loading
  - retrieval
  - web search fallback
  - model/API failures

## Immediate Next Steps

1. Run `python scripts/scrape_department_sources.py` to collect official web sources.
2. Review outputs in `data/web/clean/` and add any missing official documents.
3. Inspect and update config, prompts, and UI branding.
4. Review vectorstore and retrieval code for metadata/citation improvements.
5. Run ingestion and validate retrieval quality with representative questions.
6. Refine answer style and fallback behavior.

## Open Items

- Confirm final project display name for UI.
- Confirm whether applicant/admission questions are in scope.
- Confirm whether web search should be enabled in the final demo by default.
- Add more official source files into `data/`.

## Working Notes

- This file should be updated after each substantial work session.
- It is intended to track scope, source coverage, implementation status, and open risks.

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
  - raw HTML, cleaned Markdown/JSON, and downloaded PDFs were saved under `data/web/`
