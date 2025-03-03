import pygame
import sys
import time
import cv2
import numpy as np

from drawing import DrawingApp
from hand_tracking import HandTracking
from sound_manager import SoundManager
from shape_match import ShapeMatcher 
from gestures import HandGesture
#from accuracy import get_cookie_contour, get_rotated_points, compute_accuracy
 
# กำหนดค่าพื้นฐาน
WIDTH, HEIGHT = 1200, 900
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BUTTON_COLOR = (0, 0, 0)             # พื้นหลังปุ่มเป็นสีดำ
BUTTON_HOVER_COLOR = (50, 50, 50)     # สีพื้นหลังปุ่มเมื่อเมาส์เลื่อนเข้า
BUTTON_BORDER_COLOR = (255, 0, 0)      # สีกรอบปุ่มเป็นสีแดง
FONT_COLOR = (255, 0, 0)               # สีฟอนต์เป็นสีแดง

# เริ่มต้น Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Cutter Game")

# สร้างอ็อบเจ็กต์ SoundManager
sound_manager = SoundManager()

# เล่นเสียงพื้นหลังเมื่อเปิดหน้าเมนูหลัก
if not pygame.mixer.music.get_busy():
    sound_manager.play_bg_music()

# font สำหรับปุ่มและข้อความนับถอยหลัง
font = pygame.font.SysFont("Arial", 40)
time_font = pygame.font.SysFont("Arial", 60)

# ฟังก์ชันสำหรับวาดปุ่ม
def draw_button(text, x, y, width, height, color, hover_color, border_color):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if x < mouse_x < x + width and y < mouse_y < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    pygame.draw.rect(screen, border_color, (x, y, width, height), 5)
    text_surface = font.render(text, True, FONT_COLOR)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2,
                               y + (height - text_surface.get_height()) // 2))

# เริ่ม Hand Tracking และ Drawing App
hand_tracker = HandTracking()
drawing_app = DrawingApp(WIDTH, HEIGHT)
# สร้างออบเจกต์ HandGesture
gesture_recognizer = HandGesture()


# ตัวแปรควบคุมสถานะเกม
running = True
main_menu = True
difficulty_selected = False
difficulty = None
countdown = False
start_game_page = False
countdown_time = 3
cookie_image = None

game_start_time = None        # เวลาเริ่มเกม
game_duration = 60000         # ระยะเวลาเกม 1 นาที (60000 มิลลิวินาที)
game_over_time = None         # เวลาเกมจบ

