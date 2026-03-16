# Q&A Preparation
## AI Assistant Chatbot for Finansia Hero

---

## 📋 Background Notes — ความซับซ้อนของเอกสาร (สำหรับผู้นำเสนอ)

ใช้ตอบกรรมการเมื่อถามว่า "เอกสารซับซ้อนยังไง?"

- **PDF ขนาดใหญ่** (4.7–18 MB ต่อไฟล์, รวม ~59 MB) — มี screenshot, ตาราง, รูปภาพจำนวนมาก PyPDFLoader สกัดได้แค่ text สูญเสีย visual context ไป
- **ตารางเปรียบเทียบฟีเจอร์** — เช่น ตารางประเภทคำสั่งซื้อขาย (Market Order, Limit Order, Stop Loss) ที่มีตัวเลขและคำอธิบายปนกัน
- **Infographic Step-by-Step** — เช่น ขั้นตอนการเปิดบัญชีที่เป็นรูปพร้อมลูกศร พอ extract เป็น text ข้อมูลหายหมด
- **Bilingual แบบสลับ** — ชื่อ feature เป็นอังกฤษ ("HERO Strong Trend") แต่คำอธิบายเป็นไทย ปนศัพท์เทคนิค ("SMA 200") กลางประโยค
- **JSON ซ้อนหลายชั้น** — เมนูนำทาง 5 ระดับที่ต้อง flatten ก่อน chunk จึงสูญเสียโครงสร้าง

**ประโยคสรุปสำหรับตอบกรรมการ:**
> "เอกสารจริงของ Finansia Hero เป็น rich media document ที่มีตาราง infographic และ screenshot ซ้อนกัน เมื่อ extract เป็น text visual context หายไปหมด ระบบ RAG จึงต้องทำงานกับข้อมูลที่ degraded ซึ่งเป็นสาเหตุที่ต้องใช้ Query Enhancement และ Web Search Fallback เข้ามาช่วย"

---

## ❓ Q&A — คำถามที่กรรมการอาจถาม

---

### Q1 — Why use RAG instead of fine-tuning the LLM directly?

**English:**
Fine-tuning requires large datasets, high cost, and must be repeated every time documentation changes. RAG updates the knowledge base instantly by adding documents to Qdrant — no retraining needed. Most importantly, RAG grounds responses in real documentation, directly reducing hallucination, which is critical in financial applications.

**ภาษาไทย:**
Fine-tuning ต้องใช้ข้อมูลจำนวนมาก ค่าใช้จ่ายสูง และต้องทำใหม่ทุกครั้งที่เอกสารเปลี่ยน RAG อัปเดตฐานความรู้ได้ทันทีโดยไม่ต้อง retrain และที่สำคัญกว่าคือ RAG บังคับให้คำตอบอ้างอิงจากเอกสารจริง ลด Hallucination ได้โดยตรง ซึ่งในโดเมนการเงินสิ่งนี้สำคัญมาก

---

### Q2 — Why choose Gemini over GPT-4 or Claude?

**English:**
Gemini 2.5 Flash is approximately 10x cheaper per token than GPT-4, supports Thai natively, and provides structured output which the Router Node needs for routing decisions. It delivers the right balance of capability and cost for this use case.

**ภาษาไทย:**
Gemini 2.5 Flash ถูกกว่า GPT-4 ประมาณ 10 เท่าต่อ token รองรับภาษาไทยได้ดี และรองรับ Structured Output ที่ Router Node ต้องใช้ในการตัดสิน routing ให้ความสมดุลระหว่างความสามารถและ cost ที่เหมาะสมสำหรับ use case นี้

---

### Q3 — Why use BGE-M3 instead of OpenAI Embeddings?

**English:**
BGE-M3 is open-source with no API cost, ranks top on the MTEB multilingual benchmark for Thai-English mixed text, and produces 1,024-dimensional vectors for richer semantic representation. For a bilingual financial system, it is both more capable and more cost-effective.

**ภาษาไทย:**
BGE-M3 เป็น Open-Source ไม่มีค่า API ได้คะแนนสูงสุดใน MTEB Multilingual Benchmark สำหรับข้อความไทย-อังกฤษ และให้ vector 1,024 มิติที่จับความหมายได้ละเอียดกว่า สำหรับระบบสองภาษาด้านการเงิน มันทั้งดีกว่าและประหยัดกว่า

---

### Q4 — What happens when documentation is updated?

**English:**
The document pipeline is fully independent of the chatbot. Simply re-run the pipeline on updated files — ingest, chunk, embed, and upsert into Qdrant. The chatbot benefits from the new knowledge immediately. No code changes or retraining required.

**ภาษาไทย:**
Pipeline แยกออกจาก chatbot โดยสมบูรณ์ เพียงรัน pipeline ใหม่กับเอกสารที่อัปเดต — ingest, chunk, embed และ upsert เข้า Qdrant แชทบอทได้ใช้ความรู้ใหม่ทันที ไม่ต้องแก้โค้ดหรือ retrain อะไรเลย

