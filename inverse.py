import cv2
import os

# กำหนด path โฟลเดอร์ที่มีรูป binary
input_folder = '/Users/patiphanakkahadsri/Documents/Final/Cookie-Cutter/assets/bin'  # แทนที่ด้วย path โฟลเดอร์รูปต้นทาง
output_folder = '/Users/patiphanakkahadsri/Documents/Final/Cookie-Cutter/assets/bin2'  # แทนที่ด้วย path โฟลเดอร์ปลายทาง

# สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# ลูปอ่านไฟล์ทั้งหมดในโฟลเดอร์
for filename in os.listdir(input_folder):
    # ตรวจสอบว่าเป็นไฟล์รูปภาพ (รองรับนามสกุล .png, .jpg, .bmp, etc.)
    if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        # อ่านภาพ binary
        image_path = os.path.join(input_folder, filename)
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Invert สี (ดำเป็นขาว, ขาวเป็นดำ)
        inverted_image = cv2.bitwise_not(image)

        # บันทึกรูปที่ invert ไว้ในโฟลเดอร์ปลายทาง
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, inverted_image)

        print(f'Processed and saved: {output_path}')

print("Inversion completed for all images!")