# AI Assistant Chatbot for Finansia Hero Website/Application

## Poster Content — Academic Format (Revised)

> เอกสารนี้เตรียมเนื้อหาสำหรับโปสเตอร์ Senior Project ขนาด A3
> ทั้งภาษาไทยและภาษาอังกฤษ — ปรับให้ครอบคลุมเกณฑ์การให้คะแนนทั้ง 7 ข้อ
>
> สัญลักษณ์: `[TODO: ...]` = ส่วนที่ต้องใส่ตัวเลขจริงจากการทดสอบ

---

## 1. Title / ชื่อเรื่อง

**English:**
> AI Assistant Chatbot for Finansia Hero Website/Application

**ภาษาไทย:**
> ระบบแชทบอทผู้ช่วยอัจฉริยะสำหรับเว็บไซต์และแอปพลิเคชัน Finansia Hero

---

## 2. Abstract / บทคัดย่อ

### English

**(Motivation)** Accessing information on the Finansia Hero Trading Platform is challenging due to the dispersion of important data across multiple sources, including user manuals, feature guides, and trading tools documentation. This fragmentation results in time-consuming information searches for users and increases customer support workload.
**(Objectives)** This project aims to develop an AI-powered chatbot using Retrieval-Augmented Generation (RAG) integrated with Gemini AI to provide accurate, context-aware, and automated responses to Finansia Hero platform inquiries, supporting both Thai and English.
**(Methodology)** The system employs a LangGraph state machine with intelligent routing across four nodes — query routing, RAG document retrieval, domain-restricted web search, and response generation — processing 1,737+ document chunks embedded with the BGE-M3 multilingual model and stored in Qdrant vector database.
**(Results)** The chatbot achieves [TODO: X%] response accuracy with an average response time of [TODO: X] seconds, and correctly routes queries to the appropriate information source. Query enhancement improves retrieval relevance by [TODO: X%] compared to unenhanced queries.
**(Conclusion)** The system demonstrates that RAG technology can be effectively applied in the fintech domain to provide reliable, 24-hour customer support while reducing staff workload and information search time.

### ภาษาไทย

**(แรงจูงใจ)** การเข้าถึงข้อมูลบนแพลตฟอร์มซื้อขายหลักทรัพย์ Finansia Hero เป็นเรื่องท้าทาย เนื่องจากข้อมูลสำคัญกระจัดกระจายอยู่ในหลายแหล่ง ทั้งคู่มือการใช้งาน เอกสารแนะนำฟีเจอร์ และคู่มือเครื่องมือการซื้อขาย ส่งผลให้ผู้ใช้เสียเวลาค้นหาข้อมูลและเพิ่มภาระงานฝ่ายสนับสนุนลูกค้า
**(วัตถุประสงค์)** โปรเจคนี้มุ่งพัฒนาแชทบอทอัจฉริยะโดยใช้ Retrieval-Augmented Generation (RAG) ร่วมกับ Gemini AI เพื่อตอบคำถามเกี่ยวกับแพลตฟอร์ม Finansia Hero ได้อย่างถูกต้อง ตรงบริบท และอัตโนมัติ รองรับทั้งภาษาไทยและอังกฤษ
**(วิธีดำเนินการ)** ระบบใช้ LangGraph State Machine พร้อม Intelligent Routing ผ่าน 4 โหนด ได้แก่ การจัดเส้นทางคำถาม, การค้นหาเอกสาร RAG, การค้นเว็บแบบจำกัดโดเมน และการสร้างคำตอบ โดยประมวลผลเอกสาร 1,737+ ชิ้น ฝังเวกเตอร์ด้วย BGE-M3 และจัดเก็บใน Qdrant
**(ผลลัพธ์)** แชทบอทมีความแม่นยำ [TODO: X%] เวลาตอบกลับเฉลี่ย [TODO: X] วินาที และจัดเส้นทางคำถามไปยังแหล่งข้อมูลที่เหมาะสมได้ถูกต้อง Query Enhancement ช่วยเพิ่มความแม่นยำในการค้นหาขึ้น [TODO: X%] เทียบกับคำถามที่ไม่ได้ปรับปรุง
**(สรุป)** ระบบแสดงให้เห็นว่าเทคโนโลยี RAG สามารถนำมาใช้ในโดเมนฟินเทคได้อย่างมีประสิทธิภาพ ให้บริการสนับสนุนลูกค้าตลอด 24 ชั่วโมง พร้อมลดภาระงานเจ้าหน้าที่และเวลาค้นหาข้อมูล

