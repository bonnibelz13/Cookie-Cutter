import pygame

class DrawingApp:
    def __init__(self, width, height):
        self.prev_position = None  # เก็บพิกัดก่อนหน้า
        self.positions = []        # เก็บตำแหน่งของนิ้วที่ลากไว้
        # สร้าง surface สำหรับวาดเส้นที่โปร่งแสง
        self.drawing_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.drawing_layer.fill((0, 0, 0, 0))  # โปร่งแสง

    def reset(self):
        self.prev_position = None
        self.positions = []
        self.drawing_layer.fill((0, 0, 0, 0))

    def update(self, hand_positions):
        """อัปเดตการวาดเส้นลงใน drawing_layer จากตำแหน่งนิ้วที่ส่งเข้ามา"""
        # หากมีตำแหน่งนิ้วใหม่
        if hand_positions:
            for hand_position in hand_positions:
                x, y = hand_position
                # ถ้ามีตำแหน่งก่อนหน้า ให้วาดเส้นจากก่อนหน้ามายังตำแหน่งปัจจุบัน
                if self.prev_position:
                    pygame.draw.line(self.drawing_layer, (255, 0, 0), self.prev_position, (x, y), 5)
                self.prev_position = (x, y)
                self.positions.append((x, y))

    def draw_layer(self):
        """คืนค่า surface ที่มีเส้นที่วาดไว้ (layer เส้น)"""
        return self.drawing_layer