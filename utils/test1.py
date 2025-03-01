import cv2
import numpy as np

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

def main():
    # อ่านภาพต้นฉบับ
    img = cv2.imread("assets/cookie_template_easy.png")
    
    # ค่า Threshold เริ่มต้น
    threshold_value = 120
    
    # สร้างหน้าต่างสำหรับแสดงผล
    cv2.namedWindow("Original Image")
    cv2.namedWindow("Processed Image")
    
    while True:
        # ประมวลผลภาพ
        processed_img = process_image(img, threshold_value)
        
        # แสดงภาพต้นฉบับ
        cv2.imshow("Original Image", img)
        
        # แสดงภาพที่ผ่านการประมวลผล
        cv2.imshow("Processed Image", processed_img)
        
        # รอรับการป้อนค่าจากผู้ใช้
        key = cv2.waitKey(1) & 0xFF
        
        # ปรับค่า Threshold ด้วยปุ่มลูกศรขึ้น/ลง
        if key == ord('q'):  # กด 'q' เพื่อออก
            break
        elif key == 82:  # ปุ่มลูกศรขึ้น
            threshold_value += 5
        elif key == 84:  # ปุ่มลูกศรลง
            threshold_value -= 5
        
        # แสดงค่า Threshold ปัจจุบัน
        print(f"Threshold: {threshold_value}")
    
    # ปิดหน้าต่างทั้งหมด
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()