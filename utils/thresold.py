import cv2
import numpy as np
import matplotlib.pyplot as plt

def main():
    # อ่านภาพในโหมด grayscale
    img = cv2.imread("assets/cookie_template_easy.png", cv2.IMREAD_GRAYSCALE)
    
    # แสดงภาพต้นฉบับ
    plt.figure(figsize=(15, 10))
    
    # แสดงภาพต้นฉบับ
    plt.subplot(2, 2, 1)
    plt.imshow(img, cmap="gray")
    plt.title("Original Image")
    plt.axis('off')
    
    # Global Thresholding (ใช้ค่าความเข้มจากพิกัด (151, 87))
    x, y = 151, 87
    threshold_value = img[y, x]  # ดึงค่าความเข้มของพิกเซลที่พิกัด (x, y)
    _, global_thresh = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
    
    plt.subplot(2, 2, 2)
    plt.imshow(global_thresh, cmap="gray")
    plt.title(f"Global Thresholding (Threshold = {threshold_value})")
    plt.axis('off')
    
    # Adaptive Thresholding
    adaptive_thresh = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    plt.subplot(2, 2, 3)
    plt.imshow(adaptive_thresh, cmap="gray")
    plt.title("Adaptive Thresholding")
    plt.axis('off')
    
    # Otsu's Thresholding
    _, otsu_thresh = cv2.threshold(
        img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    plt.subplot(2, 2, 4)
    plt.imshow(otsu_thresh, cmap="gray")
    plt.title(f"Otsu's Thresholding (Threshold = {_})")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()