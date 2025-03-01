import cv2
import numpy as np
import matplotlib.pyplot as plt


# Example usage
import cv2
import numpy as np
import matplotlib.pyplot as plt

def main():
    # อ่านภาพในโหมด grayscale
    img = cv2.imread("assets/cookie_template_easy.png", cv2.IMREAD_GRAYSCALE)
    
    # แสดงภาพต้นฉบับ
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap="gray")
    plt.title("Original Image")
    plt.axis('off')
    
    # ดึงค่าความเข้มของพิกเซลที่พิกัด (x, y) = (151, 87)
    x, y = 151, 87
    threshold_value = 120  # OpenCV ใช้รูปแบบ (y, x) สำหรับการเข้าถึงพิกเซล
    
    print(f"Threshold value at ({x}, {y}): {threshold_value}")
    
    # ทำ Thresholding โดยใช้ค่าความเข้มที่ได้เป็นเกณฑ์
    _, binary_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)

    
    # แสดงภาพที่ผ่าน Thresholding
    plt.subplot(1, 2, 2)
    plt.imshow(binary_img, cmap="gray")
    plt.title(f"Binary Image (Threshold = {threshold_value})")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()