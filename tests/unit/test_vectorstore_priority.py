from src.backend.services import vectorstore


def test_local_priority_documents_include_electrical_communications_program():
    documents = vectorstore._local_priority_documents("หลักสูตรวิศวกรรมไฟฟ้าสื่อสาร พ.ศ. 2565 รวมกี่หน่วยกิต")

    file_paths = {document["metadata"]["file_path"] for document in documents}

    assert "data/web/clean/program_electrical_communications.md" in file_paths


def test_local_priority_documents_include_master_program():
    documents = vectorstore._local_priority_documents("หลักสูตรปริญญาโทวิศวกรรมไฟฟ้าและคอมพิวเตอร์มีข้อมูลอะไรบ้าง")

    file_paths = {document["metadata"]["file_path"] for document in documents}

    assert "data/web/clean/program_master_ece.md" in file_paths


def test_local_priority_documents_include_curriculum_download_sources():
    documents = vectorstore._local_priority_documents("ขอเอกสารหลักสูตรปี 65 หน่อยครับ")

    file_paths = {document["metadata"]["file_path"] for document in documents}

    assert "data/web/clean/faculty_department_overview.md" in file_paths
    assert "data/web/clean/program_ecs.md" in file_paths
    assert "data/web/clean/program_electrical_communications.md" in file_paths
    assert "data/web/clean/program_master_ece.md" in file_paths


def test_local_priority_documents_include_undergraduate_programs_for_internship():
    documents = vectorstore._local_priority_documents("วิชา ฝึกงาน ต้องไม่น้อยกว่ากี่ชั่วโมง")

    file_paths = {document["metadata"]["file_path"] for document in documents}

    assert "data/web/clean/program_ecs.md" in file_paths
    assert "data/web/clean/program_electrical_communications.md" in file_paths


def test_local_priority_documents_match_staff_detail_by_name():
    documents = vectorstore._local_priority_documents("อาจารย์ยุทธนาทำวิจัยอะไร")

    file_paths = {document["metadata"]["file_path"] for document in documents}

    assert "data/web/clean/staff_details/lecturer_5.md" in file_paths


def test_local_priority_documents_match_staff_detail_by_research_interest():
    documents = vectorstore._local_priority_documents("อาจารย์คนไหนทำวิจัยด้าน FPGA หรือ VLSI บ้าง")

    file_paths = {document["metadata"]["file_path"] for document in documents}

    assert "data/web/clean/staff_details/lecturer_5.md" in file_paths