---

## 3. Introduction / บทนำ

### English

The Finansia Hero Trading Platform, developed by Finansia Syrus Securities PCL, provides comprehensive securities trading tools across web and mobile applications. However, users frequently struggle to locate specific information due to documentation being scattered across PDF manuals, feature guides, and web resources in both Thai and English. Conventional support methods such as FAQ pages and call centers are limited in scalability and cannot handle context-dependent queries effectively.

Recent advances in Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) enable the development of intelligent question-answering systems that retrieve relevant information from a knowledge base and generate grounded responses. This project applies RAG technology combined with a LangGraph agentic workflow to create a chatbot that intelligently routes queries, retrieves documentation, and generates accurate responses for the Finansia Hero platform.

### ภาษาไทย

แพลตฟอร์มซื้อขายหลักทรัพย์ Finansia Hero พัฒนาโดย บมจ.หลักทรัพย์ ฟินันเซีย ไซรัส ให้บริการเครื่องมือซื้อขายหลักทรัพย์ครบวงจรทั้งบนเว็บและแอปพลิเคชันมือถือ อย่างไรก็ตาม ผู้ใช้มักประสบปัญหาในการค้นหาข้อมูลเฉพาะ เนื่องจากเอกสารกระจัดกระจายอยู่ในคู่มือ PDF เอกสารแนะนำฟีเจอร์ และแหล่งข้อมูลบนเว็บ ทั้งในภาษาไทยและอังกฤษ การสนับสนุนลูกค้าแบบดั้งเดิม เช่น FAQ และ Call Center มีข้อจำกัดด้านการรองรับปริมาณผู้ใช้และไม่สามารถจัดการคำถามที่ซับซ้อนได้อย่างมีประสิทธิภาพ

ความก้าวหน้าของ Large Language Models (LLMs) และ Retrieval-Augmented Generation (RAG) เปิดโอกาสในการสร้างระบบตอบคำถามอัจฉริยะที่ค้นหาข้อมูลจากฐานความรู้และสร้างคำตอบที่มีหลักฐานอ้างอิง โปรเจคนี้ประยุกต์ใช้ RAG ร่วมกับ LangGraph Agentic Workflow เพื่อสร้างแชทบอทที่จัดเส้นทางคำถามอย่างชาญฉลาด ค้นหาเอกสาร และสร้างคำตอบที่ถูกต้องสำหรับแพลตฟอร์ม Finansia Hero

---

## 4. Objectives / วัตถุประสงค์

### English

1. To develop a RAG-based AI chatbot that answers user inquiries about the Finansia Hero Trading Platform using official documentation as the primary knowledge source.
2. To design an intelligent query routing system using LangGraph state machine architecture that determines the optimal retrieval strategy for each query.
3. To build a multilingual document processing pipeline that ingests, chunks, and embeds Thai and English documents from PDF, CSV, and JSON formats.
4. To integrate a domain-restricted web search fallback that supplements internal documentation when retrieved information is insufficient.
5. To evaluate system performance in terms of response accuracy, response time, and retrieval relevance.

### ภาษาไทย

