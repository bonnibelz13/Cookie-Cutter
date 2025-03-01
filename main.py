# main.py

import pygame
import sys
import time

from hand_tracking import HandTracking
from sound_manager import SoundManager





# กำหนดค่าพื้นฐาน
WIDTH, HEIGHT = 1200, 600
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BUTTON_COLOR = (0, 0, 0)  # พื้นหลังปุ่มเป็นสีดำ
BUTTON_HOVER_COLOR = (50, 50, 50)  # สีพื้นหลังปุ่มเมื่อเมาส์เลื่อนไป
BUTTON_BORDER_COLOR = (255, 0, 0)  # สีกรอบปุ่มเป็นสีแดง
FONT_COLOR = (255, 0, 0)  # สีฟอนต์เป็นสีแดง

# เริ่มต้น Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Cutter Game")

# สร้างอ็อบเจ็กต์ SoundManager
sound_manager = SoundManager()


# เล่นเสียงพื้นหลังเมื่อเปิดหน้าเมนูหลัก
if not pygame.mixer.music.get_busy():  # ตรวจสอบว่าเสียงพื้นหลังไม่ได้เล่นอยู่
    sound_manager.play_bg_music()


# font
font = pygame.font.SysFont("Arial", 40)
time_font = pygame.font.SysFont("Arial", 60) # font ตัวtext นับถอยหลังในเกม



# ฟังก์ชันสำหรับวาดปุ่ม
def draw_button(text, x, y, width, height, color, hover_color, border_color):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # ตรวจสอบว่าเมาส์อยู่บนปุ่มหรือไม่
    if x < mouse_x < x + width and y < mouse_y < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))  # พื้นหลังปุ่มเมื่อเมาส์อยู่บน
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))  # พื้นหลังปุ่มปกติ
    
    # วาดกรอบปุ่มเป็นสีแดง
    pygame.draw.rect(screen, border_color, (x, y, width, height), 5)  # กรอบปุ่ม

    # วาดข้อความในปุ่ม
    text_surface = font.render(text, True, FONT_COLOR)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))


# เริ่ม Hand Tracking
hand_tracker = HandTracking()




# ตัวแปรควบคุม
running = True
main_menu = True
difficulty_selected = False
difficulty = None
countdown = False
start_game_page = False
countdown_time = 3
cookie_image = None

game_start_time = None  # ตัวแปรจับเวลาการเริ่มเกม
game_duration = 60600  # ระยะเวลาเกม 3 นาที (3 นาที = 180,000 มิลลิวินาที) นานเกินไปปะ? ขอเร็วสุด 1 นาทีแล้วกัน 60600

# เพิ่มตัวแปร game_over_time
game_over_time = None


