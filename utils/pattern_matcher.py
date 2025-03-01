import cv2
import numpy as np
import pygame


class PatternMatcher:
    def __init__(self):
        """
        คลาสสำหรับตรวจสอบความคล้ายคลึงระหว่างการวาดของผู้เล่นกับแม่แบบคุกกี้
        """
        self.template = None
        self.template_edges = None
        self.template_contours = None
        self.start_points = []
        self.template_width = 400
        self.template_height = 400
        self.offset_x = 0
        self.offset_y = 0

    def load_template(self, template_path):
        """
        โหลดรูปแม่แบบและประมวลผล
        
        Parameters:
        template_path (str): พาธไปยังไฟล์รูปแม่แบบ
        """
        # โหลดรูปแม่แบบ
        template_img = cv2.imread(template_path)
        if template_img is None:
            print(f"Error: Could not load template image at {template_path}")
            return False
            
        # ปรับขนาด
        template_img = cv2.resize(template_img, (self.template_width, self.template_height))
        
        # แปลงเป็นขาวดำ
        template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
        
        # ใช้ GaussianBlur เพื่อลดสัญญาณรบกวน
        template_blur = cv2.GaussianBlur(template_gray, (5, 5), 0)
        
        # ใช้ Canny Edge Detection
        self.template_edges = cv2.Canny(template_blur, 50, 150)
        
        # หาขอบ (Contours)
        contours, _ = cv2.findContours(self.template_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # เลือกขอบที่ใหญ่ที่สุด
        if contours:
            self.template_contours = max(contours, key=cv2.contourArea)
            
            # สร้างรูปแม่แบบใหม่ที่มีเฉพาะขอบเท่านั้น
            self.template = np.zeros((self.template_height, self.template_width), dtype=np.uint8)
            cv2.drawContours(self.template, [self.template_contours], 0, 255, 2)
            
            # เลือกจุดเริ่มต้นที่เหมาะสม (บนขอบของรูป)
            # หาจุดบนสุด ซ้ายสุด ขวาสุด และกึ่งกลางด้านบน
            x, y, w, h = cv2.boundingRect(self.template_contours)
            self.start_points = [
                (x, y + h//2),  # จุดซ้าย
                (x + w, y + h//2),  # จุดขวา
                (x + w//2, y),  # จุดบน
                (x + w//2, y + h)   # จุดล่าง
            ]
            
            return True
        else:
            print("Error: No contours found in template")
            return False

    def compare_drawing(self, drawing_surface):
        """
        เปรียบเทียบการวาดของผู้เล่นกับแม่แบบและคำนวณความคล้ายคลึง
        
        Parameters:
        drawing_surface (pygame.Surface): Surface ที่ผู้เล่นวาด
        
        Returns:
        float: เปอร์เซ็นต์ความคล้ายคลึง (0-100)
        """
        if self.template is None:
            print("Error: Template not loaded")
            return 0
            
        # แปลง pygame Surface เป็นรูปแบบ OpenCV
        drawing_array = pygame.surfarray.array3d(drawing_surface)
        drawing_array = drawing_array.transpose([1, 0, 2])  # สลับแกน x, y
        
        # แปลงเป็น BGR
        drawing_bgr = cv2.cvtColor(drawing_array, cv2.COLOR_RGB2BGR)
        
        # ดึงเฉพาะพื้นที่ที่เกี่ยวข้อง (ตรงกลางของหน้าจอตามขนาดของแม่แบบ)
        h, w = drawing_bgr.shape[:2]
        center_x, center_y = w // 2, h // 2
        self.offset_x = center_x - self.template_width // 2
        self.offset_y = center_y - self.template_height // 2
        
        # ตรวจสอบว่าพื้นที่อยู่ในขอบเขตของรูป
        if (self.offset_x < 0 or self.offset_y < 0 or 
            self.offset_x + self.template_width > w or 
            self.offset_y + self.template_height > h):
            # ปรับขนาดพื้นที่ตัด
            crop_x = max(0, self.offset_x)
            crop_y = max(0, self.offset_y)
            crop_w = min(w - crop_x, self.template_width)
            crop_h = min(h - crop_y, self.template_height)
            region = drawing_bgr[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
            
            # ปรับขนาดกลับให้เท่ากับแม่แบบ
            if crop_w > 0 and crop_h > 0:
                region = cv2.resize(region, (self.template_width, self.template_height))
            else:
                return 0
        else:
            region = drawing_bgr[self.offset_y:self.offset_y+self.template_height, 
                               self.offset_x:self.offset_x+self.template_width]
        
        # แปลงเป็นขาวดำและประมวลผล
        region_gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # ใช้เฉพาะการหาพิกเซลสีแดงจากการวาด (แดง = (255,0,0) ใน RGB)
        red_mask = cv2.inRange(region, (0, 0, 150), (50, 50, 255))  # BGR - ตรวจจับสีแดง
        
        # ใช้ GaussianBlur
        red_mask_blur = cv2.GaussianBlur(red_mask, (5, 5), 0)
        
        # หาขอบของการวาด
        drawing_edges = cv2.Canny(red_mask_blur, 50, 150)
        
        # คำนวณความคล้ายคลึงโดยใช้ Structural Similarity Index (SSIM)
        # แต่เราจะใช้วิธีง่ายๆ โดยนับพิกเซลที่ตรงกัน
        
        # ขยายขอบของแม่แบบและการวาดเพื่อให้การเปรียบเทียบมีความยืดหยุ่นมากขึ้น
        kernel = np.ones((5, 5), np.uint8)
        template_dilated = cv2.dilate(self.template.copy(), kernel, iterations=2)
        drawing_dilated = cv2.dilate(drawing_edges, kernel, iterations=1)
        
        # หาส่วนที่ซ้อนทับกัน
        intersection = cv2.bitwise_and(template_dilated, drawing_dilated)
        template_area = np.sum(template_dilated > 0)
        intersection_area = np.sum(intersection > 0)
        
        # คำนวณเปอร์เซ็นต์การซ้อนทับ
        if template_area > 0:
            match_percentage = (intersection_area / template_area) * 100
        else:
            match_percentage = 0
            
        # คำนวณบทลงโทษสำหรับส่วนที่วาดแล้วเกินแม่แบบ
        drawing_area = np.sum(drawing_dilated > 0)
        if drawing_area > template_area * 1.5:  # หากวาดเกินมากเกินไป
            excess_penalty = min(50, (drawing_area - template_area) / template_area * 30)
            match_percentage = max(0, match_percentage - excess_penalty)
        
        # จำกัดค่าระหว่าง 0-100
        match_percentage = min(100, max(0, match_percentage))
            
        return match_percentage

    def get_start_points(self):
        """
        ส่งคืนจุดเริ่มต้นที่แนะนำสำหรับการวาด
        
        Returns:
        list: รายการของตำแหน่ง (x, y) ที่ควรเริ่มวาด
        """
        return self.start_points
        
    def debug_visualize(self, drawing_surface, output_path='debug_match.png'):
        """
        สร้างภาพที่แสดงการเปรียบเทียบระหว่างการวาดกับแม่แบบ (สำหรับดีบัก)
        
        Parameters:
        drawing_surface (pygame.Surface): Surface ที่ผู้เล่นวาด
        output_path (str): พาธสำหรับบันทึกภาพ debug
        """
        if self.template is None:
            print("Error: Template not loaded")
            return
            
        # แปลง pygame Surface เป็นรูปแบบ OpenCV
        drawing_array = pygame.surfarray.array3d(drawing_surface)
        drawing_array = drawing_array.transpose([1, 0, 2])
        drawing_bgr = cv2.cvtColor(drawing_array, cv2.COLOR_RGB2BGR)
        
        # ตัดเฉพาะพื้นที่ที่เกี่ยวข้อง
        h, w = drawing_bgr.shape[:2]
        center_x, center_y = w // 2, h // 2
        offset_x = center_x - self.template_width // 2
        offset_y = center_y - self.template_height // 2
        
        # ตรวจสอบขอบเขต
        if (offset_x < 0 or offset_y < 0 or 
            offset_x + self.template_width > w or 
            offset_y + self.template_height > h):
            crop_x = max(0, offset_x)
            crop_y = max(0, offset_y)
            crop_w = min(w - crop_x, self.template_width)
            crop_h = min(h - crop_y, self.template_height)
            region = drawing_bgr[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
            
            if crop_w > 0 and crop_h > 0:
                region = cv2.resize(region, (self.template_width, self.template_height))
            else:
                return
        else:
            region = drawing_bgr[offset_y:offset_y+self.template_height, 
                               offset_x:offset_x+self.template_width]
        
        # สร้างภาพสำหรับดีบัก
        debug_img = np.zeros((self.template_height, self.template_width * 3, 3), dtype=np.uint8)
        
        # แสดงแม่แบบ
        template_color = cv2.cvtColor(self.template, cv2.COLOR_GRAY2BGR)
        debug_img[:, :self.template_width] = template_color
        
        # แสดงการวาด
        debug_img[:, self.template_width:self.template_width*2] = region
        
        # แสดงซ้อนทับ
        red_mask = cv2.inRange(region, (0, 0, 150), (50, 50, 255))
        drawing_edges = cv2.Canny(red_mask, 50, 150)
        drawing_edges_color = cv2.cvtColor(drawing_edges, cv2.COLOR_GRAY2BGR)
        
        # ซ้อนทับแม่แบบและการวาด
        overlay = region.copy()
        template_color_for_overlay = cv2.cvtColor(self.template, cv2.COLOR_GRAY2BGR)
        overlay[template_color_for_overlay[:, :, 0] > 0] = [0, 255, 0]  # แม่แบบเป็นสีเขียว
        overlay[drawing_edges_color[:, :, 0] > 0] = [0, 0, 255]  # การวาดเป็นสีแดง
        
        debug_img[:, self.template_width*2:] = overlay
        
        # บันทึกภาพ
        cv2.imwrite(output_path, debug_img)
        print(f"Debug visualization saved to {output_path}")