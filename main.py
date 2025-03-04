import pygame
import sys
import time
import cv2
import numpy as np
import math

from drawing import DrawingApp
from hand_tracking import HandTracking
from sound_manager import SoundManager
from measure import ShapeMeasure 
from gestures import HandGesture  # ใช้ gestures.py ทีถูกต้อง
 
# กำหนดค่าพื้นฐาน
WIDTH, HEIGHT = 1200, 900
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BUTTON_COLOR = (0, 0, 0)             # พื้นหลังปุ่มเป็นสีดำ
BUTTON_HOVER_COLOR = (50, 50, 50)     # สีพื้นหลังปุ่มเมื่อเมาส์เลื่อนเข้า
BUTTON_BORDER_COLOR = (255, 0, 0)      # สีกรอบปุ่มเป็นสีแดง
FONT_COLOR = (255, 0, 0)               # สีฟอนต์เป็นสีแดง

# ฟังก์ชันสำหรับโหลด binary template
def load_binary_template(difficulty):
    """
    โหลด binary template และแปลงเป็น Pygame surface ที่มองเห็นได้ชัดเจน
    
    Args:
        difficulty: ระดับความยาก ("Easy", "Normal", "Hard")
        
    Returns:
        pygame.Surface: Surface ที่พร้อมแสดงผล หรือ None ถ้าโหลดไม่สำเร็จ
    """
    binary_path = f"assets/bin2/cookie_template_{difficulty.lower()}_bin.png"
    try:
        # วิธีที่ 1: ใช้ pygame โหลดโดยตรง (เร็วกว่า)
        binary_surface = pygame.image.load(binary_path).convert_alpha()
        # แปลงสีให้เป็นสีฟ้า
        blue_overlay = pygame.Surface(binary_surface.get_size()).convert_alpha()
        blue_overlay.fill((0, 180, 255))
        binary_surface.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return binary_surface
    except Exception as e:
        print(f"Error loading binary template with pygame: {e}")
        try:
            # วิธีที่ 2: ใช้ OpenCV ถ้าโหลดด้วย pygame ไม่สำเร็จ
            binary_img = cv2.imread(binary_path, cv2.IMREAD_GRAYSCALE)
            if binary_img is None:
                print(f"Could not load binary template from {binary_path}")
                return None
                
            # ทำให้เส้นสว่างขึ้น
            _, binary_img = cv2.threshold(binary_img, 50, 255, cv2.THRESH_BINARY)
            
            # แปลงเป็น RGB ก่อนที่จะเปลี่ยนสี
            colored = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
            
            # เปลี่ยนสีขาวให้เป็นสีฟ้า (BGR ใน OpenCV)
            colored[binary_img > 0] = [255, 180, 0]  # สีฟ้า (BGR)
            
            # แปลงเป็น Pygame surface
            colored = cv2.transpose(colored)
            colored = cv2.flip(colored, 1)
            binary_surface = pygame.surfarray.make_surface(colored)
            
            return binary_surface
        except Exception as e:
            print(f"Error loading binary template with OpenCV: {e}")
            return None

def evaluate_win_condition(metrics, difficulty):
    """
    Evaluate if the current metrics meet the win condition for the given difficulty
    
    Args:
        metrics: Dictionary containing all drawing metrics
        difficulty: Game difficulty level ("easy", "normal", or "hard")
        
    Returns:
        str: "win", "lose", or None
    """
    if not metrics:
        return None
        
    difficulty = difficulty.lower()
    thresholds = WIN_THRESHOLDS.get(difficulty, WIN_THRESHOLDS["normal"])
    
    # Check if out of bounds exceeds threshold (fail condition)
    if metrics["out_of_bounds"] > thresholds["out_of_bounds"]:
        print(f"Lose: Out of bounds {metrics['out_of_bounds']:.1f}% exceeds threshold {thresholds['out_of_bounds']}%")
        return "lose"
    
    # Check win conditions
    criteria_met = 0
    total_criteria = 3
    
    # Check overall score
    if metrics["overall_score"] >= thresholds["overall_score"]:
        criteria_met += 1
        
    # Check coverage
    if metrics["coverage"] >= thresholds["coverage"]:
        criteria_met += 1
        
    # Check similarity
    if metrics["similarity"] >= thresholds["similarity"]:
        criteria_met += 1
    
    # Win if overall score meets threshold AND majority of other criteria are met
    win_score_threshold = thresholds["overall_score"] * 0.9  # 90% of threshold
    if metrics["overall_score"] >= win_score_threshold and criteria_met >= 2:
        print(f"Win: Score {metrics['overall_score']:.1f}% meets criteria ({criteria_met}/{total_criteria})")
        return "win"
    
    # Neither win nor lose yet
    return None
    