1. เพื่อพัฒนาแชทบอท AI บนพื้นฐาน RAG ที่ตอบคำถามเกี่ยวกับแพลตฟอร์ม Finansia Hero โดยใช้เอกสารทางการเป็นแหล่งความรู้หลัก
2. เพื่อออกแบบระบบ Intelligent Query Routing โดยใช้ LangGraph State Machine ที่กำหนดกลยุทธ์การค้นหาที่เหมาะสมสำหรับแต่ละคำถาม
3. เพื่อสร้าง Document Processing Pipeline หลายภาษา ที่รองรับการนำเข้า แบ่งส่วน และฝังเวกเตอร์เอกสารภาษาไทยและอังกฤษ จากรูปแบบ PDF, CSV และ JSON
4. เพื่อบูรณาการระบบ Domain-Restricted Web Search เป็นกลไกสำรองเมื่อข้อมูลภายในไม่เพียงพอ
5. เพื่อประเมินประสิทธิภาพระบบในด้านความแม่นยำของคำตอบ เวลาตอบกลับ และความเกี่ยวข้องของการค้นหา

---

## 5. Methodology / วิธีดำเนินการ

### English

#### 5.1 System Architecture

The system uses a client-server architecture with a Streamlit frontend and FastAPI backend communicating via REST API. The core is a LangGraph state machine with four nodes:

1. **Router Node** — Performs query enhancement and determines routing path (RAG, web search, or direct answer).
2. **RAG Lookup Node** — Retrieves document chunks from Qdrant using semantic similarity search and evaluates information sufficiency.
3. **Web Search Node** — Performs domain-restricted web search via Tavily API when RAG results are insufficient.
4. **Answer Generation Node** — Generates responses using Gemini 2.5 Flash (temperature 0.3) for financial accuracy.

#### 5.2 Document Processing Pipeline

| Step | Method | Detail |
|---|---|---|
| Ingestion | Format-specific loaders | PyPDFLoader, CSVLoader, JSONLoader |
| Chunking | RecursiveCharacterTextSplitter | 1,000 chars, 200 overlap |
| Embedding | BGE-M3 | 1,024 dimensions, multilingual |
| Storage | Qdrant Cloud | Cosine similarity, metadata filtering |

#### 5.3 Variables Studied

| Variable Type | Variable | Values |
|---|---|---|
| Independent | Similarity Threshold | 0.5, 0.6, 0.7, 0.8, 0.9 |
| Independent | Query Enhancement | Enabled / Disabled |
| Independent | Web Search Fallback | Enabled / Disabled |
| Dependent | Response Accuracy | Measured by human evaluation |
| Dependent | Response Time | Seconds from query to response |
| Dependent | Retrieval Relevance | Cosine similarity score of retrieved chunks |

#### 5.4 Evaluation Method

The system was evaluated using [TODO: X] test queries covering platform features, account management, trading tools, and troubleshooting. Each response was assessed by human evaluators on:
- **Accuracy** — Is the answer factually correct and grounded in documentation?
- **Relevance** — Does the answer address the user's actual question?
- **Completeness** — Does the answer provide sufficient detail?
- **Response Time** — Time from query submission to response delivery.

### ภาษาไทย

#### 5.1 สถาปัตยกรรมระบบ

ระบบใช้สถาปัตยกรรม Client-Server ประกอบด้วย Frontend (Streamlit) และ Backend (FastAPI) สื่อสารผ่าน REST API แกนหลักคือ LangGraph State Machine ที่มี 4 โหนด:

1. **Router Node** — ปรับปรุงคำถาม (Query Enhancement) และกำหนดเส้นทาง (RAG, Web Search หรือตอบโดยตรง)
2. **RAG Lookup Node** — ค้นหาเอกสารจาก Qdrant ด้วย Semantic Similarity Search และประเมินความเพียงพอของข้อมูล
3. **Web Search Node** — ค้นเว็บผ่าน Tavily API แบบจำกัดโดเมน เมื่อ RAG ไม่เพียงพอ
4. **Answer Generation Node** — สร้างคำตอบด้วย Gemini 2.5 Flash (Temperature 0.3) เพื่อความถูกต้องทางการเงิน

#### 5.2 กระบวนการประมวลผลเอกสาร

