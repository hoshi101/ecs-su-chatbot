# Bruno Collection

เปิด Bruno แล้วเลือก `Open Collection` ไปที่โฟลเดอร์นี้:

`bruno/ecs-chatbot`

ค่า environment ที่เตรียมไว้แล้ว:

- `local-windows = http://localhost:8001`
- `local-wsl = http://127.0.0.1:8001`
- `provider = openai`
- `model = gpt-5.4-mini`
- `sessionId = bruno-routing-test`

โครงสร้างหลัก:

- `00 Health`
- `01 Config`
- `02 Routing`
- `03 Domain`
- `04 Debug`

ลำดับที่แนะนำ:

1. ใช้ environment `local-windows` ถ้า Bruno รันบน Windows
2. รัน `00 Health`
3. รัน `01 Config`
4. รัน `02 Routing`
5. ถ้า routing ผ่าน ค่อยไป `03 Domain`
6. ใช้ `04 Debug` เมื่อจะไล่ retrieval/embedding โดยตรง

ข้อสำคัญ:

- request ใน `02 Routing` และ `03 Domain` ถูกตั้ง `session_id` แยกต่อเคสไว้แล้ว เพื่อไม่ให้ memory ของแชทปนกัน
- ถ้าคุณสร้าง request เองใน Bruno ให้เปลี่ยน `session_id` ทุกครั้งเมื่อเทสคนละเคส intent
- ถ้า request ไหนเป็น shortcut ปกติ `sources` ควรเป็น `[]`
