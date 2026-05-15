# Bruno Routing Test Guide

คู่มือนี้ใช้สำหรับทดสอบ decision/routing ของ `/chat/` โดยตรงก่อนเทสผ่าน frontend

## เป้าหมาย

แยกการเทสออกเป็น 2 ส่วน:

1. `Smoke`
เช็กว่า backend ยังรันและ config ตอบได้

2. `Routing Regression`
เช็กว่าข้อความแต่ละแบบถูกจัดกลุ่มถูกต้องหรือไม่ ผ่าน `trace_events`

## Base URL

ค่าที่ควรใช้:

- Windows Bruno: `http://localhost:8001`
- Bruno ใน WSL: `http://127.0.0.1:8001`
- `provider = openai`
- `model = gpt-5.4-mini`

## Bruno Environment

สร้าง environment 2 อัน:

- `local-windows`
- `local-wsl`

ตัวแปรที่ควรมี:

```json
{
  "baseUrl": "http://localhost:8001",
  "provider": "openai",
  "model": "gpt-5.4-mini",
  "sessionId": "bruno-routing-test"
}
```

```json
{
  "baseUrl": "http://127.0.0.1:8001",
  "provider": "openai",
  "model": "gpt-5.4-mini",
  "sessionId": "bruno-routing-test"
}
```

## โครงสร้าง Collection

- `00 Health`
- `01 Config`
- `02 Routing`
- `03 Domain`
- `04 Debug`

## Requests ที่ควรใช้

### 1. Health

- Method: `GET`
- URL: `{{baseUrl}}/health`

ผลที่ควรได้:

- status `200`
- body:

```json
{
  "status": "ok"
}
```

### 2. LLM Options

- Method: `GET`
- URL: `{{baseUrl}}/llm/options`

ผลที่ควรได้:

- status `200`
- มี `default_provider`
- มี `default_model`
- มี `providers`

### 3. Routing Requests

- Method: `POST`
- URL: `{{baseUrl}}/chat/`
- Header: `Content-Type: application/json`

ใช้ body template นี้:

```json
{
  "session_id": "{{sessionId}}-case-001",
  "query": "สวัสดีครับ",
  "enable_web_search": true,
  "force_web_search": false,
  "similarity_threshold": 0.7,
  "llm_provider": "{{provider}}",
  "llm_model": "{{model}}"
}
```

สำคัญ:

- ถ้าจะเทส `routing` แบบแยกเคส ห้ามใช้ `session_id` เดิมยิงหลายข้อความคนละ intent
- ระบบมี memory ต่อบทสนทนา ดังนั้น `session_id` เดิมควรใช้เฉพาะเมื่อคุณต้องการจำบริบทของแชทเดียวกัน
- สำหรับ Bruno ให้เปลี่ยน `session_id` ต่อเคส เช่น `{{sessionId}}-greeting-01`, `{{sessionId}}-contact-01`

## ฟิลด์ที่ต้องดูทุกครั้ง

ดูจาก response:

- `response`
- `trace_events[0].description`
- `trace_events[0].details.precheck_intent`
- `trace_events[0].details.shortcut_variant`
- `sources`

## วิธีอ่านผล

### Shortcut ที่ควรเกิด

ถ้าเป็น shortcut ปกติควรเห็น:

- `trace_events[0].description = "Shortcut response selected for '...'"` 
- `sources = []`

### Domain Flow

ถ้าเป็นคำถามในขอบเขตที่ไม่ shortcut:

- `trace_events[0].details.decision` ควรเป็น `rag`, `web`, `answer` หรือ `end`
- ต้องไม่ใช่ shortcut ผิด intent

## ชุด Request ที่ควรรัน

Routing:

- `01 Greeting TH`
- `02 Greeting EN`
- `03 Contact Phone TH`
- `04 Contact Phone EN`
- `05 Contact Facebook TH`
- `06 Out Of Scope Soft TH`
- `07 Out Of Scope Hard TH`
- `08 Out Of Scope Hard EN`
- `09 Mixed Greeting + Contact TH`
- `10 Mixed Greeting + Contact EN`
- `11 Mixed Contact + Detail TH`

Domain:

- `01 Admission TH`
- `02 Prerequisite TH`
- `03 Lecturer Contact Detailed TH`
- `04 Institution Other Department TH`
- `05 Institution Unknown TH`

## ขั้นตอนทำงานที่แนะนำ

1. ยิง `GET /health`
2. ยิง `GET /llm/options`
3. รัน `02 Routing` ทีละเคส
4. ถ้า routing ผ่าน ค่อยรัน `03 Domain`
5. ถ้าต้อง debug retrieval ค่อยใช้ `04 Debug`
6. ส่งเฉพาะเคสที่ fail กลับมาเป็น `query -> actual intent/variant`

## รูปแบบรายงานที่ส่งกลับมา

แนะนำให้สรุปแบบนี้:

```text
สวัสดีครับ -> actual=greeting / greeting_template / pass
หิวข้าวจัง -> actual=domain_question / fail
ใครคือนายก -> actual=domain_question / fail
```

## Step ถัดไปหลังจากคุณใส่ Bruno แล้ว

1. รันเฉพาะ `Smoke` ก่อน
2. รัน `02 Routing` ตามลำดับ
3. ส่งเฉพาะเคสที่ fail กลับมา
4. ผมจะแก้ decision layer จากผลจริงของ Bruno ไม่ใช้ frontend เป็นตัว debug หลักอีก