| ขั้นตอน | วิธีการ | รายละเอียด |
|---|---|---|
| นำเข้า | Loader เฉพาะรูปแบบ | PyPDFLoader, CSVLoader, JSONLoader |
| แบ่งส่วน | RecursiveCharacterTextSplitter | 1,000 ตัวอักษร, Overlap 200 |
| ฝังเวกเตอร์ | BGE-M3 | 1,024 มิติ, หลายภาษา |
| จัดเก็บ | Qdrant Cloud | Cosine Similarity, กรอง Metadata |

#### 5.3 ตัวแปรที่ศึกษา

| ประเภทตัวแปร | ตัวแปร | ค่า |
|---|---|---|
| ตัวแปรต้น | Similarity Threshold | 0.5, 0.6, 0.7, 0.8, 0.9 |
| ตัวแปรต้น | Query Enhancement | เปิด / ปิด |
| ตัวแปรต้น | Web Search Fallback | เปิด / ปิด |
| ตัวแปรตาม | ความแม่นยำของคำตอบ | วัดโดยผู้ประเมิน |
| ตัวแปรตาม | เวลาตอบกลับ | วินาที จากคำถามถึงคำตอบ |
| ตัวแปรตาม | ความเกี่ยวข้องของการค้นหา | Cosine Similarity Score |

#### 5.4 วิธีการประเมินผล

ระบบถูกประเมินด้วยชุดคำถามทดสอบ [TODO: X] ข้อ ครอบคลุมฟีเจอร์แพลตฟอร์ม การจัดการบัญชี เครื่องมือซื้อขาย และการแก้ปัญหา โดยผู้ประเมินตรวจสอบ:
- **ความถูกต้อง** — คำตอบถูกต้องตามข้อเท็จจริงและอ้างอิงจากเอกสารหรือไม่?
- **ความเกี่ยวข้อง** — คำตอบตรงกับคำถามของผู้ใช้หรือไม่?
- **ความครบถ้วน** — คำตอบมีรายละเอียดเพียงพอหรือไม่?
- **เวลาตอบกลับ** — เวลาตั้งแต่ส่งคำถามจนได้รับคำตอบ

---

## 6. Results / ผลการดำเนินงาน

### English

#### 6.1 System Performance

| Metric | Value |
|---|---|
| Response Accuracy | [TODO: X%] |
| Average Response Time | [TODO: X seconds] |
| Retrieval Relevance (avg cosine similarity) | [TODO: 0.XX] |
| Routing Accuracy | [TODO: X%] |
| Knowledge Base Size | 1,737+ chunks |

#### 6.2 Effect of Query Enhancement

| Condition | Retrieval Relevance | Response Accuracy |
|---|---|---|
| Without Query Enhancement | [TODO: 0.XX] | [TODO: X%] |
| With Query Enhancement | [TODO: 0.XX] | [TODO: X%] |
| Improvement | [TODO: +X%] | [TODO: +X%] |

#### 6.3 Effect of Similarity Threshold

| Threshold | Precision | Recall | F1-Score |
|---|---|---|---|
| 0.5 | [TODO] | [TODO] | [TODO] |
| 0.6 | [TODO] | [TODO] | [TODO] |
| 0.7 (default) | [TODO] | [TODO] | [TODO] |
| 0.8 | [TODO] | [TODO] | [TODO] |
| 0.9 | [TODO] | [TODO] | [TODO] |

#### 6.4 Intelligent Routing Performance

The state machine correctly routes queries to the appropriate path:
- **RAG-sufficient queries** — Answered from platform documentation directly.
- **RAG-insufficient queries** — Escalated to domain-restricted web search automatically.
- **Out-of-domain queries** — Handled gracefully with appropriate messaging.

Routing accuracy: [TODO: X%] across [TODO: X] test queries.

### ภาษาไทย

#### 6.1 ประสิทธิภาพของระบบ

| ตัวชี้วัด | ค่า |
|---|---|
| ความแม่นยำของคำตอบ | [TODO: X%] |
| เวลาตอบกลับเฉลี่ย | [TODO: X วินาที] |
| ความเกี่ยวข้องของการค้นหา (avg cosine similarity) | [TODO: 0.XX] |
| ความถูกต้องของ Routing | [TODO: X%] |
| ขนาดฐานความรู้ | 1,737+ ชิ้น |

