# hand_tracking.py

import cv2
import mediapipe as mp
import threading
import pygame

class HandTracking:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.frame_surface = None
        self.running = True
        self.thread = threading.Thread(target=self.capture_hand_tracking, daemon=True)
        self.thread.start()

    def capture_hand_tracking(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)  # พลิกแนวนอน
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            # แปลงภาพ OpenCV เป็น Surface ของ Pygame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (300, 200))
            self.frame_surface = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")

    def get_frame(self):
        return self.frame_surface

    def stop(self):
        self.running = False
        self.cap.release()
