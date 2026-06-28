# Report Update Recommendations

Reviewed file: `docs/reports/สหกิจ_report_v2_0.pdf`  
Reviewed on: 2026-06-28

## Current Report Status

The report already covers the core project story well:

- Objective and scope of the AI Assistant Chatbot
- RAG, LLM, vector database, FastAPI, Streamlit, and Tavily concepts
- Data preparation from official documents and websites
- API-based testing with 50 sample questions
- Evaluation criteria for API success, answer relevance, expected keywords, source correctness, response time, and out-of-scope handling
- Summary with average response time `3.42 seconds`
- Limitations around prototype status, public-source data, and lack of real-user evaluation

## Recommended Additions

| Report Area | Add | Why |
|---|---|---|
| Section 3.1.3 System Development | Mention routing/precheck layer and response templates | Explains why greetings/contact/out-of-scope can respond quickly and consistently |
| Section 3.1.4 Testing | Add Bruno API testing workflow | Shows the project has a repeatable API test collection, not only ad hoc tests |
| Section 4.2 Testing Results | Add a small table for Bruno coverage | Current report says 50 cases; Bruno now adds 28 request-level demo checks |
| Section 4.2 Testing Results | Add usage tracking evidence | Shows basic monitoring/readiness for demo and future operation |
| Section 4.2 or 5 Analysis | Add current-public-information guardrail | Explains why TCAS/latest admission questions prefer official website search |
| Section 5 Analysis | Add source/trace observability | Explains trace events, source count, route, and relevance score as transparency tools |
| Section 6 Summary | Add final frontend validation sentence | Completes the story from API testing to real user-facing demo |

## Suggested Text

### Add to System Development

```text
ระบบมีชั้นตรวจสอบคำถามเบื้องต้น (query precheck/routing) เพื่อแยกประเภทคำถาม เช่น คำทักทาย ข้อมูลติดต่อ คำถามนอกขอบเขต และคำถามเชิงข้อมูลของภาควิชา โดยคำถามบางประเภทสามารถตอบจาก template ที่กำหนดไว้ล่วงหน้าได้ทันที ส่วนคำถามเชิงข้อมูลจะเข้าสู่กระบวนการค้นคืนข้อมูลจากฐานความรู้หรือค้นจากเว็บไซต์ทางการเมื่อจำเป็น แนวทางนี้ช่วยลดเวลาในการตอบคำถามทั่วไปและลดความเสี่ยงในการสร้างคำตอบที่ไม่มีแหล่งอ้างอิง
```

### Add to Testing Section

```text
นอกจากการทดสอบผ่าน API โดยตรงแล้ว ได้จัดเตรียม Bruno Collection สำหรับใช้ทดสอบ endpoint สำคัญของระบบอย่างเป็นลำดับ ได้แก่ Health, Config, Routing, Domain, Debug และ General Query รวม 28 request เพื่อให้สามารถทดสอบซ้ำก่อนการสาธิตได้อย่างเป็นระบบ โดยชุดทดสอบดังกล่าวเน้นตรวจสอบ status code, routing behavior, response shape, source attribution และ key facts ที่สำคัญของคำถามตัวอย่าง
```

### Add to Testing Results

```text
ระบบได้เพิ่มการบันทึก usage tracking แบบ lightweight ในรูปแบบ JSONL สำหรับ endpoint /chat/ โดยเก็บเฉพาะ metadata ที่จำเป็น เช่น เวลาใช้งาน session id, route, intent, model, latency, จำนวนแหล่งอ้างอิง และสถานะ success/error ข้อมูลดังกล่าวช่วยให้สามารถตรวจสอบภาพรวมการใช้งานและนำไปประกอบการนำเสนอผลการทดสอบได้ โดยไม่เก็บ API key หรือคำตอบฉบับเต็มของระบบ
```

### Add to Analysis

```text
สำหรับคำถามที่เกี่ยวข้องกับข้อมูลปัจจุบัน เช่น TCAS รอบล่าสุด คะแนนรับสมัคร หรือกำหนดการรับสมัคร ระบบถูกกำหนดให้ให้ความสำคัญกับการค้นจากเว็บไซต์ทางการมากกว่าการตอบจากข้อมูลเดิมในฐานความรู้ เพื่อหลีกเลี่ยงการตอบข้อมูลที่อาจล้าสมัย หากไม่พบข้อมูลจากแหล่งทางการ ระบบควรชี้แจงข้อจำกัดแทนการคาดเดา
```

### Add to Conclusion

```text
ก่อนการสาธิตระบบ ได้จัดเตรียมการทดสอบทั้งระดับ API และ frontend โดย API ใช้ Bruno Collection สำหรับตรวจสอบ routing, RAG, debug endpoint และคำถามทั่วไป ส่วน frontend ใช้ตรวจสอบประสบการณ์ใช้งานจริง เช่น การแสดงคำตอบ แหล่งอ้างอิง trace events และการทำงานของ session เพื่อให้มั่นใจว่าระบบพร้อมสำหรับการนำเสนอในรูปแบบผู้ใช้งานจริง
```

## Evidence File for Presentation

Use this file when you need a compact readiness artifact:

```text
docs/reports/demo_readiness_evidence.md
```

It summarizes automated tests, Bruno coverage, usage tracking, readiness improvements, and the final frontend checklist.