def display_result_message(screen, result, metrics, difficulty, time_font, font):
    """
    Display win or lose message with visual effects
    
    Args:
        screen: Pygame screen surface to draw on
        result: "win" or "lose"
        metrics: Dictionary containing all metrics
        difficulty: Game difficulty level
        time_font: Large font
        font: Regular font
    """
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Different overlay color based on result
    if result == "win":
        overlay.fill((0, 50, 0, 150))  # Green tint for win
        main_color = (50, 255, 50)
        header_text = "SUCCESS!"
    else:
        overlay.fill((50, 0, 0, 150))  # Red tint for lose
        main_color = (255, 50, 50)
        header_text = "TRY AGAIN!"
        
    screen.blit(overlay, (0, 0))
    
    # Calculate pulsing effect for the first 2 seconds
    global result_effect_active, result_effect_start
    if result_effect_active:
        elapsed = pygame.time.get_ticks() - result_effect_start
        if elapsed < 2000:  # 2 seconds of pulsing
            # Oscillate between 150 and 255 for pulsing effect
            alpha = 150 + int(105 * abs(math.sin(elapsed / 200)))
            scale_factor = 1.0 + 0.1 * abs(math.sin(elapsed / 200))
        else:
            result_effect_active = False
            alpha = 255
            scale_factor = 1.0
    else:
        alpha = 255
        scale_factor = 1.0
    
    # Draw result message with scaling effect
    result_text = time_font.render(header_text, True, main_color)
    
    # Scale the text for the pulsing effect
    if scale_factor != 1.0:
        result_text = pygame.transform.scale(result_text, 
                                         (int(result_text.get_width() * scale_factor), 
                                          int(result_text.get_height() * scale_factor)))
    
    # Set transparency
    result_text.set_alpha(alpha)
    
    # Position variables
    y_pos = HEIGHT // 3
    y_spacing = 40
    
    # Draw the main result message
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, y_pos))
    y_pos += result_text.get_height() + 20
    
    # Draw difficulty
    diff_text = font.render(f"Difficulty: {difficulty.upper()}", True, (255, 255, 255))
    screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, y_pos))
    y_pos += y_spacing
    
    # Draw metrics
    metrics_to_show = [
        ("Overall Score", metrics["overall_score"], "%"),
        ("Coverage", metrics["coverage"], "%"),
        ("Out of Bounds", metrics["out_of_bounds"], "%"),
        ("Similarity", metrics["similarity"], "%")
    ]
    
    thresholds = WIN_THRESHOLDS.get(difficulty.lower(), WIN_THRESHOLDS["normal"])
    
    for label, value, unit in metrics_to_show:
        # Determine color based on good/bad value
        if label == "Out of Bounds":
            # For out_of_bounds, lower is better
            threshold = thresholds.get("out_of_bounds", 0)
            color = (50, 255, 50) if value <= threshold else (255, 50, 50)
        else:
            # For other metrics, higher is better
            threshold_key = label.lower().replace(" ", "_")
            threshold = thresholds.get(threshold_key, 0)
            color = (50, 255, 50) if value >= threshold else (255, 150, 50)
            
        metric_text = font.render(f"{label}: {value:.1f}{unit}", True, color)
        screen.blit(metric_text, (WIDTH // 2 - metric_text.get_width() // 2, y_pos))
        y_pos += y_spacing
    
    # Draw continue message
    if pygame.time.get_ticks() - result_time > 1500:  # After 1.5 seconds show continue message
        continue_text = font.render("Game will continue... Keep drawing!", True, (200, 200, 200))
        screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT * 3/4))

