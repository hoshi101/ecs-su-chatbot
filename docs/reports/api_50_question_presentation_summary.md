# API Testing Summary for Presentation

Generated: 2026-06-29 01:26 ICT

## Result Statement

จากชุดทดสอบ API จำนวน 50 คำถาม ระบบสามารถตอบกลับผ่าน API ได้ครบ 50 คำถาม คิดเป็นอัตราสำเร็จ 100.00% และมีเวลาเฉลี่ย 6.44 วินาทีในสภาพแวดล้อมทดสอบแบบ FastAPI TestClient โดยปิด rate limit เฉพาะการประเมินผล

## Summary Table

| Metric | Result |
|---|---:|
| Total test questions | 50 |
| Answered successfully | 50 |
| Success rate | 100.00% |
| Average latency | 6.44 seconds |
| Median latency | 6.55 seconds |
| Minimum latency | 0.01 seconds |
| Maximum latency | 11.02 seconds |
| API transport | FastAPI TestClient |
| Rate limit during evaluation | Disabled |
| LLM provider/model | OpenAI / gpt-4.1 |

## Evidence Files

| File | Purpose |
|---|---|
| `docs/reports/api_50_question_presentation_table.csv` | Recommended table for presentation; concise per-question status and latency |
| `docs/reports/api_50_question_results_latest.csv` | Raw per-question API result with response preview and keyword matching details |
| `docs/reports/api_50_question_summary_latest.md` | Machine-generated summary from the latest run |
| `docs/reports/department_chatbot_test_questions.csv` | Source list of the 50 API test questions |

## Report Note

หากในรายงานยังใช้ข้อความว่าเวลาเฉลี่ยประมาณ 3.42 วินาที ให้ถือว่าเป็นค่าจากรอบทดสอบเดิมหรือสภาพแวดล้อมเดิม ส่วนค่าที่วัดล่าสุดหลังเพิ่ม RAG/source handling และทดสอบครบ 50 คำถามคือ 6.44 วินาที ค่าใหม่นี้สมเหตุสมผลกว่าเพราะระบบมีการเรียก retrieval, source attribution, LLM judgement และ answer generation หลายขั้นตอน
