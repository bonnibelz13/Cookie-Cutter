import cv2
import mediapipe as mp
import numpy as np

class HandGesture:
    def __init__(self):
        self.game_running = True  # สถานะเกม (True = เกมกำลังทำงาน, False = ออกจากเกม)
        self.gesture_cooldown = 0  # ป้องกันการตรวจจับซ้ำเร็วเกินไป
        self.cooldown_frames = 30  # รอ 30 เฟรมก่อนตรวจจับท่าถัดไป
        
        # เริ่มต้น MediaPipe Hands solution สำหรับการตรวจจับมือ
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )
        
        # ความมั่นใจขั้นต่ำในการตรวจจับท่ามือ
        self.min_gesture_confidence = 0.85
        
        # เก็บประวัติการตรวจจับ
        self.detection_history = []
        self.history_length = 5  # จำนวนเฟรมที่ใช้ในการตัดสินใจ
        
    def process_frame(self, frame):
        """
        ประมวลผลเฟรมและตรวจจับท่ามือ
        
        Args:
            frame (numpy.ndarray): เฟรมภาพจากกล้อง
            
        Returns:
            numpy.ndarray: เฟรมที่มีการวาดตำแหน่งมือ
        """
        # ลดค่า cooldown ลงในแต่ละเฟรม
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            
        # แปลงเป็น RGB สำหรับ MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # ตรวจจับมือ
        results = self.hands.process(rgb_frame)
        
        # วาดจุดและเส้นมือ
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # แปลง landmarks เป็นรายการตำแหน่ง (x, y)
                h, w, c = frame.shape
                hand_positions = []
                
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    hand_positions.append((x, y))
                
                # วาดจุด,เส้น
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                
                # ตรวจจับท่ามือและเพิ่มลงในประวัติ
                is_rock = self.is_rock_hand_sign(hand_positions)
                self.detection_history.append(is_rock)
                
                # เก็บเฉพาะ n เฟรมล่าสุด
                if len(self.detection_history) > self.history_length:
                    self.detection_history.pop(0)
                
                # ตัดสินใจจากประวัติการตรวจจับ
                if self.gesture_cooldown == 0 and self.should_trigger_rock():
                    print("Rock Hand Sign Detected! Exiting the program...")
                    self.game_running = False
                    self.gesture_cooldown = self.cooldown_frames
                
                # แสดงสถานะบนหน้าจอ
                confidence = sum(self.detection_history) / max(1, len(self.detection_history))
                cv2.putText(
                    frame,
                    f"Rock confidence: {confidence:.2f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0) if confidence > self.min_gesture_confidence else (0, 0, 255),
                    2
                )
        
        return frame
    
    def should_trigger_rock(self):
        """
        ตัดสินใจว่าควรเรียกใช้การตรวจจับท่า Rock หรือไม่ จากประวัติการตรวจจับ
        
        Returns:
            bool: True ถ้าควรเรียกใช้ท่า Rock, False ถ้าไม่ควร
        """
        if not self.detection_history:
            return False
        
        # คำนวณความมั่นใจจากสัดส่วนการตรวจจับที่เป็นบวก
        confidence = sum(self.detection_history) / len(self.detection_history)
        
        # ต้องมีความมั่นใจมากกว่าค่าที่กำหนด
        return confidence >= self.min_gesture_confidence
        
    def process_gesture(self, hand_positions):
        """
        ตรวจจับท่ามือ "Rock" จากพิกัดที่ได้จาก HandTracking
        
        Args:
            hand_positions (list): รายการของจุดพิกัด (x, y) ที่ได้จาก HandTracking
        """
        # ลดค่า cooldown ลงในแต่ละเฟรม
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return
            
        # ตรวจสอบว่ามีข้อมูลพิกัดมือเพียงพอหรือไม่
        if not hand_positions or len(hand_positions) < 21:
            return
            
        # โครงสร้างของ MediaPipe มี 21 จุด
        # เพิ่มผลการตรวจจับลงในประวัติ
        is_rock = self.is_rock_hand_sign(hand_positions)
        self.detection_history.append(is_rock)
        
        # เก็บเฉพาะ N เฟรมล่าสุด
        if len(self.detection_history) > self.history_length:
            self.detection_history.pop(0)
            
        # ตัดสินใจจากประวัติการตรวจจับ
        if self.should_trigger_rock():
            print("Rock Hand Sign Detected! Exiting the program...")
            self.game_running = False
            self.gesture_cooldown = self.cooldown_frames

   

    def is_rock_hand_sign(self, hand_positions):
        """
        ตรวจสอบท่ามือ "Rock" (🤘) - นิ้วชี้และนิ้วก้อยเหยียดตรง, นิ้วกลาง นิ้วนาง และนิ้วโป้งงอ
        """
        try:
            if len(hand_positions) >= 21:
                # กำหนดตำแหน่งสำคัญ
                index_tip, middle_tip, ring_tip, pinky_tip = hand_positions[8], hand_positions[12], hand_positions[16], hand_positions[20]
                index_pip, middle_pip, ring_pip, pinky_pip = hand_positions[6], hand_positions[10], hand_positions[14], hand_positions[18]
                index_mcp, middle_mcp, ring_mcp, pinky_mcp = hand_positions[5], hand_positions[9], hand_positions[13], hand_positions[17]
                thumb_mcp, thumb_tip = hand_positions[2], hand_positions[4]
                wrist = hand_positions[0]  # จุดข้อมือ

                def distance(p1, p2):
                    return np.linalg.norm(np.array(p1) - np.array(p2))

                # ✅ ใช้ตำแหน่งแนวตั้ง (Y) แทนระยะทาง
                index_extended = index_tip[1] < index_pip[1]  # นิ้วชี้เหยียด
                pinky_extended = pinky_tip[1] < pinky_pip[1]  # นิ้วก้อยเหยียด

                middle_bent = middle_tip[1] > middle_pip[1]  # นิ้วกลางงอ
                ring_bent = ring_tip[1] > ring_pip[1]  # นิ้วนางงอ

                # ✅ **แก้ไขเงื่อนไขนิ้วโป้ง**
                # นิ้วโป้งงอ → thumb_tip ต้องอยู่ต่ำกว่า thumb_mcp และ wrist
                thumb_bent = thumb_tip[1] < thumb_mcp[1] and thumb_tip[1] < wrist[1]

                # ✅ **เพิ่ม Debugging ให้ดูค่าที่ได้**
                print(f"Index Extended: {index_extended}, Pinky Extended: {pinky_extended}")
                print(f"Middle Bent: {middle_bent}, Ring Bent: {ring_bent}, Thumb Bent: {thumb_bent} (Tip: {thumb_tip[1]:.2f}, MCP: {thumb_mcp[1]:.2f}, Wrist: {wrist[1]:.2f})")
                print(f"Hand Size: {distance(wrist, index_tip):.2f}")

                is_rock = index_extended and pinky_extended and middle_bent and ring_bent and thumb_bent

                if is_rock:
                    print("✅ ROCK HAND SIGN DETECTED! 🤘")
                    return True

            return False

        except Exception as e:
            print(f"❌ Error in gesture detection: {e}")
            return False