while running:
    screen.fill(BLACK)  # พื้นหลัง BLACK

    if main_menu:

        # วาดข้อความ "Cookie Cutter"
        title_text = font.render("Cookie Cutter", True, RED)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 - title_text.get_height() // 2))

        # วาดปุ่ม "Play Game"
        draw_button("Play Game", WIDTH // 4 - 150, HEIGHT // 2 - 40, 300, 80, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)

        # วาดปุ่ม "Quit"
        draw_button("Quit", WIDTH // 4 - 150, HEIGHT // 2 + 100, 300, 80, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)
        
    # ตำแหน่งปุ่ม "Easy", "Normal", "Hard" ให้อยู่ในแนวตั้ง
    if difficulty_selected:
        # วาดข้อความ "Select Difficulty"
        title_text = font.render("Select Difficulty", True, RED)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 5 - title_text.get_height() // 2))

        # วาดปุ่ม "Easy", "Normal", "Hard" แบบเรียงในแนวตั้ง
        button_width = 300
        button_height = 80
        button_spacing = 20  # ระยะห่างระหว่างปุ่ม
        button_y_start = HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2  # จัดกลางแนวตั้ง

        draw_button("Easy", WIDTH // 2 - button_width // 2, button_y_start, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)
        draw_button("Normal", WIDTH // 2 - button_width // 2, button_y_start + button_height + button_spacing, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)
        draw_button("Hard", WIDTH // 2 - button_width // 2, button_y_start + (button_height + button_spacing) * 2, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_BORDER_COLOR)



    # กำลังจะเริ้มเกม
    if start_game_page:
        title_text = font.render("Starting Game!", True, RED)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 - title_text.get_height() // 2))


    # นับถอยหลัง 3 2 1
    if countdown:
        # วาดข้อความ "3", "2", "1"
        countdown_text = font.render(str(countdown_time), True, RED)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2))

        # ลดเวลา
        if time.time() - countdown_start >= 1 and countdown_time > 0:
            print(time.time() - countdown_start)
            countdown_time -= 1
            countdown_start = time.time()

        # เมื่อหมดเวลาให้เริ่มเกม
        if countdown_time == 0:
            print("Game Started!")
            # เริ่มเกมจริง ๆ ที่นี่
            start_game_page = False # เอา text Starting Game! ออก


            # แสดงภาพจากกล้อง
            frame_surface = hand_tracker.get_frame()
            if frame_surface:
                # ขยายภาพจากกล้อง
                frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))  # ขยายภาพกล้องให้เต็มหน้าจอ

                # วางภาพจากกล้องบนหน้าจอ
                screen.blit(frame_surface, (0, 0))

                # แสดงภาพคุกกี้ซ้อนภาพกล้อง
                if cookie_image:
                    cookie_image.set_alpha(200)  # ทำให้ภาพคุกกี้โปร่งใส
                    # ขยายภาพคุกกี้
                    cookie_image = pygame.transform.scale(cookie_image, (400, 400))

                    # วางภาพคุกกี้บนภาพจากกล้อง
                    screen.blit(cookie_image, (WIDTH // 2 - cookie_image.get_width() // 2, HEIGHT // 2 - cookie_image.get_height() // 2))

            # เริ่มจับเวลาของเกม
            if game_start_time is None:
                game_start_time = pygame.time.get_ticks()  # เริ่มจับเวลาเมื่อเกมเริ่ม
                # เล่นเสียง in game 
                sound_manager.play_in_game_music()

            # คำนวณเวลาที่เหลือ
            elapsed_time = pygame.time.get_ticks() - game_start_time  # เวลาที่ผ่านไปตั้งแต่เริ่มเกม
            remaining_time = max(0, game_duration - elapsed_time)  # เวลาที่เหลือ (ไม่ให้ต่ำกว่า 0)


            # แสดงเวลาเหลือที่ข้างบนกึ่งกลางจอ
            minutes = remaining_time // 60000
            seconds = (remaining_time // 1000) % 60
            time_text = time_font.render(f"{minutes:02}:{seconds:02}", True, RED)
            screen.blit(time_text, ((WIDTH - time_text.get_width()) // 2, 80))  # แสดงเวลานับถอยหลังตรงกลาง บนคุกกี้

            # ถ้าหมดเวลา
            if remaining_time <= 600:  # <= 1 วินาที
                if game_over_time is None:  # ตั้งค่าเวลาที่เกมจบ
                    game_over_time = pygame.time.get_ticks()  # บันทึกเวลาที่เกมจบ
                    print("Game Over: Time's up!")
                    
                    # หยุดเสียงพื้นหลังเมื่อหมดเวลา
                    pygame.mixer.music.stop()
                
                # แสดงข้อความ "Time's Up!"
                title_text = font.render("Time's Up!", True, RED)
                screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2))
                
                
                # ตรวจสอบว่าเวลาผ่านไป 2 วินาทีหรือยัง
                if pygame.time.get_ticks() - game_over_time >= 2000:
                    # รีเซ็ตสถานะเกม
                    main_menu = True  # กลับไปที่หน้าเมนูหลัก
                    difficulty_selected = False
                    start_game_page = False
                    countdown = False
                    countdown_time = 3  # รีเซ็ตนับถอยหลัง
                    game_start_time = None  # รีเซ็ตเวลาเริ่มเกม
                    cookie_image = None  # ลบภาพคุกกี้
                    game_over_time = None  # รีเซ็ตเวลาที่เกมจบ
                    
                    # รีเซ็ตเสียงพื้นหลังเมื่อกลับไปที่หน้าเมนูหลัก
                    sound_manager.play_bg_music()


    # จับ event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if main_menu:
                # ถ้าคลิกที่ปุ่ม "Play Game"
                if WIDTH // 4 - 150 < mouse_x < WIDTH // 4 + 150 and HEIGHT // 2 - 40 < mouse_y < HEIGHT // 2 + 40:
                    print("Play Game Pressed")
                    # เล่นเสียงคลิกเมื่อกดปุ่ม
                    sound_manager.play_click_sound()
                    main_menu = False  # เปลี่ยนหน้าไปยังเลือกความยาก
                    
                    #แสดงหน้าเลือกระดับความยาก
                    difficulty_selected = True
                    difficulty = None  # รีเซ็ตความยาก

            if difficulty_selected:
                # ถ้าคลิกที่ปุ่ม "Easy", "Normal", หรือ "Hard"
                button_width = 300
                button_height = 80
                button_spacing = 20
                button_y_start = HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2  # คำนวณตำแหน่งเริ่มต้นแนวตั้ง
                
                # ตรวจสอบตำแหน่งการคลิกที่ปุ่ม "Easy"
                if WIDTH // 2 - button_width // 2 < mouse_x < WIDTH // 2 + button_width // 2:
                    if button_y_start < mouse_y < button_y_start + button_height:
                        difficulty = "Easy"

                        # เล่นเสียงคลิกเมื่อกดปุ่ม
                        sound_manager.play_click_sound()

                        cookie_image = pygame.image.load("assets/cookie_template_easy.png")
                        print("Selected Difficulty: Easy")
                        # difficulty_selected = False 
                        start_game_page = True # เปลี่ยนไปหน้า Start Game

                # ตรวจสอบตำแหน่งการคลิกที่ปุ่ม "Normal"
                if WIDTH // 2 - button_width // 2 < mouse_x < WIDTH // 2 + button_width // 2:
                    if button_y_start + button_height + button_spacing < mouse_y < button_y_start + button_height * 2 + button_spacing:
                        difficulty = "Normal"

                        # เล่นเสียงคลิกเมื่อกดปุ่ม
                        sound_manager.play_click_sound()

                        cookie_image = pygame.image.load("assets/cookie_template_normal.png")
                        print("Selected Difficulty: Normal")
                        # difficulty_selected = False
                        start_game_page = True # เปลี่ยนไปหน้า Start Game

                # ตรวจสอบตำแหน่งการคลิกที่ปุ่ม "Hard"
                if WIDTH // 2 - button_width // 2 < mouse_x < WIDTH // 2 + button_width // 2:
                    if button_y_start + (button_height + button_spacing) * 2 < mouse_y < button_y_start + (button_height + button_spacing) * 3:
                        difficulty = "Hard"

                        # เล่นเสียงคลิกเมื่อกดปุ่ม
                        sound_manager.play_click_sound()

                        cookie_image = pygame.image.load("assets/cookie_template_hard.png")
                        print("Selected Difficulty: Hard")
                        # difficulty_selected = False
                        start_game_page = True # เปลี่ยนไปหน้า Start Game

            # ถ้าคลิกที่ปุ่ม "Quit"
            elif WIDTH // 4 - 150 < mouse_x < WIDTH // 4 + 150 and HEIGHT // 2 + 100 < mouse_y < HEIGHT // 2 + 180:

                # เล่นเสียงคลิกเมื่อกดปุ่ม
                sound_manager.play_click_sound()

                running = False


            # ถ้าเลือกระดับความยากแล้ว ให้ มาหน้า Start Game"
            if start_game_page and cookie_image:
                difficulty_selected = False # ลบหน้าเลือกระดับความยาก เปลี่ยนไปหน้า Start Game
                # print("มี difficulty เลือกแล้ว")

                # หยุดเสียงพื้นหลังเมื่อออกจากหน้าเลือกระดับความยาก
                pygame.mixer.music.stop()


                print(f"Starting Game with Difficulty: {difficulty}")
                countdown = True
                countdown_start = time.time()  # เริ่มนับถอยหลัง

    pygame.display.flip()  # อัพเดตหน้าจอ

# ปิดโปรแกรม
hand_tracker.stop()
pygame.quit()
sys.exit()
