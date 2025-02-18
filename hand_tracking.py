import cv2
import mediapipe as mp
import threading
import pygame


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

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    # ดึงค่าพิกัดของปลายนิ้วชี้ (landmark 8)
                    index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    h, w, _ = frame.shape
                    cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                    self.hand_positions.append((cx, cy))

                    # กรอบสี่เหลี่ยมรอบปลายนิ้วชี้
                    rect_size = 50
                    cv2.rectangle(frame, (cx - rect_size, cy - rect_size),
                                  (cx + rect_size, cy + rect_size), (0, 255, 0), 2)

                    # วาดจุดที่ปลายนิ้วชี้
                    cv2.circle(frame, (cx, cy), 10, (0, 0, 255), -1)

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

    def stop(self):
        self.running = False
        self.cap.release()