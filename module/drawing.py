import pygame
import numpy as np
import cv2

class DrawingApp:
    def __init__(self, width, height, template_path, processed_template_path, max_out_of_bounds=50, 
                 min_coverage_percent=70, similarity_threshold=0.7, line_thickness=15):  # เพิ่มพารามิเตอร์ line_thickness
        self.width = width
        self.height = height
        self.prev_position = None  # เก็บพิกัดก่อนหน้า
        self.positions = []        # เก็บตำแหน่งของนิ้วที่ลากไว้
        # สร้าง surface สำหรับวาดเส้นที่โปร่งแสง
        self.drawing_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.drawing_layer.fill((0, 0, 0, 0))  # โปร่งแสง
        self.total_pixels = width * height
        self.drawn_pixels = 0
        self.line_thickness = line_thickness  # เก็บค่าความหนาของเส้น
        
        # ตั้งค่าเกณฑ์ความสำเร็จ
        self.min_coverage_percent = min_coverage_percent  # เปอร์เซ็นต์ขั้นต่ำของพื้นที่ที่ต้องวาด
        self.similarity_threshold = similarity_threshold  # เกณฑ์ความคล้ายขั้นต่ำ (0-1)
        
        # เพิ่มส่วนตรวจสอบความแม่นยำ
        self.template_path = template_path          # ภาพต้นฉบับสำหรับแสดงผล UX
        self.processed_template_path = processed_template_path  # ภาพสำหรับตรวจสอบความแม่นยำ
        
        # โหลดภาพ template สำหรับแสดงผล
        self.template_surface = pygame.image.load(template_path).convert_alpha()
        self.template_surface = pygame.transform.scale(self.template_surface, (self.width, self.height))
        
        # โหลดภาพสำหรับตรวจสอบความแม่นยำ (ภาพที่ผ่านการประมวลผลมาแล้ว)
        self.processed_template = cv2.imread(processed_template_path)
        if self.processed_template is not None:
            self.processed_template = cv2.resize(self.processed_template, (self.width, self.height))
            # แปลงเป็นภาพสีเทาเพื่อการประมวลผล
            self.template_gray = cv2.cvtColor(self.processed_template, cv2.COLOR_BGR2GRAY)
            # หา contour จาก processed template
            ret, thresh = cv2.threshold(self.template_gray, 127, 255, 0)
            self.template_contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # คำนวณพื้นที่ของ template
            self.template_area = 0
            for contour in self.template_contours:
                self.template_area += cv2.contourArea(contour)
        else:
            self.template_gray = None
            self.template_contours = []
            self.template_area = 0
        
        # ตัวแปรเก็บสถานะว่าวาดออกนอกกรอบหรือไม่
        self.is_out_of_bounds = False
        self.out_of_bounds_count = 0
        self.max_out_of_bounds = max_out_of_bounds  # จำนวนพิกเซลที่วาดออกนอกกรอบได้สูงสุด
        
    def reset(self):
        """รีเซ็ตการวาด ล้าง surface และตัวแปรต่างๆ"""
        self.prev_position = None
        self.positions = []
        self.drawing_layer.fill((0, 0, 0, 0))
        self.drawn_pixels = 0
        self.is_out_of_bounds = False
        self.out_of_bounds_count = 0

    def update(self, hand_positions):
        """อัปเดตการวาดเส้นลงใน drawing_layer จากตำแหน่งนิ้วที่ส่งเข้ามา"""
        # หากมีตำแหน่งนิ้วใหม่
        if hand_positions:
            for hand_position in hand_positions:
                x, y = hand_position
                
                # ตรวจสอบว่าอยู่ในกรอบหรือไม่
                self.check_bounds(x, y)
                
                # ถ้ามีตำแหน่งก่อนหน้า ให้วาดเส้นจากก่อนหน้ามายังตำแหน่งปัจจุบัน
                if self.prev_position:
                    # ใช้ความหนาจากตัวแปร line_thickness แทนค่าคงที่ 5 
                    pygame.draw.line(self.drawing_layer, (255, 0, 0), self.prev_position, (x, y), self.line_thickness)
                    
                    # คำนวณพิกเซลที่วาดเพิ่ม (อย่างง่าย)
                    line_length = ((self.prev_position[0] - x) ** 2 + (self.prev_position[1] - y) ** 2) ** 0.5
                    approx_pixels = line_length * self.line_thickness  # คูณด้วยความหนาของเส้น
                    self.drawn_pixels += approx_pixels
                    
                    # ตรวจสอบจุดระหว่างเส้น
                    self._check_line_bounds(self.prev_position, (x, y))
                    
                self.prev_position = (x, y)
                self.positions.append((x, y))

    def _check_line_bounds(self, start_pos, end_pos):
        """ตรวจสอบจุดระหว่างเส้นว่าออกนอกกรอบหรือไม่"""
        # สร้างจุดระหว่างเส้น
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # หาจำนวนจุดที่จะตรวจสอบตามความยาวเส้น
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        steps = max(int(distance), 1)
        
        for i in range(1, steps):
            # หาจุดระหว่างเส้น
            t = i / steps
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            
            # ตรวจสอบจุด
            self.check_bounds(x, y)

    def check_bounds(self, x, y):
        """ตรวจสอบว่าจุด (x, y) อยู่ในกรอบหรือไม่ โดยใช้ processed_template"""
        if self.processed_template is None:
            return
            
        # ตรวจสอบว่าอยู่ในขอบเขตของภาพหรือไม่
        if 0 <= x < self.width and 0 <= y < self.height:
            # ตรวจสอบสีที่จุด (x, y) ในภาพ processed
            # ถ้าเป็นสีดำหรือสีที่กำหนดไว้สำหรับพื้นที่นอกกรอบ แสดงว่าออกนอกกรอบ
            b, g, r = self.processed_template[y, x]
            
            # ตรวจสอบว่าเป็นพื้นที่นอกกรอบหรือไม่ (ต้องปรับเงื่อนไขตามสีของภาพ processed)
            # สมมติว่าพื้นที่นอกกรอบจะเป็นสีขาวหรือใกล้เคียง (ค่า RGB สูง)
            if r > 200 and g > 200 and b > 200:  # ปรับเงื่อนไขตามลักษณะของภาพ processed
                self.out_of_bounds_count += 1
                # ถ้าออกนอกกรอบเกินกำหนด
                if self.out_of_bounds_count > self.max_out_of_bounds:
                    self.is_out_of_bounds = True

    def draw_layer(self):
        """คืนค่า surface ที่มีเส้นที่วาดไว้ (layer เส้น)"""
        return self.drawing_layer
        
    def draw_combined(self):
        """สร้างและคืนค่า surface ที่รวมภาพ template และเส้นที่วาดไว้"""
        combined = self.template_surface.copy()
        combined.blit(self.drawing_layer, (0, 0))
        return combined
        
    def is_failed(self):
        """ตรวจสอบว่าแพ้หรือไม่ (วาดออกนอกกรอบเกินกำหนด)"""
        return self.is_out_of_bounds

    def get_drawing_as_cv2_image(self):
        """แปลง drawing_layer เป็นภาพ CV2 สำหรับการตรวจสอบ"""
        try:
            # แปลง pygame surface เป็นข้อมูล numpy array
            drawing_rgb = pygame.surfarray.array3d(self.drawing_layer)
            # สลับแกน (pygame และ OpenCV มีการจัดเก็บข้อมูลภาพต่างกัน)
            drawing_rgb = drawing_rgb.transpose([1, 0, 2])
            # แปลงจาก RGB เป็น BGR (OpenCV ใช้ BGR)
            drawing_bgr = cv2.cvtColor(drawing_rgb, cv2.COLOR_RGB2BGR)
            # แปลงเป็นภาพสีเทา
            drawing_gray = cv2.cvtColor(drawing_bgr, cv2.COLOR_BGR2GRAY)
            return drawing_gray
        except Exception as e:
            print(f"Error converting drawing to CV2 image: {e}")
            # สร้างภาพว่างในกรณีที่มีข้อผิดพลาด
            return np.zeros((self.height, self.width), dtype=np.uint8)
        
    def calculate_shape_similarity(self):
        """คำนวณความคล้ายคลึงกันระหว่างรูปที่วาดกับ template แบบที่ทำงานได้ดีกว่า"""
        # ต้องคืนค่าเป็น tuple (coverage_percent, similarity) เสมอ
        if self.processed_template is None:
            return (0.0, 0.0)
            
        # แปลงการวาดเป็นภาพ OpenCV
        drawing_gray = self.get_drawing_as_cv2_image()
        
        # หา contour ของภาพที่วาด
        ret, drawing_thresh = cv2.threshold(drawing_gray, 5, 255, 0)  # ลดค่าเกณฑ์ลงเพื่อจับเส้นให้ได้มากขึ้น
        try:
            drawing_contours, _ = cv2.findContours(drawing_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        except Exception as e:
            print(f"Error finding contours: {e}")
            return (0.0, 0.0)
        
        if not drawing_contours or not self.template_contours:
            return (0.0, 0.0)
            
        # คำนวณพื้นที่ของภาพที่วาด
        drawing_area = 0
        for contour in drawing_contours:
            area = cv2.contourArea(contour)
            drawing_area += area
            
        # เพิ่มน้ำหนักให้กับพื้นที่เพื่อการคำนวณที่ดีขึ้น
        weighted_area = drawing_area * 1.5  # เพิ่มน้ำหนักให้พื้นที่
            
        # คำนวณเปอร์เซ็นต์การครอบคลุมพื้นที่
        coverage_percent = 0.0
        if self.template_area > 0:
            coverage_percent = (weighted_area / self.template_area) * 100
            
        # ใช้ Shape Matching เพื่อหาความคล้าย
        best_match = 0.0
        
        # ถ้ามีการวาดแต่ยังไม่มีความคล้าย ให้คืนค่าขั้นต่ำเพื่อให้เห็นว่ามีการวาดแล้ว
        if drawing_area > 0:
            best_match = max(0.05, best_match)  # กำหนดค่าขั้นต่ำของความคล้าย
        
        # ถ้ามีการวาดพื้นที่เกิน 5% ของพื้นที่ต้นแบบ ให้คืนค่าความคล้ายขั้นต่ำ 0.1
        if coverage_percent > 5:
            best_match = max(0.1, best_match)
        
        for template_contour in self.template_contours:
            if len(template_contour) < 5:  # ต้องมีจุดมากกว่า 5 จุด
                continue
                
            for drawing_contour in drawing_contours:
                if len(drawing_contour) < 5:
                    continue
                    
                try:
                    # ใช้ Hu Moments เพื่อเปรียบเทียบรูปร่าง
                    match = cv2.matchShapes(template_contour, drawing_contour, cv2.CONTOURS_MATCH_I1, 0.0)
                    # matchShapes คืนค่าน้อย = คล้ายกันมาก, ปรับให้เป็น 0-1 โดย 1 = คล้ายที่สุด
                    similarity = 1.0 / (1.0 + match) if match > 0 else 1.0
                    best_match = max(best_match, similarity)
                except Exception as e:
                    print(f"Error in shape matching: {e}")
                    continue
        
        # เพิ่มค่าความคล้ายตามเปอร์เซ็นต์การครอบคลุมพื้นที่
        # ถ้าครอบคลุมพื้นที่มาก ก็น่าจะคล้ายกันมาก
        if coverage_percent > 80:
            best_match = max(best_match, 0.8)
        elif coverage_percent > 50:
            best_match = max(best_match, 0.5)
        elif coverage_percent > 30:
            best_match = max(best_match, 0.3)
                
        return (coverage_percent, best_match)
        
    def is_drawing_complete(self):
        """ตรวจสอบว่าการวาดสำเร็จหรือยัง"""
        # ตรวจสอบว่าออกนอกกรอบเกินกำหนดหรือไม่
        if self.is_out_of_bounds:
            return False
            
        # ตรวจสอบความคล้ายคลึงและการครอบคลุมพื้นที่
        coverage, similarity = self.calculate_shape_similarity()
        
        # เงื่อนไขสำเร็จ: ครอบคลุมพื้นที่มากกว่าเกณฑ์ขั้นต่ำ และมีความคล้ายเพียงพอ
        is_complete = (coverage >= self.min_coverage_percent and 
                      similarity >= self.similarity_threshold)
                      
        return is_complete
        
    def get_completion_stats(self):
        """คืนค่าสถิติการทำเสร็จสิ้น"""
        coverage, similarity = self.calculate_shape_similarity()
        return {
            "coverage_percent": coverage,
            "shape_similarity": similarity,
            "out_of_bounds_count": self.out_of_bounds_count,
            "is_failed": self.is_out_of_bounds,
            "is_complete": self.is_drawing_complete()
        }