#### 6.2 ผลกระทบของ Query Enhancement

| เงื่อนไข | ความเกี่ยวข้องของการค้นหา | ความแม่นยำ |
|---|---|---|
| ไม่มี Query Enhancement | [TODO: 0.XX] | [TODO: X%] |
| มี Query Enhancement | [TODO: 0.XX] | [TODO: X%] |
| ดีขึ้น | [TODO: +X%] | [TODO: +X%] |

#### 6.3 ผลกระทบของ Similarity Threshold

| Threshold | Precision | Recall | F1-Score |
|---|---|---|---|
| 0.5 | [TODO] | [TODO] | [TODO] |
| 0.6 | [TODO] | [TODO] | [TODO] |
| 0.7 (ค่าเริ่มต้น) | [TODO] | [TODO] | [TODO] |
| 0.8 | [TODO] | [TODO] | [TODO] |
| 0.9 | [TODO] | [TODO] | [TODO] |

#### 6.4 ประสิทธิภาพ Intelligent Routing

State Machine จัดเส้นทางคำถามไปยังเส้นทางที่เหมาะสม:
- **คำถามที่ RAG เพียงพอ** — ตอบจากเอกสารแพลตฟอร์มโดยตรง
- **คำถามที่ RAG ไม่เพียงพอ** — ส่งต่อไปยัง Domain-Restricted Web Search อัตโนมัติ
- **คำถามนอกขอบเขต** — จัดการพร้อมข้อความแจ้งเตือนที่เหมาะสม

ความถูกต้องของ Routing: [TODO: X%] จากชุดทดสอบ [TODO: X] คำถาม

---

## 7. Innovation Highlights / จุดเด่นด้านความคิดริเริ่มสร้างสรรค์

> ส่วนนี้เตรียมไว้สำหรับเกณฑ์ข้อ 4 (ความคิดริเริ่มสร้างสรรค์)

### English

| Aspect | Innovation | How it differs from conventional approaches |
|---|---|---|
| **Problem** | Applies RAG to Thai fintech customer support | Most RAG chatbots target English-only or general domains; this addresses bilingual financial documentation |
| **Variables** | Studies interaction between similarity threshold, query enhancement, and web search fallback | Treats these as tunable independent variables rather than fixed parameters |
| **Measurement** | Uses LLM-as-Judge for automated sufficiency evaluation | RAG Lookup Node uses a dedicated judge prompt to evaluate if retrieved documents are sufficient, enabling autonomous routing decisions |
| **Data Collection** | Multi-format pipeline (PDF + CSV + JSON) with bilingual chunking | Most RAG systems handle single format; this ingests heterogeneous financial documents |
| **Presentation** | Real-time workflow tracing with transparent decision visualization | Users can see exactly how the chatbot decided to route, retrieve, and generate — unique for fintech chatbots |

### ภาษาไทย

| ด้าน | นวัตกรรม | ต่างจากแนวทางทั่วไปอย่างไร |
|---|---|---|
| **ปัญหา** | ประยุกต์ RAG กับ Customer Support ฟินเทคภาษาไทย | RAG Chatbot ส่วนใหญ่รองรับแค่ภาษาอังกฤษหรือโดเมนทั่วไป โปรเจคนี้รองรับเอกสารการเงินสองภาษา |
| **ตัวแปร** | ศึกษาปฏิสัมพันธ์ระหว่าง Similarity Threshold, Query Enhancement และ Web Search Fallback | ปฏิบัติกับสิ่งเหล่านี้เป็นตัวแปรต้นที่ปรับได้ ไม่ใช่ค่าคงที่ |
| **การวัด** | ใช้ LLM-as-Judge ประเมินความเพียงพอของข้อมูลอัตโนมัติ | RAG Lookup Node ใช้ Judge Prompt เฉพาะเพื่อประเมินว่าเอกสารที่ค้นพบเพียงพอหรือไม่ ทำให้ตัดสินใจ Routing ได้อัตโนมัติ |
| **การรวบรวมข้อมูล** | Pipeline หลายรูปแบบ (PDF + CSV + JSON) พร้อมการแบ่งส่วนสองภาษา | ระบบ RAG ส่วนใหญ่รองรับรูปแบบเดียว โปรเจคนี้นำเข้าเอกสารการเงินหลากหลายรูปแบบ |
| **การนำเสนอข้อมูล** | Workflow Tracing แบบ Real-Time พร้อมแสดงกระบวนการตัดสินใจ | ผู้ใช้เห็นได้ทันทีว่าแชทบอทตัดสินใจ Route, ค้นหา และสร้างคำตอบอย่างไร — ไม่เหมือน Chatbot ทั่วไป |

