# API 50-Question Test Evidence

## Summary

| Metric | Value |
|---|---:|
| Generated at | 2026-06-29 01:26:47 +07 |
| Base URL | http://127.0.0.1:8001 |
| Transport | testclient |
| Total questions | 50 |
| Answered successfully | 50 |
| Success rate | 100.00% |
| Average latency seconds | 6.44 |
| Median latency seconds | 6.55 |
| Min latency seconds | 0.01 |
| Max latency seconds | 11.02 |
| Provider | openai |
| Model | gpt-4.1 |

## Notes

- All 50 successful cases returned HTTP 200 with a non-empty API response.
- Latency is measured client-side through FastAPI TestClient with rate limiting disabled for evaluation.
- Keyword matching is supporting evidence only; PASS/FAIL in this file means the API returned a usable response.
- Open the CSV file directly in Excel, LibreOffice Calc, or Google Sheets for presentation.
