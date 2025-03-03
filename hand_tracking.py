import cv2
import mediapipe as mp
import threading
import numpy as np
import pygame
from collections import deque


class HandTracking:
    def __init__(self):
        """
        คลาสสำหรับตรวจจับมือและแสดงผลลัพธ์เป็น Pygame Surface
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(0)
        self.frame_surface = None
        self.running = True
        self.hand_positions = []  # เก็บค่าพิกัดของนิ้วที่ตรวจพบ
        self.smooth_positions = deque(maxlen=5)
        
        # เก็บพิกัดทั้ง 21 จุดของมือ
        self.all_hand_landmarks = []

        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.thread = threading.Thread(target=self.capture_hand_tracking, daemon=True)
        self.thread.start()

    def capture_hand_tracking(self):
        """
        ดึงภาพจากกล้อง ตรวจจับมือ และบันทึกพิกัดของนิ้ว
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)  # พลิกภาพเพื่อให้สอดคล้องกับกระจก
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            self.hand_positions = []  # เคลียร์ค่าเดิมทุกเฟรม
            self.all_hand_landmarks = []  # เคลียร์ค่าจุดมือทั้งหมด

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    # เก็บพิกัดทั้งหมด 21 จุดของมือ
                    hand_points = []
                    h, w, _ = frame.shape
                    for landmark in hand_landmarks.landmark:
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        hand_points.append((x, y))
                    
                    # เก็บข้อมูลจุดทั้งหมดของมือ
                    self.all_hand_landmarks = hand_points

                    # ดึงค่าพิกัดของปลายนิ้วชี้ (landmark 8)
                    index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    # ตรวจสอบว่าอยู่ในช่วง 0-1 (เป็นพิกัดที่ถูกต้อง)
                    if not (0 <= index_finger_tip.x <= 1 and 0 <= index_finger_tip.y <= 1):
                        continue  # ข้ามไปถ้าค่าผิดปกติ

                    cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                    self.smooth_positions.append((cx, cy))

                    # คำนวณค่าเฉลี่ยของพิกัดใน queue ที่เก็บไว้ (สำหรับทำให้การเคลื่อนไหวนุ่มนวล)
                    if len(self.smooth_positions) > 0:
                        avg_x = int(np.mean([pos[0] for pos in self.smooth_positions]))
                        avg_y = int(np.mean([pos[1] for pos in self.smooth_positions]))
                    else:
                        avg_x, avg_y = cx, cy

                    self.hand_positions.append((avg_x, avg_y))

                    # กรอบสี่เหลี่ยมรอบปลายนิ้วชี้
                    rect_size = 30
                    cv2.rectangle(frame, (cx - rect_size, cy - rect_size),
                                  (cx + rect_size, cy + rect_size), (0, 255, 0), 1)

                    # วาดจุดที่ปลายนิ้วชี้
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                    # แสดงพิกัดของปลายนิ้วชี้
                    cv2.putText(frame, f"({cx}, {cy})", (cx + 20, cy - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # แปลงภาพ OpenCV เป็น Pygame Surface
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (300, 200))
            self.frame_surface = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")

    def get_frame(self):
        """
        คืนค่าภาพที่ถูกแปลงเป็น Pygame Surface
        """
        return self.frame_surface

    def get_hand_positions(self):
        """
        คืนค่าพิกัดของปลายนิ้วที่ตรวจจับได้
        """
        return self.hand_positions
        
    def get_all_hand_landmarks(self):
        """
        คืนค่าพิกัดทั้ง 21 จุดของมือที่ตรวจจับได้
        """
        return self.all_hand_landmarks

    def stop(self):
        self.running = False
        self.cap.release()