---

## 8. Practical Applications / การนำไปใช้ประโยชน์

> ส่วนนี้เตรียมไว้สำหรับเกณฑ์ข้อ 7 (การนำความรู้ไปใช้ประโยชน์)

### English

| Criterion | Description |
|---|---|
| **Usability** | The system is fully functional and deployed as a web application accessible via browser. Users can ask questions and receive AI-generated answers grounded in official documentation. |
| **Daily Life Application** | Investors and traders using the Finansia Hero platform can get instant answers about platform features, order types, technical analysis tools, and account management — replacing time-consuming manual searches through PDF manuals. |
| **Extensibility** | The modular architecture (LangGraph + Qdrant + configurable LLM) allows the system to be adapted for other trading platforms, financial products, or entirely different domains by simply replacing the document knowledge base. |
| **Commercial Viability** | The system can be deployed as a white-label customer support solution for securities brokers. Using Gemini 2.5 Flash (significantly cheaper than GPT-4) and open-source embeddings (BGE-M3), operational costs remain low while maintaining quality. |
| **Cost-Effectiveness** | Compared to hiring additional customer support staff, the chatbot provides 24/7 availability at a fraction of the cost. Estimated infrastructure cost: [TODO: X baht/month] for API calls + vector database hosting, versus [TODO: X baht/month] per support agent. |

### ภาษาไทย

| เกณฑ์ | รายละเอียด |
|---|---|
| **ใช้งานได้จริง** | ระบบทำงานได้สมบูรณ์และ Deploy เป็น Web Application เข้าถึงผ่าน Browser ผู้ใช้สามารถถามคำถามและรับคำตอบจาก AI ที่อ้างอิงจากเอกสารทางการ |
| **ใช้ในชีวิตประจำวัน** | นักลงทุนและเทรดเดอร์ที่ใช้ Finansia Hero สามารถได้รับคำตอบทันทีเกี่ยวกับฟีเจอร์แพลตฟอร์ม ประเภทคำสั่ง เครื่องมือวิเคราะห์ทางเทคนิค และการจัดการบัญชี — แทนที่การค้นหาจากคู่มือ PDF ที่เสียเวลา |
| **พัฒนาต่อยอดได้** | สถาปัตยกรรมแบบ Modular (LangGraph + Qdrant + LLM ที่เปลี่ยนได้) ทำให้สามารถปรับใช้กับแพลตฟอร์มซื้อขายอื่น ผลิตภัณฑ์ทางการเงินอื่น หรือโดเมนอื่นได้ เพียงเปลี่ยนฐานความรู้เอกสาร |
| **พัฒนาสู่เชิงพาณิชย์ได้** | ระบบสามารถ Deploy เป็น White-Label Customer Support สำหรับบริษัทหลักทรัพย์ต่างๆ การใช้ Gemini 2.5 Flash (ถูกกว่า GPT-4 อย่างมาก) และ Embedding แบบ Open-Source (BGE-M3) ทำให้ต้นทุนดำเนินการต่ำแต่คุณภาพคงเดิม |
| **คุ้มค่าต่อการลงทุน** | เทียบกับการจ้างเจ้าหน้าที่สนับสนุนเพิ่ม แชทบอทให้บริการ 24/7 ด้วยต้นทุนที่ต่ำกว่ามาก ค่าใช้จ่ายโครงสร้างพื้นฐานโดยประมาณ: [TODO: X บาท/เดือน] สำหรับ API + Vector Database เทียบกับ [TODO: X บาท/เดือน] ต่อเจ้าหน้าที่ 1 คน |

