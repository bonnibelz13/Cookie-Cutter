import mediapipe as mp
import time

class HandGest:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.game_running = True  # สถานะของเกม
        self.paused = False  # สถานะ Pause
        self.last_gesture = None  # Gesture ล่าสุด
        self.last_gesture_time = time.time()  # เวลา Gesture ล่าสุด

    def _is_finger_up(self, tip, pip):
        """ ตรวจสอบว่านิ้วชูขึ้นหรือไม่ """
        return tip.y < pip.y

    def _is_finger_down(self, tip, pip):
        """ ตรวจสอบว่านิ้วงอลงหรือไม่ """
        return tip.y > pip.y

    def is_rock_hand(self, landmarks):
        """ ตรวจจับ Rock (🤘) """
        if not landmarks:
            return False

        return (
            self._is_finger_up(landmarks[8], landmarks[6]) and  # นิ้วชี้ขึ้น
            self._is_finger_up(landmarks[20], landmarks[18]) and  # นิ้วก้อยขึ้น
            self._is_finger_down(landmarks[12], landmarks[10]) and  # นิ้วกลางงอลง
            self._is_finger_down(landmarks[16], landmarks[14])  # นิ้วนางงอลง
        )

    def is_fist(self, landmarks):
        """ ตรวจจับ กำมือ (👊) """
        if not landmarks:
            return False

        return all(
            self._is_finger_down(landmarks[i], landmarks[i - 2])
            for i in [8, 12, 16, 20]
        )

    def is_open_palm(self, landmarks):
        """ ตรวจจับ ชูฝ่ามือ (✋) """
        if not landmarks:
            return False

        return all(
            self._is_finger_up(landmarks[i], landmarks[i - 2])
            for i in [8, 12, 16, 20]
        )

    def process_gesture(self, landmarks):
        """ เช็ค Gesture และเปลี่ยนสถานะเกม """
        current_time = time.time()
        if current_time - self.last_gesture_time < 1:  # ป้องกัน Gesture ซ้อนกัน
            return

        if self.is_rock_hand(landmarks):
            if self.last_gesture != "rock":
                print("🤘 Rock Gesture - Playing")
                self.paused = False
                self.last_gesture = "rock"
                self.last_gesture_time = current_time

        elif self.is_fist(landmarks):
            if self.last_gesture != "fist":
                print("👊 Fist Gesture - Paused")
                self.paused = True
                self.last_gesture = "fist"
                self.last_gesture_time = current_time

        elif self.is_open_palm(landmarks):
            if self.last_gesture != "palm":
                print("✋ Open Palm - Quitting")
                self.game_running = False
                self.last_gesture = "palm"
                self.last_gesture_time = current_time

    def draw_landmarks(self, frame, landmarks):
        """ วาดจุดเชื่อมนิ้ว """
        if landmarks:
            self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)