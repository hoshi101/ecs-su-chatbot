# Planning Management

ใช้ไฟล์นี้เป็นศูนย์กลางสำหรับติดตามแผนงานย่อยของโปรเจค

- ทุกงานต้องมีสถานะ `[ ]` หรือ `[x]`
- เมื่อทำงานเสร็จ ต้องอัปเดต `Last Updated` และ `Completion Note` ทุกครั้ง
- ต้องเช็กไฟล์นี้ก่อนเริ่มงานรอบใหม่ เพื่อไม่ทำงานซ้ำ
- ชุดคำถามทดสอบหลักของโปรเจคอยู่ที่ `docs/testing/question_sets/`

## Plan 001: รีเซ็ตโครงสร้าง Planning Management

- Objective: ลบรูปแบบ plan เก่าและจัดแผนใหม่ให้อ่านง่าย ติดตามได้จริง
- Deliverable: `PLANNING_MANAGEMENT.md` เวอร์ชันใหม่ที่มีสถานะงาน, วันที่อัปเดต, และหมายเหตุปิดงาน
- Status: [x]
- Last Updated: 2026-04-22
- Completion Note: เขียนไฟล์ใหม่ทั้งฉบับและเปลี่ยนมาใช้รูปแบบ checklist + completion note แล้ว

## Plan 002: แยกชุดคำถามทดสอบเป็นหมวดหมู่

- Objective: สร้างชุดคำถามทดสอบแบบแยกหมวดและมีไฟล์รวมกลางสำหรับใช้เทสซ้ำ
- Deliverable: โฟลเดอร์ `docs/testing/question_sets/` พร้อมไฟล์ `general`, `department_info`, `lecturer`, `contact`, `out_of_scope`, และ `master`
- Status: [x]
- Last Updated: 2026-04-22
- Completion Note: สร้าง CSV แยก 5 หมวดและ master CSV รวม 70 คำถามเรียบร้อยแล้ว

## Plan 003: ตรวจความสอดคล้องของคำถามกับข้อมูลจริงในโปรเจค

- Objective: ให้ทุกคำถามและ expected keywords อ้างอิงจาก source จริงใน repo
- Deliverable: ชุดคำถามที่ผูกกับ `data/web/clean/` และเอกสารสถานะโปรเจคอย่างชัดเจน
- Status: [x]
- Last Updated: 2026-04-22
- Completion Note: ตรวจอ้างอิงจาก `department_contact`, `faculty_department_overview`, `department_lecturers`, `department_support_staff`, `program_*`, และ `staff_details` แล้ว

## Plan 004: อัปเดต Session Management ให้สะท้อนความคืบหน้าจริง

- Objective: บันทึกว่างานอะไรเสร็จแล้ว ตอนนี้โปรเจคอยู่จุดไหน และ canonical test assets อยู่ที่ไหน
- Deliverable: `SESSION_MANAGEMENT.md` ที่มี current status, completed work, current focus, และ recent updates
- Status: [x]
- Last Updated: 2026-04-22
- Completion Note: เพิ่มสถานะล่าสุดของโปรเจคและย้าย canonical test question location ไปที่ `docs/testing/question_sets/`

## Plan 005: เตรียมสถานะพร้อมสำหรับรอบทดสอบถัดไป

- Objective: ให้ทีมกลับมาอ่านแล้วรู้ทันทีว่าควรเทสอะไรต่อโดยไม่ทำงานซ้ำ
- Deliverable: แผนที่ปิดงานแล้ว, ชุดคำถามพร้อมใช้, และ session note สำหรับรอบ validation ถัดไป
- Status: [x]
- Last Updated: 2026-04-22
- Completion Note: งานเอกสารและ test assets รอบนี้พร้อมแล้ว เหลือขั้นตอนนำชุดคำถามไปใช้ทดสอบ chatbot จริง
