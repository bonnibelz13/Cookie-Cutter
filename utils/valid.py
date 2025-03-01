import cv2
import numpy as np

ASSET_PATH = "assets/"

def overlay_images(image1_path, image2_path, alpha=0.5):
    """
    นำภาพสองภาพมาทับกันและทำให้ภาพจางลง (Alpha Blending)
    
    Args:
        image1_path (str): Path ของภาพแรก
        image2_path (str): Path ของภาพที่สอง
        alpha (float): ค่า Alpha (ความโปร่งแสง) ระหว่าง 0 ถึง 1
    
    Returns:
        blended_image (numpy.ndarray): ภาพที่ผสมกันแล้ว
    """
    # โหลดภาพทั้งสอง
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    
    # ตรวจสอบว่าภาพถูกโหลดได้หรือไม่
    if image1 is None or image2 is None:
        raise ValueError("ไม่สามารถโหลดภาพได้ ตรวจสอบ path อีกครั้ง")
    
    # ตรวจสอบว่าภาพมีขนาดเดียวกันหรือไม่
    if image1.shape != image2.shape:
        raise ValueError("ภาพทั้งสองต้องมีขนาดเดียวกัน")
    
    # ทำ Alpha Blending
    blended_image = cv2.addWeighted(image1, alpha, image2, 1 - alpha, 0)
    
    return blended_image

def main():
    # กำหนด path ของภาพทั้งสอง
    image1_path = f"{ASSET_PATH}/template/cookie_template_easy.png"
    image2_path = f"{ASSET_PATH}/processed/cookie_template_easy.png"
    # นำภาพมาทับกันและทำให้จางลง
    blended_image = overlay_images(image1_path, image2_path, alpha=0.5)
    
    # แสดงผล
    cv2.imshow("Blended Image", blended_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()