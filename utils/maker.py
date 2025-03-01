import cv2
import numpy as np
import os

# กำหนด path สำหรับโฟลเดอร์
PROCESSED_ASSET_PATH = "assets/processed/"
TEMPLATE_ASSET_PATH = "assets/template/"
THRESHOLD_VALUE = 120

def process_image(img, threshold_value):
    """
    ประมวลผลภาพด้วย Thresholding และ Noise Reduction
    
    Args:
        img (numpy.ndarray): ภาพต้นฉบับ
        threshold_value (int): ค่า Threshold
    
    Returns:
        processed_img (numpy.ndarray): ภาพที่ผ่านการประมวลผล
    """
    # แปลงภาพเป็น grayscale (ถ้ายังไม่ใช่)
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # ทำ Thresholding
    _, binary_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
    
    # ลด noise ด้วย Median Filter
    processed_img = cv2.medianBlur(binary_img, 5)
    
    return processed_img

def process_all_images(input_folder, output_folder, threshold_value):
    """
    ประมวลผลภาพทั้งหมดในโฟลเดอร์ input_folder และบันทึกลงในโฟลเดอร์ output_folder
    
    Args:
        input_folder (str): โฟลเดอร์ที่เก็บภาพต้นฉบับ
        output_folder (str): โฟลเดอร์ที่เก็บภาพที่ผ่านการประมวลผล
        threshold_value (int): ค่า Threshold
    """
    # ตรวจสอบว่าโฟลเดอร์ output มีอยู่หรือไม่ ถ้าไม่มีให้สร้าง
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # วนลูปอ่านภาพทั้งหมดในโฟลเดอร์ input_folder
    for filename in os.listdir(input_folder):
        # อ่านภาพ
        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path)
        
        # ตรวจสอบว่าภาพถูกอ่านได้หรือไม่
        if img is not None:
            # ประมวลผลภาพ
            processed_img = process_image(img, threshold_value)
            
            # บันทึกภาพที่ผ่านการประมวลผล
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, processed_img)
            print(f"Processed and saved: {output_path}")
        else:
            print(f"Failed to read image: {img_path}")

def main():
    # ประมวลผลภาพทั้งหมดในโฟลเดอร์ TEMPLATE_ASSET_PATH
    process_all_images(TEMPLATE_ASSET_PATH, PROCESSED_ASSET_PATH, THRESHOLD_VALUE)

if __name__ == "__main__":
    main()