---

### Q5 — What is the purpose of Workflow Tracing?

**English:**
Workflow tracing gives users transparency — they can see exactly which documents were retrieved and how the answer was formed. For administrators, it provides auditability, which is critical in financial applications subject to regulatory scrutiny.

**ภาษาไทย:**
Workflow Tracing ให้ผู้ใช้เห็นว่าแชทบอทค้นพบเอกสารใดและสร้างคำตอบยังไง สำหรับผู้ดูแลระบบช่วยให้ตรวจสอบได้ ซึ่งสำคัญมากสำหรับแอปการเงินที่ต้องมีความโปร่งใส

---

### Q6 — How many concurrent users can the system handle?

**English:**
FastAPI is asynchronous, so it handles concurrent requests without blocking. Rate limiting is set at 10 requests per minute per IP. For larger scale, the system can be placed behind a load balancer with multiple backend instances.

**ภาษาไทย:**
FastAPI เป็น asynchronous framework รองรับ concurrent requests ได้โดยไม่ blocking มี Rate Limiting ที่ 10 requests/min ต่อ IP ถ้าต้องการ scale ใหญ่ขึ้นก็วางหลัง Load Balancer พร้อม backend หลาย instance ได้เลย

---

### Q7 — What does Temperature 0.3 mean and why not use a different value?

**English:**
Temperature controls output randomness. Lower values produce more consistent, factual responses. We chose 0.3 because financial accuracy matters more than creativity — high temperature risks generating plausible-sounding but incorrect information, which is exactly what RAG is designed to prevent.

**ภาษาไทย:**
Temperature ควบคุมความสุ่มของ output ค่าต่ำให้คำตอบที่สม่ำเสมอและอ้างอิงข้อเท็จจริง เราเลือก 0.3 เพราะในโดเมนการเงิน ความถูกต้องสำคัญกว่าความสร้างสรรค์ Temperature สูงเสี่ยงสร้างข้อมูลที่ฟังดูน่าเชื่อแต่ผิด ซึ่งเป็นปัญหาที่ RAG ออกแบบมาเพื่อลด

---

### Q8 — How does Query Enhancement work?

**English:**
The original query is sent to the LLM with a prompt to rewrite it — expanding abbreviations, adding platform context, and using terminology from official documentation. For example, "what is SL?" becomes "how does the Stop-Loss order type work on Finansia Hero?" This produces significantly better semantic similarity during retrieval.

**ภาษาไทย:**
คำถามเดิมถูกส่งให้ LLM เขียนใหม่ให้เฉพาะเจาะจงขึ้น ขยายคำย่อ เพิ่มบริบทแพลตฟอร์ม และใช้คำศัพท์จากเอกสารจริง เช่น "SL คืออะไร?" กลายเป็น "Stop-Loss ทำงานอย่างไรบน Finansia Hero?" ทำให้ cosine similarity ตอน retrieval ดีขึ้นอย่างมีนัยสำคัญ

---

### Q9 — How does the system handle out-of-scope queries?

**English:**
The Router Node uses the LLM to evaluate whether the query is related to Finansia Hero. If it falls outside scope, the system returns a polite message rather than attempting to answer without supporting documentation — preventing potentially harmful financial guidance.

**ภาษาไทย:**
Router Node ใช้ LLM ประเมินว่าคำถามเกี่ยวกับ Finansia Hero หรือไม่ ถ้านอกขอบเขตระบบตอบอย่างสุภาพแทนที่จะพยายามตอบโดยไม่มีเอกสารรองรับ ป้องกันการให้คำแนะนำการเงินที่อาจเป็นอันตราย

---

### Q10 — Can this system be adapted to other domains?

**English:**
Yes. The architecture is fully modular — replace the knowledge base, update the system prompt, and adjust domain-restricted search URLs. The routing logic, retrieval, and generation nodes remain unchanged. In fact, I am currently building a similar chatbot for my own department as a next step.

**ภาษาไทย:**
ได้ครับ สถาปัตยกรรม Modular ทั้งหมด เพียงเปลี่ยน knowledge base อัปเดต system prompt และปรับ URL สำหรับ domain-restricted search ส่วน routing, retrieval และ generation node คงเดิม ตอนนี้ผมกำลังพัฒนา chatbot แบบเดียวกันสำหรับภาควิชาของตัวเองอยู่ครับ

---

### Q11 — Where does the knowledge base data come from?

**English:**
Two sources. First, official PDF manuals provided by Finansia Hero covering platform features and usage. Second, CSV and JSON data collected through web scraping from public Q&A boards, which reflects real questions users actually ask — making the knowledge base more representative of real use cases.

