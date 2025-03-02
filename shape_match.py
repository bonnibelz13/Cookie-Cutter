import cv2
import numpy as np
import pygame

class ShapeMatcher:
    @staticmethod
    def get_contour_from_surface(surface):
        # แปลง Pygame Surface เป็น numpy array (RGB)
        surface_str = pygame.image.tostring(surface, 'RGB')
        img = np.frombuffer(surface_str, dtype=np.uint8).reshape(surface.get_height(), surface.get_width(), 3)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            return max(contours, key=cv2.contourArea)
        return None

    @staticmethod
    def match_shapes(surface1, surface2):
        contour1 = ShapeMatcher.get_contour_from_surface(surface1)
        contour2 = ShapeMatcher.get_contour_from_surface(surface2)
        if contour1 is None or contour2 is None:
            return None
        match_score = cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I1, 0.0)
        accuracy = max(0, 100 - match_score * 100)
        return accuracy

    @staticmethod
    def get_edge_image(surface):
        """
        แปลง Pygame Surface เป็น edge image ด้วย Canny Edge Detection
        """
        surface_str = pygame.image.tostring(surface, 'RGB')
        img = np.frombuffer(surface_str, dtype=np.uint8).reshape(surface.get_height(), surface.get_width(), 3)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return edges

    @staticmethod
    def match_edges(drawing_surface, cookie_surface, scaling_factor=1.0):
        """
        เปรียบเทียบความแม่นยำของจุดที่วาดกับเส้นลายบนคุกกี้
        โดยใช้การตรวจจับ edge และ distance transform
        """
        # ปรับขนาด cookie_surface ให้มีขนาดเดียวกับ drawing_surface
        cookie_surface_scaled = pygame.transform.scale(cookie_surface, (drawing_surface.get_width(), drawing_surface.get_height()))
        
        # สร้าง edge image สำหรับคุกกี้
        cookie_edges = ShapeMatcher.get_edge_image(cookie_surface_scaled)
        # invert image เพื่อให้ใช้ใน distance transform
        cookie_edges_inv = cv2.bitwise_not(cookie_edges)
        dist_transform = cv2.distanceTransform(cookie_edges_inv, cv2.DIST_L2, 3)

        # แปลง drawing_surface เป็น grayscale และ threshold เพื่อแยกจุดที่วาด
        drawing_str = pygame.image.tostring(drawing_surface, 'RGB')
        drawing_img = np.frombuffer(drawing_str, dtype=np.uint8).reshape(drawing_surface.get_height(), drawing_surface.get_width(), 3)
        drawing_gray = cv2.cvtColor(drawing_img, cv2.COLOR_RGB2GRAY)
        _, drawing_thresh = cv2.threshold(drawing_gray, 50, 255, cv2.THRESH_BINARY)

        # หาตำแหน่งพิกเซลที่มีการวาด (non-zero)
        drawn_points = np.column_stack(np.where(drawing_thresh > 0))
        if drawn_points.size == 0:
            return None

        # คำนวณระยะห่างจากแต่ละจุดไปยัง edge บนคุกกี้
        distances = []
        for pt in drawn_points:
            y, x = pt
            distances.append(dist_transform[y, x])
        avg_distance = np.mean(distances)

        # แปลงค่าเฉลี่ยของระยะห่างให้เป็นเปอร์เซ็นต์ความแม่นยำ
        accuracy = max(0, 100 - avg_distance * scaling_factor)
        return accuracy