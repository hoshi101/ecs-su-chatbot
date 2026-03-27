# Web Scraping Guide

## Purpose

This project should not rely on runtime web search for every department question.
Instead, official department and faculty pages should be collected in advance and
stored in the local knowledge base for RAG retrieval.

The scraper in this repository is designed for that workflow.

## Script

Run:

```bash
python scripts/scrape_department_sources.py
```

## Output Structure

The script writes data into `data/web/`:

- `data/web/raw/`
  - Raw HTML for debugging and later re-processing
- `data/web/clean/`
  - Cleaned Markdown and JSON files ready for ingestion
- `data/web/downloads/`
  - Downloaded PDFs discovered from program/faculty pages
- `data/web/index.json`
  - Manifest of successful scrapes, failures, and output locations

## Current Target Sources

- Department contact page
- Department academic staff page
- Department support staff page
- Department program pages
- Faculty department overview page

## Why This Approach

- Faster chatbot responses because most answers come from the vector database
- Lower dependence on live website availability
- Better source control because scraped outputs can be inspected
- Easier debugging when a retrieved answer looks wrong

## Recommended Workflow

1. Run the scraper.
2. Review files in `data/web/clean/`.
3. Add manual documents or corrected notes if any page was parsed poorly.
4. Run document ingestion.
5. Test representative queries against the updated knowledge base.

## Notes

- Runtime web search can still remain as a fallback for missing or highly dynamic information.
- If a page layout changes, update the parser in `scripts/scrape_department_sources.py`.
