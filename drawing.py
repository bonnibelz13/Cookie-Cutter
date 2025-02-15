# drawing.py

import numpy as np
import cv2
from hand_tracking import HandTracker

class DrawingApp:
    def __init__(self):
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)  # สร้างกระดานวาดรูป
        self.tracker = HandTracker()  # ใช้ HandTracker เพื่อตรวจจับมือ

    def draw(self, frame, landmarks):
        """
        วาดเส้นตามตำแหน่งนิ้วชี้
        """
        if landmarks and landmarks.multi_hand_landmarks:  # ตรวจสอบว่า landmarks มีค่าหรือไม่
            index_finger = landmarks.multi_hand_landmarks[0].landmark[8]  # นิ้วชี้
            x, y = int(index_finger.x * 640), int(index_finger.y * 480)
            cv2.circle(self.canvas, (x, y), 5, (255, 255, 255), -1)  # วาดจุดบนกระดาน

        return cv2.addWeighted(frame, 0.7, self.canvas, 0.3, 0)  # ผสมภาพจากกล้องและกระดานวาดรูป

    def clear_canvas(self):
        """
        ล้างกระดานวาดรูป
        """
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)