import cv2
import numpy as np
import os

def preprocess_template(image_path, output_path, kernel_size=3, iterations=1):
    """
    แปลงรูปคุกกี้เป็น binary outline
    
    Args:
        image_path: ที่อยู่ของไฟล์ต้นฉบับ
        output_path: ที่อยู่ที่ต้องการบันทึกไฟล์
        kernel_size: ขนาดของ kernel สำหรับการปรับแต่งเส้น
        iterations: จำนวนรอบของการปรับแต่งเส้น
    """
    # ตรวจสอบว่าโฟลเดอร์เป้าหมายมีอยู่หรือไม่ ถ้าไม่มีให้สร้างขึ้น
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"สร้างโฟลเดอร์ {output_dir}")
    
    # โหลดรูปภาพ
    img = cv2.imread(image_path)
    if img is None:
        print(f"ไม่สามารถโหลดรูปจาก {image_path}")
        return False
    
    print(f"กำลังประมวลผล: {image_path}")
    
    # แปลงเป็นภาพขาวดำ
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # ปรับความชัดเจนของภาพด้วย Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # ทำ threshold เพื่อแยกพื้นหลังและวัตถุ
    _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
    
    # ปรับปรุงเส้นขอบด้วย morphology operations
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=iterations)
    eroded = cv2.erode(dilated, kernel, iterations=iterations)
    
    # หาขอบภาพด้วย Canny edge detector
    edges = cv2.Canny(eroded, 50, 150)
    
    # ปรับความหนาของเส้นขอบเล็กน้อย
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
    
    # บันทึกไฟล์
    cv2.imwrite(output_path, edges)
    print(f"บันทึกไฟล์ binary template ไปที่ {output_path}")
    return True

def process_all_templates():
    """ประมวลผลรูปคุกกี้ทั้งหมดและสร้าง binary templates"""
    difficulties = ["easy", "normal", "hard"]
    
    # สร้างโฟลเดอร์ output ถ้ายังไม่มี
    os.makedirs("assets/bin", exist_ok=True)
    
    for difficulty in difficulties:
        input_path = f"assets/cookie_template_{difficulty}.png"
        output_path = f"assets/bin/cookie_template_{difficulty}_bin.png"
        
        success = preprocess_template(input_path, output_path)
        if success:
            print(f"ประมวลผลรูปแบบ {difficulty} สำเร็จ")
        else:
            print(f"ประมวลผลรูปแบบ {difficulty} ไม่สำเร็จ")

if __name__ == "__main__":
    print("เริ่มการสร้าง binary templates...")
    process_all_templates()
    print("เสร็จสิ้นการสร้าง binary templates")