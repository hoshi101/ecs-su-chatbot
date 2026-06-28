# Usage Tracking

ระบบบันทึก usage ของ endpoint `/chat/` แบบเบา ๆ สำหรับดูภาพรวมตอน demo/report เท่านั้น

ไฟล์ที่ถูกเขียน:

```bash
logs/usage_events.jsonl
```

หนึ่งบรรทัดคือหนึ่ง chat request ในรูปแบบ JSON เช่น route, intent, model, latency, source count, และสถานะ success/error โดยไม่เก็บ response เต็มและไม่เก็บ API key

สรุปผล usage:

```bash
.venv/bin/python scripts/summarize_usage.py
```

ปิด usage tracking ชั่วคราว:

```bash
USAGE_TRACKING_ENABLED=false .venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload
```

กำหนด path log เอง:

```bash
USAGE_LOG_FILE=/tmp/usage_events.jsonl .venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload
```

ตัวเลขที่เหมาะสำหรับพูดในสไลด์:

- จำนวน chat requests ทั้งหมด
- สัดส่วน route เช่น `rag`, `web`, `end`
- สัดส่วน intent เช่น `domain_question`, `contact`, `greeting`
- average/max latency
- average source count
- error count