---

## 9. Conclusion / สรุปผล

### English

This project successfully developed an AI-powered chatbot for the Finansia Hero Trading Platform using RAG combined with a LangGraph state machine architecture. The system achieves [TODO: X%] response accuracy with [TODO: X]-second average response time, demonstrating that RAG technology can be effectively applied in the fintech domain for customer support.

Key contributions: (1) intelligent routing that dynamically selects between RAG and web search based on information sufficiency, (2) query enhancement that improves retrieval relevance by [TODO: X%], (3) a multilingual document pipeline supporting Thai and English, and (4) transparent workflow tracing for decision visibility.

Future work includes incorporating real-time market data, expanding the knowledge base, and conducting large-scale user studies.

### ภาษาไทย

โปรเจคนี้พัฒนาแชทบอท AI สำหรับแพลตฟอร์ม Finansia Hero โดยใช้ RAG ร่วมกับ LangGraph State Machine สำเร็จ ระบบมีความแม่นยำ [TODO: X%] เวลาตอบกลับเฉลี่ย [TODO: X] วินาที แสดงให้เห็นว่า RAG ใช้งานได้จริงในโดเมนฟินเทคสำหรับงานสนับสนุนลูกค้า

ผลงานสำคัญ: (1) Intelligent Routing ที่เลือกระหว่าง RAG กับ Web Search ตามความเพียงพอของข้อมูล (2) Query Enhancement ที่เพิ่มความแม่นยำการค้นหาขึ้น [TODO: X%] (3) Document Pipeline หลายภาษารองรับไทยและอังกฤษ และ (4) Workflow Tracing ที่โปร่งใสแสดงกระบวนการตัดสินใจ

งานในอนาคต ได้แก่ การบูรณาการข้อมูลตลาดแบบ Real-Time การขยายฐานความรู้ และการศึกษาประเมินผลจากผู้ใช้จำนวนมาก

---

## 10. References / เอกสารอ้างอิง

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474.

2. Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation. *arXiv preprint arXiv:2402.03216*.

3. Google. (2025). Gemini API Documentation. Retrieved from https://ai.google.dev/docs

4. LangChain. (2025). LangGraph: Build Stateful Agents. Retrieved from https://langchain-ai.github.io/langgraph/

5. Qdrant. (2025). Qdrant Vector Database Documentation. Retrieved from https://qdrant.tech/documentation/

6. Tavily. (2025). Tavily Search API Documentation. Retrieved from https://docs.tavily.com/

7. FastAPI. (2025). FastAPI Documentation. Retrieved from https://fastapi.tiangolo.com/

8. Finansia Syrus Securities PCL. (2025). Finansia Hero Trading Platform. Retrieved from https://www.finansiahero.com/

---

## 11. Recommended Figures / รูปภาพที่แนะนำ

1. **System Architecture Diagram** — แผนภาพ Frontend → Backend → Services → External APIs
2. **LangGraph State Machine Diagram** — แผนภาพ 4 โหนด พร้อมเส้นทาง Routing
3. **Document Processing Pipeline** — Raw Documents → Chunking → Embedding → Qdrant
4. **Chatbot UI Screenshot** — หน้าจอการใช้งานจริง
5. **Results Chart** — กราฟเปรียบเทียบ Query Enhancement on/off, Threshold ต่างๆ

---

## 12. Q&A Preparation / เตรียมตอบคำถามกรรมการ

> ส่วนนี้เตรียมไว้สำหรับเกณฑ์ข้อ 6 (การอธิบายและตอบคำถาม)

### คำถามที่กรรมการอาจถาม + แนวทางตอบ

