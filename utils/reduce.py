import cv2
import numpy as np
import matplotlib.pyplot as plt

# ค่า Threshold ที่กำหนด
THRESHOLD_VALUE = 120

def main():
    # อ่านภาพในโหมด grayscale
    img = cv2.imread("assets/cookie_template_normal.png", cv2.IMREAD_GRAYSCALE)
    
    # แสดงภาพต้นฉบับ
    plt.figure(figsize=(15, 10))
    
    # แสดงภาพต้นฉบับ
    plt.subplot(2, 3, 1)
    plt.imshow(img, cmap="gray")
    plt.title("Original Image")
    plt.axis('off')
    
    # ทำ Thresholding โดยใช้ค่าความเข้มที่ได้เป็นเกณฑ์
    _, binary_img = cv2.threshold(img, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    
    # แสดงภาพที่ผ่าน Thresholding
    plt.subplot(2, 3, 2)
    plt.imshow(binary_img, cmap="gray")
    plt.title(f"Binary Image (Threshold = {THRESHOLD_VALUE})")
    plt.axis('off')
    
    # ลด noise ด้วย Gaussian Blur
    gaussian_blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, binary_gaussian = cv2.threshold(gaussian_blur, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    
    plt.subplot(2, 3, 3)
    plt.imshow(binary_gaussian, cmap="gray")
    plt.title("Gaussian Blur + Thresholding")
    plt.axis('off')
    
    # ลด noise ด้วย Median Filter
    median_blur = cv2.medianBlur(img, 5)  # แก้ไขเป็น cv2.medianBlur
    _, binary_median = cv2.threshold(median_blur, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    
    plt.subplot(2, 3, 4)
    plt.imshow(binary_median, cmap="gray")
    plt.title("Median Filter + Thresholding")
    plt.axis('off')
    
    # ลด noise ด้วย Erosion + Dilation
    kernel = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(img, kernel, iterations=1)
    dilated = cv2.dilate(eroded, kernel, iterations=1)
    _, binary_morph = cv2.threshold(dilated, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    
    plt.subplot(2, 3, 5)
    plt.imshow(binary_morph, cmap="gray")
    plt.title("Erosion + Dilation + Thresholding")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()