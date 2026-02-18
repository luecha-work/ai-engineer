import os


def find_knowledge_base(root_path: str):
    """
    ฟังก์ชันสำหรับค้นหาไฟล์ PDF ทั้งหมดในโฟลเดอร์ย่อยของ root_path

    Args:
        root_path (str): ที่อยู่ของโฟลเดอร์หลักที่ต้องการค้นหา

    Returns:
        list[dict]: รายการของไฟล์ PDF ที่พบ โดยแต่ละรายการเป็น dictionary
                    ที่มี 'subfolder_name' และ 'pdf_path'
    """
    found_files = []
    print(f"กำลังค้นหาใน: {root_path}")

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):

                subfolder_name = os.path.basename(dirpath)

                pdf_full_path = os.path.join(dirpath, filename)

                found_files.append({
                    "subfolder_name": subfolder_name,
                    "pdf_path": pdf_full_path
                })

    return found_files