**Q1: ทำไมเลือกใช้ RAG แทนที่จะ Fine-tune LLM โดยตรง?**
> Fine-tuning ต้องใช้ข้อมูลจำนวนมาก มีค่าใช้จ่ายสูง และต้องทำใหม่ทุกครั้งที่เอกสารเปลี่ยน RAG สามารถอัปเดตฐานความรู้ได้ทันทีโดยเพิ่มเอกสารใหม่เข้า Vector Database ไม่ต้อง retrain โมเดล นอกจากนี้ RAG ยังลดปัญหา Hallucination เพราะคำตอบอ้างอิงจากเอกสารจริง

**Q2: ทำไมเลือก Gemini แทน GPT-4 หรือ Claude?**
> Gemini 2.5 Flash มีราคาถูกกว่า GPT-4 ประมาณ 10 เท่า รองรับภาษาไทยได้ดี Inference เร็ว และรองรับ Structured Output สำหรับ Router Decision ซึ่งเพียงพอสำหรับ Use Case นี้

**Q3: ทำไมใช้ BGE-M3 แทน OpenAI Embeddings?**
> BGE-M3 เป็น Open-Source ไม่มีค่า API, มีประสิทธิภาพสูงสุดสำหรับข้อมูลหลายภาษา (Thai-English) ในเบนช์มาร์ค MTEB และมี 1,024 มิติ ให้ Representation ที่ดีกว่า

**Q4: ถ้าเอกสารอัปเดต ต้องทำอะไรบ้าง?**
> เพียงรัน Document Processing Pipeline ใหม่กับเอกสารที่อัปเดต ระบบจะ chunk, embed และ upsert เข้า Qdrant ไม่ต้องแก้โค้ดหรือ retrain อะไร

**Q5: Workflow Tracing มีประโยชน์อย่างไร?**
> ช่วยให้ผู้ใช้และผู้ดูแลระบบเห็นว่าแชทบอทตัดสินใจอย่างไร ทำให้ตรวจสอบได้ (Auditable) ซึ่งสำคัญมากในโดเมนการเงินที่ต้องมี Regulatory Compliance

**Q6: ระบบรองรับผู้ใช้พร้อมกันได้กี่คน?**
> ระบบมี Rate Limiting ที่ 10 requests/min ต่อ IP ใช้ FastAPI ที่เป็น Async รองรับ Concurrent Requests ได้ สามารถ Scale ด้วย Load Balancer ได้ในอนาคต

**Q7: Temperature 0.3 หมายความว่าอย่างไร? ทำไมไม่ใช้ค่าอื่น?**
> Temperature ควบคุมความหลากหลายของคำตอบ ค่าต่ำ (0.3) ทำให้คำตอบสม่ำเสมอและถูกต้อง เหมาะกับโดเมนการเงินที่ความถูกต้องสำคัญกว่าความสร้างสรรค์ ค่าสูงเกินไปอาจทำให้เกิด Hallucination

**Q8: Query Enhancement ทำงานอย่างไร?**
> ส่งคำถามเดิมไปให้ LLM ปรับให้เฉพาะเจาะจงมากขึ้น เช่น ขยายคำย่อ เพิ่มบริบทของแพลตฟอร์ม ทำให้ Similarity Search ค้นหาเอกสารที่ตรงกับความต้องการจริงได้ดีขึ้น

**Q9: มีการจัดการกรณีที่ผู้ใช้ถามนอกขอบเขตอย่างไร?**
> Router Node วิเคราะห์ว่าคำถามเกี่ยวข้องกับ Finansia Hero หรือไม่ ถ้าไม่เกี่ยวข้องจะตอบอย่างสุภาพว่าอยู่นอกขอบเขต ไม่พยายามตอบในสิ่งที่ไม่มีข้อมูลรองรับ

**Q10: โปรเจคนี้สามารถนำไปใช้กับโดเมนอื่นได้ไหม?**
> ได้ เพราะสถาปัตยกรรมเป็น Modular เพียงเปลี่ยนเอกสารในฐานความรู้ ปรับ System Prompt และ Domain-Restricted Search ก็สามารถใช้กับโดเมนอื่น เช่น ธนาคาร ประกันภัย หรือ E-Commerce ได้