**ภาษาไทย:**
มา 2 แหล่งครับ แหล่งแรกคือคู่มือ PDF ทางการจาก Finansia Hero ครอบคลุมฟีเจอร์และการใช้งาน แหล่งที่สองคือข้อมูล CSV และ JSON ที่ได้จาก web scraping จากบอร์ดถาม-ตอบสาธารณะ ซึ่งสะท้อนคำถามจริงที่ผู้ใช้ถาม ทำให้ knowledge base ครอบคลุมและตรงกับ use case จริงมากขึ้น

---

### Q12 — Was permission obtained for web scraping?

**English:**
The scraped data comes from publicly accessible boards. This is an academic project with no commercial use of the data. For any commercial deployment, formal permission would be required.

**ภาษาไทย:**
ข้อมูลที่ scrape มาจากบอร์ดที่เปิดให้เข้าถึงได้สาธารณะ และโปรเจคนี้เป็น Academic Project ไม่ได้นำข้อมูลไปใช้เชิงพาณิชย์ครับ ถ้าจะ deploy จริงในเชิงพาณิชย์ควรขอ permission อย่างเป็นทางการก่อน

---

### Q13 — Is this system deployed in production on Finansia Hero?

**English:**
Not yet. This is a working prototype for academic purposes. The full pipeline runs end-to-end and has been tested, but it has not been integrated into Finansia Hero's production system.

**ภาษาไทย:**
ยังครับ ตอนนี้เป็น working prototype สำหรับ academic purposes โดยเฉพาะ pipeline ทำงานได้ครบ end-to-end และผ่านการทดสอบแล้ว แต่ยังไม่ได้ integrate เข้ากับ production system ของ Finansia Hero

---

### Q14 — Are there details about this project you cannot disclose?

**English:**
Due to the confidentiality agreement with Finansia Syrus Securities, some internal details are restricted. What I can share is the architecture, methodology, and test results presented in this poster.

**ภาษาไทย:**
เนื่องจากโปรเจคนี้ทำร่วมกับ Finansia Syrus Securities บางรายละเอียดภายในอยู่ภายใต้ข้อตกลงการรักษาความลับครับ สิ่งที่แชร์ได้คือ architecture, methodology และผลการทดสอบที่นำเสนอในโปสเตอร์นี้

---

### Q15 — Why not use an official API from Finansia Hero instead of scraping?

**English:**
Finansia Hero does not provide a public API for documentation or Q&A data. Web scraping from public boards was the practical alternative for collecting real user questions that reflect actual use cases.

**ภาษาไทย:**
Finansia Hero ไม่ได้เปิด Public API สำหรับข้อมูลเอกสารหรือ Q&A ครับ การ scrape จากบอร์ดสาธารณะจึงเป็นทางเลือกที่ทำได้จริงสำหรับรวบรวมคำถามจาก user จริงๆ

---

### Q16 — What is the difference between RAG and Agentic RAG?

**English:**
Standard RAG retrieves documents and generates a response in a fixed pipeline. Agentic RAG adds decision-making — the system evaluates whether retrieved information is sufficient and autonomously decides to escalate to web search if needed. It is reactive rather than linear.

**ภาษาไทย:**
RAG ธรรมดาดึงเอกสารแล้วตอบเป็น pipeline ตายตัว Agentic RAG เพิ่มการตัดสินใจเข้าไป ระบบประเมินเองว่าข้อมูลที่ค้นมาเพียงพอไหม และตัดสินใจ escalate ไป web search ได้อัตโนมัติ มันตอบสนองต่อสถานการณ์แทนที่จะเดินตาม pipeline เส้นตรง

---

### Q17 — Why use Qdrant specifically over other vector databases like Pinecone?

**English:**
Qdrant offers a generous free tier on cloud, supports metadata filtering, and has excellent Python integration. For an academic project with budget constraints, Qdrant Cloud provided everything needed without additional cost.

**ภาษาไทย:**
Qdrant มี free tier บน cloud ที่ใช้ได้ดี รองรับ metadata filtering และ integrate กับ Python ได้ดีมาก สำหรับ academic project ที่มีข้อจำกัดด้านงบประมาณ Qdrant Cloud ให้ทุกอย่างที่ต้องการโดยไม่มีค่าใช้จ่ายเพิ่ม

---

### Q18 — Why is 17–33 seconds acceptable as a response time?

**English:**
The pipeline involves multiple LLM calls — query enhancement, routing, sufficiency evaluation, and generation. Compared to waiting on hold with a call center, 17–33 seconds for an accurate, documented answer is a significant improvement. Response time can be reduced in future iterations by optimizing the pipeline.

**ภาษาไทย:**
Pipeline มี LLM call หลายขั้นตอน ทั้ง query enhancement, routing, sufficiency evaluation และ generation เทียบกับการรอสาย Call Center แล้ว 17–33 วินาทีสำหรับคำตอบที่ถูกต้องและมีเอกสารรองรับถือว่าดีกว่ามาก และสามารถลดเวลาได้ในการพัฒนาต่อไป
