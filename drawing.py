import pygame
import numpy as np
import cv2


class DrawingApp:
    def __init__(self):
        self.drawing = False
        self.prev_position = None  # เก็บพิกัดก่อนหน้า
        self.positions = []  # เก็บตำแหน่งของมือทั้งหมดที่ลากไว้

    def draw(self, frame_surface, hand_positions):
        # Convert the pygame surface to a numpy array
        frame = pygame.surfarray.array3d(frame_surface)  
        
        frame = cv2.transpose(frame)  
        #frame = cv2.flip(frame, 1)    

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  

        self.canvas = np.zeros_like(frame)

        #ตำแหน่งนิ้ว
        if hand_positions:
            for hand_position in hand_positions:
                x, y = hand_position

                frame_width = frame.shape[1]
                x = frame_width - x  
                

                # เช็คว่ามีการเคลื่อนที่ของนิ้วมั้ย
                if self.prev_position:
                    prev_x, prev_y = self.prev_position
                    if 0 <= prev_x < frame.shape[1] and 0 <= prev_y < frame.shape[0]:
                        # วาดเส้นจากพิกัดก่อนหน้าถึงพิกัดล่าสุด
                        cv2.line(self.canvas, (prev_x, prev_y), (x, y), (0, 0, 255), 5)  # วาดเส้นสีแดง
                
                # เก็บตำแหน่งล่าสุดเอาไว้
                self.prev_position = (x, y)
                self.positions.append((x, y))  # เก็บตำแหน่งของนิ้วทุกจุด

        # วาดเส้นทุกเส้นที่ผ่านมาบน canvas
        if len(self.positions) >= 2:
            for i in range(1, len(self.positions)):
                cv2.line(self.canvas, self.positions[i - 1], self.positions[i], (0, 0, 255), 5)

        # Blend the frame and canvas
        frame_with_drawing = cv2.addWeighted(frame, 0.8, self.canvas, 0.5, 0)

        # Convert the blended frame back to a pygame surface
        frame_with_drawing = cv2.cvtColor(frame_with_drawing, cv2.COLOR_BGR2RGB)  
        frame_with_drawing = cv2.transpose(frame_with_drawing)  
        frame_with_drawing = cv2.flip(frame_with_drawing, 0)    
        frame_with_drawing = pygame.surfarray.make_surface(frame_with_drawing)

        return frame_with_drawing