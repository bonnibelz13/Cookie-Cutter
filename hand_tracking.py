# hand_tracking.py

# import cv2
# import mediapipe as mp

# class HandTracker:
#     def __init__(self):
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
#         self.mp_draw = mp.solutions.drawing_utils

#     def detect_hands(self, frame):
#         """
#         ตรวจจับมือและ landmarks
#         """
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.hands.process(frame_rgb)

#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

#         return frame, results