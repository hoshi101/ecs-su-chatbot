# Bruno Collection

เปิด Bruno แล้วเลือก `Open Collection` ไปที่โฟลเดอร์นี้:

`bruno/ecs-chatbot`

ค่า environment ที่เตรียมไว้แล้ว:

- `baseUrl = http://127.0.0.1:8001`
- `provider = openai`
- `model = gpt-5.4-mini`
- `sessionId = bruno-routing-test`

โครงสร้างหลัก:

- `00 Health`
- `01 Config`
- `02 Chat`
- `03 Debug`

ใน `02 Chat` ผมแยกเคส routing ที่เราใช้ debug ไว้ให้แล้ว เพื่อให้คุณยิงทีละเคสและดู `trace_events` ได้ตรง ๆ
