# Bruno Routing Test Guide

คู่มือนี้ใช้สำหรับทดสอบ decision/routing ของ `/chat/` โดยตรงก่อนเทสผ่าน frontend

## เป้าหมาย

แยกการเทสออกเป็น 2 ส่วน:

1. `Smoke`
เช็กว่า backend ยังรันและ config ตอบได้

2. `Routing Regression`
เช็กว่าข้อความแต่ละแบบถูกจัดกลุ่มถูกต้องหรือไม่ ผ่าน `trace_events`

## Base URL

ค่าปัจจุบันในเครื่องนี้:

- `base_url = http://127.0.0.1:8001`
- `provider = openai`
- `model = gpt-5.4-mini`

## Bruno Environment

สร้าง environment ใน Bruno ชื่อ `local`

ตัวแปรที่ควรมี:

```json
{
  "baseUrl": "http://127.0.0.1:8001",
  "provider": "openai",
  "model": "gpt-5.4-mini",
  "sessionId": "bruno-routing-test"
}
```

## Requests ที่ควรสร้าง

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

### 3. Chat Routing Template

- Method: `POST`
- URL: `{{baseUrl}}/chat/`
- Header: `Content-Type: application/json`

ใช้ body template นี้:

```json
{
  "session_id": "{{sessionId}}",
  "query": "สวัสดีครับ",
  "enable_web_search": true,
  "force_web_search": false,
  "similarity_threshold": 0.7,
  "llm_provider": "{{provider}}",
  "llm_model": "{{model}}"
}
```

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

## ชุด Test แนะนำ

ให้ใช้ชุดข้อมูลจากไฟล์:

- [tests/data/bruno_routing_cases.json](/home/hoshi/hoshi/side-project/university-project/extracted_folder/ecs-chatbot/tests/data/bruno_routing_cases.json:1)

หลักการคือ:

- `expected_intent` = พฤติกรรมที่ต้องการ
- `expected_variant` = variant ที่ต้องการ
- `notes` = สิ่งที่ควรสังเกต

## ขั้นตอนทำงานที่แนะนำ

1. ยิง `GET /health`
2. ยิง `GET /llm/options`
3. สร้าง request `/chat/` 1 อัน แล้วเปลี่ยนแค่ค่า `query`
4. รันตามรายการใน `bruno_routing_cases.json`
5. จดผลว่าเคสไหน `pass/fail`
6. ส่งกลับมาเป็นตารางหรือข้อความคู่ `query -> actual intent/variant`

## รูปแบบรายงานที่ส่งกลับมา

แนะนำให้สรุปแบบนี้:

```text
สวัสดีครับ -> actual=greeting / greeting_template / pass
หิวข้าวจัง -> actual=domain_question / fail
ใครคือนายก -> actual=domain_question / fail
```

## Step ถัดไปหลังจากคุณใส่ Bruno แล้ว

1. รันเฉพาะ `Smoke` ก่อน
2. รัน `Routing Regression` ตามไฟล์ test cases
3. ส่งเฉพาะเคสที่ fail กลับมา
4. ผมจะแก้ decision layer จากผลจริงของ Bruno ไม่ใช้ frontend เป็นตัว debug หลักอีก