def metrics_are_stable(current_metrics, last_metrics, threshold=2.0):
    """
    ตรวจสอบว่าเมทริกซ์คงที่หรือไม่โดยเปรียบเทียบกับเมทริกซ์ก่อนหน้า
    
    Args:
        current_metrics: เมทริกซ์ปัจจุบัน
        last_metrics: เมทริกซ์ก่อนหน้า
        threshold: ความแตกต่างสูงสุดที่ยอมรับได้
        
    Returns:
        bool: True ถ้าเมทริกซ์คงที่, False ถ้าไม่คงที่
    """
    if not current_metrics or not last_metrics:
        return False
        
    # ตรวจสอบความแตกต่างของเมทริกซ์หลัก
    metrics_to_check = ['overall_score', 'coverage', 'out_of_bounds', 'similarity']
    
    for metric in metrics_to_check:
        # ตรวจสอบว่าเมทริกซ์มีค่าที่ต้องการหรือไม่
        if metric not in current_metrics or metric not in last_metrics:
            return False
            
        # ตรวจสอบว่าค่าไม่ใช่ None
        if current_metrics[metric] is None or last_metrics[metric] is None:
            return False
            
        # ตรวจสอบความแตกต่าง
        try:
            if abs(current_metrics[metric] - last_metrics[metric]) > threshold:
                return False
        except (TypeError, ValueError):
            # ป้องกันกรณีที่ค่าไม่สามารถลบกันได้
            return False
            
    return True

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
# สร้างออบเจกต์ HandGesture จาก gestures.py 
gesture_recognizer = HandGesture()
shape_measure = ShapeMeasure()

# ตัวแปรควบคุมสถานะเกม
running = True
main_menu = True
difficulty_selected = False
difficulty = None
countdown = False
start_game_page = False
countdown_time = 3
cookie_image = None

# ควบคุมการชนะเกม
game_result = None  # Can be "win", "lose", or None
result_time = None
result_effect_active = False
result_effect_start = None
result_cooldown = 0  # เวลาขั้นต่ำระหว่างการเช็คผลลัพธ์
min_drawing_time = 10000  # เวลาขั้นต่ำที่ต้องวาดก่อนที่จะเช็คผล (5 วินาที)
last_check_time = 0  # เวลาล่าสุดที่เช็คผลลัพธ์
metrics_stable_count = 0  # นับจำนวนครั้งที่เมทริกซ์คงที่
required_stable_metrics = 3  # จำนวนครั้งที่ต้องการให้เมทริกซ์คงที่ก่อนประเมินผล
last_metrics = None  # เมทริกซ์ล่าสุดเพื่อเช็คความคงที่
result_display_time = 4000
# Thresholds for different difficulty levels
WIN_THRESHOLDS = {
    "easy": {
        "overall_score": 60.0,
        "coverage": 55.0,
        "out_of_bounds": 90.0,  # Maximum allowed out of bounds
        "similarity": 60.0
    },
    "normal": {
        "overall_score": 75.0,
        "coverage": 70.0,
        "out_of_bounds": 20.0,  # Maximum allowed out of bounds
        "similarity": 65.0
    },
    "hard": {
        "overall_score": 80.0,
        "coverage": 75.0,
        "out_of_bounds": 15.0,  # Maximum allowed out of bounds
        "similarity": 70.0
    }
}

game_start_time = None        # เวลาเริ่มเกม
game_duration = 60000         # ระยะเวลาเกม 1 นาที (60000 มิลลิวินาที)
game_over_time = None         # เวลาเกมจบ