while running:
    screen.fill(BLACK)  # พื้นหลังสีดำ

    # หน้า Main Menu
    if main_menu:
        title_text = font.render("Cookie Cutter", True, RED)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2,
                                 HEIGHT // 4 - title_text.get_height() // 2))
        draw_button("Play Game", WIDTH // 4 - 150, HEIGHT // 2 - 40, 300, 80,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)
        draw_button("Quit", WIDTH // 4 - 150, HEIGHT // 2 + 100, 300, 80,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)

    # หน้าเลือกระดับความยาก
    if difficulty_selected:
        title_text = font.render("Select Difficulty", True, RED)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2,
                                 HEIGHT // 5 - title_text.get_height() // 2))
        button_width = 300
        button_height = 80
        button_spacing = 20
        button_y_start = HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2
        draw_button("Easy", WIDTH // 2 - button_width // 2, button_y_start,
                    button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)
        draw_button("Normal", WIDTH // 2 - button_width // 2,
                    button_y_start + button_height + button_spacing,
                    button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)
        draw_button("Hard", WIDTH // 2 - button_width // 2,
                    button_y_start + (button_height + button_spacing) * 2,
                    button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)

    # หน้าเริ่มเกม (แสดงข้อความ "Starting Game!")
    if start_game_page:
        title_text = font.render("Starting Game!", True, RED)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2,
                                 HEIGHT // 4 - title_text.get_height() // 2))

    # หน้าเกมกำลังนับถอยหลังและเล่นเกม
    if countdown:
        countdown_text = font.render(str(countdown_time), True, RED)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2,
                                     HEIGHT // 2 - countdown_text.get_height() // 2))
        if time.time() - countdown_start >= 1 and countdown_time > 0:
            countdown_time -= 1
            countdown_start = time.time()
        if countdown_time == 0:
            # เมื่อหมดนับถอยหลัง ให้เริ่มเกมจริง
            start_game_page = False

            # ดึงภาพจาก Hand Tracking แล้วปรับขนาดให้เต็มหน้าจอ
            frame_surface = hand_tracker.get_frame()
            if frame_surface:
                frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
                # ถ้าต้องการ mirror ภาพให้ flip ที่นี่ (ทำครั้งเดียว)
                # frame_surface = pygame.transform.flip(frame_surface, True, False)

                # ดึงพิกัดนิ้วจาก HandTracking
                hand_positions = hand_tracker.get_hand_positions()

                 # ดึงพิกัดทั้ง 21 จุดของมือ
                all_hand_landmarks = hand_tracker.get_all_hand_landmarks()
                # ปรับพิกัดจากความละเอียดของกล้อง (original_width, original_height) ไปยังขนาดหน้าจอ
                if hand_positions:
                    scale_x = WIDTH / hand_tracker.original_width
                    scale_y = HEIGHT / hand_tracker.original_height
                    hand_positions = [(int(x * scale_x), int(y * scale_y)) for (x, y) in hand_positions]


                    # ปรับพิกัดของจุดทั้งหมดของมือ (ถ้ามี)
                    if all_hand_landmarks:
                        all_hand_landmarks = [(int(x * scale_x), int(y * scale_y)) for (x, y) in all_hand_landmarks]

                # อัปเดตเลเยอร์เส้นใน DrawingApp
                drawing_app.update(hand_positions)
                drawing_layer = drawing_app.draw_layer()


               # ตรวจจับท่าทางจากมือ
                if all_hand_landmarks:
                  gesture_recognizer.process_gesture(all_hand_landmarks)

                # ตรวจสอบว่าเกมกำลังดำเนินการหรือไม่
                if not gesture_recognizer.game_running:
                    screen.fill((0, 0, 0))
                    print("🤘 Rock Gesture - Quitting")  # เมื่อท่าทาง "Rock Hand Sign" ถูกตรวจจับ
                    title_text = font.render("EXIT GAME BYE!", True, (0, 0, 255))
                    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2,
                                            HEIGHT // 2 - title_text.get_height() // 2))
                    pygame.display.flip()
                      # เติมหน้าจอด้วยสีดำ
                    pygame.time.wait(3000)  # แสดง Game Over สักพัก
                    running = False  # หยุดเกม
                    

                # สร้างพื้นหลังใหม่ (background) โดยเริ่มจากภาพจากกล้อง
                base_surface = frame_surface.copy()

                # วางรูปคุกกี้ลงบนพื้นหลัง
                if cookie_image:
                    cookie_image.set_alpha(200)
                    cookie_image_scaled = pygame.transform.scale(cookie_image, (400, 400))
                    base_surface.blit(cookie_image_scaled, (WIDTH // 2 - cookie_image_scaled.get_width() // 2,
                                                            HEIGHT // 2 - cookie_image_scaled.get_height() // 2))

                # นำ drawing_layer (เส้นที่วาด) มาวางซ้อนบนพื้นหลัง
                base_surface.blit(drawing_layer, (0, 0))

                # แสดงผลลงหน้าจอ
                screen.blit(base_surface, (0, 0))

                # คำนวณความแม่นยำของเส้นที่วาดเทียบกับเส้นลายบนคุกกี้
                accuracy = ShapeMatcher.match_edges(drawing_layer, cookie_image)
                if accuracy is not None:
                    accuracy_text = font.render(f"Accuracy: {accuracy:.2f}%", True, RED)
                else:
                    accuracy_text = font.render("Accuracy: N/A", True, RED)
                # แสดงผลที่มุมบนซ้ายของหน้าจอ
                screen.blit(accuracy_text, (WIDTH - accuracy_text.get_width() - 20, 20))  # 20px ห่างจากขอบขวา

            # จับเวลาเริ่มเกมและเล่นเพลงในเกม
            if game_start_time is None:
                game_start_time = pygame.time.get_ticks()
                sound_manager.play_in_game_music()

            # คำนวณเวลาและแสดงนับถอยหลังบนหน้าจอ
            elapsed_time = pygame.time.get_ticks() - game_start_time
            remaining_time = max(0, game_duration - elapsed_time)
            minutes = remaining_time // 60000
            seconds = (remaining_time // 1000) % 60
            time_text = time_font.render(f"{minutes:02}:{seconds:02}", True, RED)
            screen.blit(time_text, ((WIDTH - time_text.get_width()) // 2, 80))

            # เมื่อหมดเวลาเกม
            if remaining_time <= 600:
                if game_over_time is None:
                    game_over_time = pygame.time.get_ticks()
                    pygame.mixer.music.stop()
                title_text = font.render("Time's Up!", True, RED)
                screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2,
                                         HEIGHT // 2 - title_text.get_height() // 2))
                if pygame.time.get_ticks() - game_over_time >= 2000:
                    # รีเซ็ตสถานะเกม
                    drawing_app.reset()
                    main_menu = True
                    difficulty_selected = False
                    start_game_page = False
                    countdown = False
                    countdown_time = 3
                    game_start_time = None
                    cookie_image = None
                    game_over_time = None
                    sound_manager.play_bg_music()

    # จับ event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # กด r เพื่อลบเส้นที่วาด
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                drawing_app.reset()
            # กด ESC เพื่อออกจากเกม
            elif event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if main_menu:
                if WIDTH // 4 - 150 < mouse_x < WIDTH // 4 + 150 and HEIGHT // 2 - 40 < mouse_y < HEIGHT // 2 + 40:
                    sound_manager.play_click_sound()
                    main_menu = False
                    difficulty_selected = True
                    difficulty = None
                elif WIDTH // 4 - 150 < mouse_x < WIDTH // 4 + 150 and HEIGHT // 2 + 100 < mouse_y < HEIGHT // 2 + 180:
                    sound_manager.play_click_sound()
                    running = False

            elif difficulty_selected:
                button_width = 300
                button_height = 80
                button_spacing = 20
                button_y_start = HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2
                if WIDTH // 2 - button_width // 2 < mouse_x < WIDTH // 2 + button_width // 2:
                    if button_y_start < mouse_y < button_y_start + button_height:
                        difficulty = "Easy"
                        sound_manager.play_click_sound()
                        cookie_image = pygame.image.load("assets/cookie_template_easy.png")
                        start_game_page = True
                    elif button_y_start + button_height + button_spacing < mouse_y < button_y_start + button_height * 2 + button_spacing:
                        difficulty = "Normal"
                        sound_manager.play_click_sound()
                        cookie_image = pygame.image.load("assets/cookie_template_normal.png")
                        start_game_page = True
                    elif button_y_start + (button_height + button_spacing) * 2 < mouse_y < button_y_start + (button_height + button_spacing) * 3:
                        difficulty = "Hard"
                        sound_manager.play_click_sound()
                        cookie_image = pygame.image.load("assets/cookie_template_hard.png")
                        start_game_page = True

            # เมื่ออยู่ในหน้า Start Game ให้เริ่มนับถอยหลัง
            if start_game_page and cookie_image:
                difficulty_selected = False
                pygame.mixer.music.stop()
                print(f"Starting Game with Difficulty: {difficulty}")
                countdown = True
                countdown_start = time.time()

    pygame.display.flip()

hand_tracker.stop()
pygame.quit()
sys.exit()
