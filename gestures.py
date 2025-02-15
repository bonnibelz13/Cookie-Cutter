# gestures.py

# def recognize_gesture(landmarks):
#     """
#     ตรวจจับท่าทางมือ
#     """
#     fingers = [4, 8, 12, 16, 20]  # นิ้วโป้ง, ชี้, กลาง, นาง, ก้อย
#     up_count = sum(1 for i in fingers if landmarks[i].y < landmarks[i - 2].y)

#     if up_count == 5:
#         return "Start Game"
#     elif up_count == 0:
#         return "Pause Game"
#     else:
#         return "Unknown Gesture"