# ตัวแปรสำหรับการวัดความแม่นยำของการวาด
frame_count = 0
measure_interval = 2  # วัดทุก 2 เฟรม
latest_metrics = None
binary_template_surface = None
show_template = True  # ตัวแปรควบคุมการแสดง binary template

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

                # ดึงพิกัดนิ้วจาก HandTracking
                hand_positions = hand_tracker.get_hand_positions()

                # ดึงพิกัดทั้ง 21 จุดของมือ
                all_hand_landmarks = hand_tracker.get_all_hand_landmarks()
                
                # ปรับพิกัดจากความละเอียดของกล้อง
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
                    # เรียกใช้ process_gesture จาก gestures.py
                    gesture_recognizer.process_gesture(all_hand_landmarks)

                # ตรวจสอบว่าเกมกำลังดำเนินการหรือไม่
                if not gesture_recognizer.game_running:
                    screen.fill((0, 0, 0))
                    print("Rock Hand Sign Detected! Quitting...")
                    title_text = font.render("EXIT GAME BYE!", True, (0, 0, 255))
                    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2,
                                            HEIGHT // 2 - title_text.get_height() // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)  # แสดง Game Over สักพัก
                    running = False  # หยุดเกม

                # สร้างพื้นหลังใหม่ (background) โดยเริ่มจากภาพจากกล้อง
                base_surface = frame_surface.copy()

                # วางรูปคุกกี้ลงบนพื้นหลัง
                cookie_position = (0, 0)  # ค่าเริ่มต้น
                if cookie_image:
                    cookie_image.set_alpha(200)
                    cookie_image_scaled = pygame.transform.scale(cookie_image, (400, 400))
                    cookie_position = (WIDTH // 2 - cookie_image_scaled.get_width() // 2,
                                      HEIGHT // 2 - cookie_image_scaled.get_height() // 2)
                    base_surface.blit(cookie_image_scaled, cookie_position)
                    
                    # แสดง binary template ถ้ามี และเปิดการแสดง
                    if binary_template_surface and show_template:
                        # ปรับขนาดให้ตรงกับ cookie image
                        binary_scaled = pygame.transform.scale(binary_template_surface, (400, 400))
                        # ปรับความโปร่งใสให้เห็น camera feed ด้านหลัง
                        binary_scaled.set_alpha(180)
                        # วาง binary template ลงบนพื้นหลัง
                        base_surface.blit(binary_scaled, cookie_position)

                # นำ drawing_layer (เส้นที่วาด) มาวางซ้อนบนพื้นหลัง
                base_surface.blit(drawing_layer, (0, 0))

                # แสดงผลลงหน้าจอ
                screen.blit(base_surface, (0, 0))
                
                # คำนวณความแม่นยำทุก 2 เฟรมเพื่อลดภาระการประมวลผล
                frame_count += 1
                if difficulty and cookie_image and frame_count % measure_interval == 0:
                    try:
                        # สร้างโฟลเดอร์ assets/bin ถ้ายังไม่มี
                        import os
                        os.makedirs("assets/bin", exist_ok=True)
                        
                        binary_template_path = shape_measure.load_binary_template(difficulty)
                        print(f"Using binary template: {binary_template_path}")
                        
                        # ตรวจสอบว่าไฟล์ binary template มีอยู่จริงหรือไม่
                        if not os.path.exists(binary_template_path):
                            print(f"Warning: Binary template not found at {binary_template_path}")
                            
                            # สร้าง binary template จาก cookie image
                            if difficulty.lower() == "easy":
                                template_name = "easy"
                            elif difficulty.lower() == "normal":
                                template_name = "normal"
                            else:
                                template_name = "hard"
                                
                            cookie_path = f"assets/cookie_template_{template_name}.png"
                            if os.path.exists(cookie_path):
                                import cv2
                                import numpy as np
                                
                                print(f"Creating binary template from {cookie_path}")
                                img = cv2.imread(cookie_path)
                                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                                _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
                                edges = cv2.Canny(binary, 50, 150)
                                edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
                                
                                output_path = f"assets/bin/cookie_template_{template_name}_bin.png"
                                cv2.imwrite(output_path, edges)
                                print(f"Created binary template at {output_path}")
                                
                                binary_template_path = output_path
                        
                        # ตรวจสอบว่า cookie_image_scaled มีขนาดเดียวกับ drawing_layer หรือไม่
                        cookie_size = (cookie_image_scaled.get_width(), cookie_image_scaled.get_height())
                        drawing_size = (drawing_layer.get_width(), drawing_layer.get_height())
                        
                        print(f"Cookie size: {cookie_size}, Drawing size: {drawing_size}")
                        
                        # ตัดขนาด drawing_layer ให้เท่ากับ cookie_image_scaled
                        if cookie_size != drawing_size:
                            print("Resizing for evaluation...")
                            drawing_portion = pygame.Surface(cookie_size, pygame.SRCALPHA)
                            drawing_portion.fill((0, 0, 0, 0))  # โปร่งใส
                            
                            # คำนวณตำแหน่งที่จะ blit (ตำแหน่งเดียวกับ cookie_image บนหน้าจอ)
                            offset_x = WIDTH // 2 - cookie_size[0] // 2
                            offset_y = HEIGHT // 2 - cookie_size[1] // 2
                            
                            # คัดลอกเฉพาะส่วนที่ตรงกับ cookie
                            drawing_portion.blit(drawing_layer, (0, 0), (offset_x, offset_y, cookie_size[0], cookie_size[1]))
                            
                            latest_metrics = shape_measure.evaluate_drawing(
                                drawing_portion, 
                                cookie_image_scaled, 
                                binary_template_path
                            )
                        else:
                            latest_metrics = shape_measure.evaluate_drawing(
                                drawing_layer, 
                                cookie_image_scaled, 
                                binary_template_path
                            )
                    except Exception as e:
                        print(f"Error measuring drawing: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # ถ้าเกิดข้อผิดพลาด ให้ใช้ค่าล่าสุดที่มี
                        if latest_metrics is None:
                            latest_metrics = {
                                'overall_score': 0,
                                'coverage': 0,
                                'out_of_bounds': 0,
                                'accuracy': 0,
                                "similarity": 0
                            }

                # แสดงผลลัพธ์การวัดบนหน้าจอ (ใช้ค่าล่าสุดที่คำนวณไว้)
                if latest_metrics:
                    y_offset = 20
                    # แสดงคะแนนรวม
                    score_text = font.render(f"Score: {latest_metrics['overall_score']:.1f}%", True, (255, 0, 0))
                    screen.blit(score_text, (WIDTH - score_text.get_width() - 20, y_offset))
                    y_offset += 50
                    
                    # แสดงความครอบคลุม
                    coverage_text = font.render(f"Coverage: {latest_metrics['coverage']:.1f}%", True, (0, 255, 0))
                    screen.blit(coverage_text, (WIDTH - coverage_text.get_width() - 20, y_offset))
                    y_offset += 40
                    
                    # แสดงค่านอกขอบเขต
                    out_text = font.render(f"Out of bounds: {latest_metrics['out_of_bounds']:.1f}%", True, (255, 0, 0))
                    screen.blit(out_text, (WIDTH - out_text.get_width() - 20, y_offset))
                    y_offset += 40
                    
                    # แสดงค่าความแม่นยำ
                    if latest_metrics['accuracy'] is not None:
                        accuracy_text = font.render(f"Accuracy: {latest_metrics['accuracy']:.1f}%", True, (0, 0, 255))
                        screen.blit(accuracy_text, (WIDTH - accuracy_text.get_width() - 20, y_offset))
                    
                    # แสดงค่าความคล้ายคลึง
                    if latest_metrics['similarity'] is not None:
                        similarity_text = font.render(f"Similarity: {latest_metrics['similarity']:.1f}%", True, (0, 0, 255))
                        screen.blit(similarity_text, (WIDTH - similarity_text.get_width() - 20, y_offset + 40))

                # แสดงสถานะเปิด/ปิด template
                template_status = "ON" if show_template else "OFF"
                template_text = font.render(f"Template: {template_status} (T)", True, (255, 255, 255))
                screen.blit(template_text, (20, 20))

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
                
                current_time = pygame.time.get_ticks()
                elapsed_since_start = current_time - game_start_time if game_start_time else 0

                # ตรวจสอบเงื่อนไขชนะ-แพ้เฉพาะเมื่อเกมกำลังดำเนินอยู่และไม่มีผลลัพธ์
                if (difficulty and latest_metrics and game_result is None and 
                        elapsed_since_start > min_drawing_time and 
                        current_time - last_check_time > result_cooldown):
                    
                    # ทำสำเนาเมทริกซ์ปัจจุบันเพื่อเปรียบเทียบ
                    current_metrics_copy = {}
                    for key in ['overall_score', 'coverage', 'out_of_bounds', 'similarity']:
                        if key in latest_metrics:
                            current_metrics_copy[key] = latest_metrics[key]
                    
                    # ตรวจสอบความคงที่ของเมทริกซ์เฉพาะเมื่อมีค่า last_metrics
                    if last_metrics:
                        if metrics_are_stable(current_metrics_copy, last_metrics):
                            metrics_stable_count += 1
                            print(f"Metrics stable: {metrics_stable_count}/{required_stable_metrics}")
                        else:
                            # รีเซ็ตตัวนับเมื่อเมทริกซ์เปลี่ยนแปลง
                            metrics_stable_count = 0
                            print("Metrics changed, resetting stability counter")
                    else:
                        # กรณีที่เพิ่งเริ่มต้น ให้ข้ามการตรวจสอบความคงที่ครั้งแรก
                        print("First metrics check, initializing last_metrics")
                    
                    # เก็บเมทริกซ์ปัจจุบันเป็นเมทริกซ์ล่าสุดสำหรับการเปรียบเทียบครั้งต่อไป
                    last_metrics = current_metrics_copy
                    last_check_time = current_time
                    
                    # ประเมินผลเมื่อเมทริกซ์คงที่เพียงพอ
                    if metrics_stable_count >= required_stable_metrics:
                        print(f"Metrics stable for {required_stable_metrics} checks, evaluating win/lose condition")
                        # ตรวจสอบว่ามีการวาดเพียงพอแล้วหรือไม่ (ป้องกันการชนะ/แพ้เมื่อยังไม่ได้วาด)
                        if latest_metrics['coverage'] > 5.0:  # มีการวาดอย่างน้อย 5% ของพื้นที่
                            # ประเมินเงื่อนไขชนะ-แพ้
                            result = evaluate_win_condition(latest_metrics, difficulty)
                            
                            if result:  # ถ้าได้ผลลัพธ์ชนะหรือแพ้
                                game_result = result
                                result_time = current_time
                                result_effect_active = True
                                result_effect_start = current_time
                                metrics_stable_count = 0  # รีเซ็ตตัวนับ
                                print(f"Game result: {result}")
                        else:
                            print("Not enough drawing yet, skipping win/lose evaluation")

                # แสดงข้อความชนะ-แพ้ถ้ามีการกำหนดผลลัพธ์
                if game_result:
                    display_result_message(screen, game_result, latest_metrics, difficulty, time_font, font)
                    
                    # ถ้าแสดงผลเพียงพอแล้ว ให้รีเซ็ตเกมเหมือนตอนหมดเวลา
                    if current_time - result_time > result_display_time:
                        print(f"Game {game_result}, resetting to main menu")
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
                        binary_template_surface = None
                        latest_metrics = None
                        game_result = None
                        result_time = None
                        result_effect_active = False
                        result_effect_start = None
                        metrics_stable_count = 0
                        last_metrics = None
                        pygame.mixer.music.stop()
                        sound_manager.play_bg_music()



                # เมื่อหมดเวลาเกม
                if remaining_time <= 0:
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
                        binary_template_surface = None
                        latest_metrics = None
                        sound_manager.play_bg_music()
                

    # จับ event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # จับการกดปุ่ม
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # กด r เพื่อลบเส้นที่วาด
                drawing_app.reset()
            elif event.key == pygame.K_ESCAPE:
                # กด ESC เพื่อออกจากเกม
                running = False
            elif event.key == pygame.K_t:
                # กด t เพื่อเปิด/ปิดการแสดง template
                show_template = not show_template

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
                        # โหลด binary template ด้วยฟังก์ชันที่สร้างไว้
                        binary_template_surface = load_binary_template("Easy")
                        start_game_page = True
                    elif button_y_start + button_height + button_spacing < mouse_y < button_y_start + button_height * 2 + button_spacing:
                        difficulty = "Normal"
                        sound_manager.play_click_sound()
                        cookie_image = pygame.image.load("assets/cookie_template_normal.png")
                        # โหลด binary template ด้วยฟังก์ชันที่สร้างไว้
                        binary_template_surface = load_binary_template("Normal")
                        start_game_page = True
                    elif button_y_start + (button_height + button_spacing) * 2 < mouse_y < button_y_start + (button_height + button_spacing) * 3:
                        difficulty = "Hard"
                        sound_manager.play_click_sound()
                        cookie_image = pygame.image.load("assets/cookie_template_hard.png")
                        # โหลด binary template ด้วยฟังก์ชันที่สร้างไว้
                        binary_template_surface = load_binary_template("Hard")
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