import pygame
import sys
import time
import cv2
import numpy as np

from module.drawing import DrawingApp
from module.hand_tracking import HandTracking
from module.sound_manager import SoundManager

class CookieCutterGame:
    # Constants
    WIDTH, HEIGHT = 1200, 900
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BUTTON_COLOR = (0, 0, 0)
    BUTTON_HOVER_COLOR = (50, 50, 50)
    BUTTON_BORDER_COLOR = (255, 0, 0)
    FONT_COLOR = (255, 0, 0)
    ASSET_PATH = "assets/"
    GAME_DURATION_MS = 60000  # 1 minute in milliseconds
    COUNTDOWN_SECONDS = 3
    PREPARATION_SECONDS = 5  # เวลาเตรียมพร้อม 5 วินาที
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Cookie Cutter Game")
        
        # Initialize fonts
        self.font = pygame.font.SysFont("Arial", 40)
        self.time_font = pygame.font.SysFont("Arial", 60)
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        self.hand_tracker = HandTracking()
        
        # Game state variables
        self.running = True
        # main_menu -> difficulty_selection -> starting_game -> countdown -> preparation -> gameplay -> game_over
        self.game_state = "main_menu"
        self.difficulty = None
        self.cookie_image = None
        self.processed_image_path = None
        
        # Drawing app (will be initialized when difficulty is selected)
        self.drawing_app = None
        
        # Game result variables
        self.game_result = None  # "success" or "failure"
        
        # Timer variables
        self.countdown_time = self.COUNTDOWN_SECONDS
        self.countdown_start = None
        self.preparation_time = self.PREPARATION_SECONDS
        self.preparation_start = None
        self.game_start_time = None
        self.game_over_time = None
        
        # Start background music
        if not pygame.mixer.music.get_busy():
            self.sound_manager.play_bg_music()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.screen.fill(self.BLACK)
            
            # Handle current game state
            if self.game_state == "main_menu":
                self.render_main_menu()
            elif self.game_state == "difficulty_selection":
                self.render_difficulty_selection()
            elif self.game_state == "starting_game":
                self.render_starting_game()
            elif self.game_state == "countdown":
                self.handle_countdown()
            elif self.game_state == "preparation":
                self.handle_preparation()
            elif self.game_state == "gameplay":
                self.handle_gameplay()
            elif self.game_state == "game_over":
                self.handle_game_over()
            
            # Process events
            self.handle_events()
            
            pygame.display.flip()
        
        # Clean up resources
        self.hand_tracker.stop()
        pygame.quit()
        sys.exit()
    
    def render_main_menu(self):
        """Render the main menu screen"""
        title_text = self.font.render("Cookie Cutter", True, self.RED)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2,
                               self.HEIGHT // 4 - title_text.get_height() // 2))
        
        self.draw_button("Play Game", self.WIDTH // 4 - 150, self.HEIGHT // 2 - 40, 300, 80,
                  self.BUTTON_COLOR, self.BUTTON_HOVER_COLOR, self.BUTTON_BORDER_COLOR)
        self.draw_button("Quit", self.WIDTH // 4 - 150, self.HEIGHT // 2 + 100, 300, 80,
                  self.BUTTON_COLOR, self.BUTTON_HOVER_COLOR, self.BUTTON_BORDER_COLOR)
    
    def render_difficulty_selection(self):
        """Render the difficulty selection screen"""
        title_text = self.font.render("Select Difficulty", True, self.RED)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2,
                               self.HEIGHT // 5 - title_text.get_height() // 2))
        
        button_width = 300
        button_height = 80
        button_spacing = 20
        button_y_start = self.HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2
        
        self.draw_button("Easy", self.WIDTH // 2 - button_width // 2, button_y_start,
                  button_width, button_height, self.BUTTON_COLOR, self.BUTTON_HOVER_COLOR, self.BUTTON_BORDER_COLOR)
        self.draw_button("Normal", self.WIDTH // 2 - button_width // 2,
                  button_y_start + button_height + button_spacing,
                  button_width, button_height, self.BUTTON_COLOR, self.BUTTON_HOVER_COLOR, self.BUTTON_BORDER_COLOR)
        self.draw_button("Hard", self.WIDTH // 2 - button_width // 2,
                  button_y_start + (button_height + button_spacing) * 2,
                  button_width, button_height, self.BUTTON_COLOR, self.BUTTON_HOVER_COLOR, self.BUTTON_BORDER_COLOR)
    
    def render_starting_game(self):
        """Render the starting game screen"""
        title_text = self.font.render("Starting Game!", True, self.RED)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2,
                               self.HEIGHT // 4 - title_text.get_height() // 2))
    
    def handle_countdown(self):
        """Handle the countdown before preparation starts"""
        countdown_text = self.font.render(str(self.countdown_time), True, self.RED)
        self.screen.blit(countdown_text, (self.WIDTH // 2 - countdown_text.get_width() // 2,
                                   self.HEIGHT // 2 - countdown_text.get_height() // 2))
        
        if time.time() - self.countdown_start >= 1 and self.countdown_time > 0:
            self.countdown_time -= 1
            self.countdown_start = time.time()
        
        if self.countdown_time == 0:
            self.game_state = "preparation"
            self.preparation_start = time.time()
            self.preparation_time = self.PREPARATION_SECONDS
    
    def handle_preparation(self):
        """ช่วงเตรียมพร้อมก่อนเริ่มเกมจริง แสดงจุดแดงติดตามนิ้วแต่ยังไม่วาดเส้น"""
        # Get camera frame
        frame_surface = self.hand_tracker.get_frame()
        if not frame_surface:
            return
        
        # Scale frame to screen size
        frame_surface = pygame.transform.scale(frame_surface, (self.WIDTH, self.HEIGHT))
        
        # Get hand positions and scale to screen coordinates
        hand_positions = self.hand_tracker.get_hand_positions()
        if hand_positions:
            scale_x = self.WIDTH / self.hand_tracker.original_width
            scale_y = self.HEIGHT / self.hand_tracker.original_height
            hand_positions = [(int(x * scale_x), int(y * scale_y)) for (x, y) in hand_positions]
        
        # Create background with camera frame
        base_surface = frame_surface.copy()
        
        # Add cookie template
        if self.cookie_image:
            self.cookie_image.set_alpha(200)
            cookie_image_scaled = pygame.transform.scale(self.cookie_image, (400, 400))
            base_surface.blit(cookie_image_scaled, (self.WIDTH // 2 - cookie_image_scaled.get_width() // 2,
                                                    self.HEIGHT // 2 - cookie_image_scaled.get_height() // 2))
        
        # แสดงจุดแดงขนาดใหญ่สำหรับติดตามนิ้ว
        if hand_positions:
            for pos in hand_positions:
                pygame.draw.circle(base_surface, self.RED, pos, 15)  # วาดวงกลมขนาด 15 พิกเซล
        
        # Display to screen
        self.screen.blit(base_surface, (0, 0))
        
        # Display preparation message
        prep_text = self.font.render("เตรียมพร้อม...", True, self.YELLOW)
        self.screen.blit(prep_text, (self.WIDTH // 2 - prep_text.get_width() // 2,
                                self.HEIGHT // 4 - prep_text.get_height() // 2))
        
        # Display hand position guidance
        hand_text = self.font.render("วางมือของคุณให้พร้อม", True, self.YELLOW)
        self.screen.blit(hand_text, (self.WIDTH // 2 - hand_text.get_width() // 2,
                                self.HEIGHT // 4 + 50 - hand_text.get_height() // 2))
        
        # Display countdown
        time_text = self.time_font.render(str(self.preparation_time), True, self.YELLOW)
        self.screen.blit(time_text, (self.WIDTH // 2 - time_text.get_width() // 2,
                                self.HEIGHT // 2 + 200 - time_text.get_height() // 2))
        
        # Update countdown
        if time.time() - self.preparation_start >= 1 and self.preparation_time > 0:
            self.preparation_time -= 1
            self.preparation_start = time.time()
        
        # When preparation is done, start the game
        if self.preparation_time == 0:
            self.game_state = "gameplay"
            self.game_start_time = pygame.time.get_ticks()
            self.sound_manager.play_in_game_music()
            # รีเซ็ต drawing app เพื่อให้แน่ใจว่าเริ่มวาดเส้นใหม่
            self.drawing_app.reset()
    
    def handle_gameplay(self):
        """Handle the actual gameplay"""
        # Get camera frame
        frame_surface = self.hand_tracker.get_frame()
        if not frame_surface:
            return
        
        # Scale frame to screen size
        frame_surface = pygame.transform.scale(frame_surface, (self.WIDTH, self.HEIGHT))
        
        # Get hand positions and scale to screen coordinates
        hand_positions = self.hand_tracker.get_hand_positions()
        if hand_positions:
            scale_x = self.WIDTH / self.hand_tracker.original_width
            scale_y = self.HEIGHT / self.hand_tracker.original_height
            hand_positions = [(int(x * scale_x), int(y * scale_y)) for (x, y) in hand_positions]
        
        # Update drawing layer
        self.drawing_app.update(hand_positions)
        
        # Check if drawing is complete
        if self.drawing_app.is_drawing_complete():
            self.game_result = "success"
            self.game_state = "game_over"
            self.game_over_time = pygame.time.get_ticks()
            pygame.mixer.music.stop()
            self.sound_manager.play_click_sound()  # ใช้เสียงคลิกแทนเสียงสำเร็จชั่วคราว
            return
            
        # Check if drawing is failed (out of bounds)
        if self.drawing_app.is_failed():
            self.game_result = "failure"
            self.game_state = "game_over"
            self.game_over_time = pygame.time.get_ticks()
            pygame.mixer.music.stop()
            self.sound_manager.play_click_sound()  # ใช้เสียงคลิกแทนเสียงล้มเหลวชั่วคราว
            return
        
        # Create background with camera frame
        base_surface = frame_surface.copy()
        
        # Get the combined surface with template and drawing
        combined_surface = self.drawing_app.draw_combined()
        base_surface.blit(combined_surface, (0, 0))
        
        # Display to screen
        self.screen.blit(base_surface, (0, 0))
        
        # Display game stats
        self.display_game_stats()
        
        # Calculate and display remaining time
        remaining_time = self.display_game_timer()
        
        # Check if time is up
        if remaining_time <= 600:  # 0.6 seconds threshold
            self.game_result = "timeout"
            self.game_state = "game_over"
            self.game_over_time = pygame.time.get_ticks()
            pygame.mixer.music.stop()
    
    def display_game_stats(self):
        """Display game statistics during gameplay"""
        stats = self.drawing_app.get_completion_stats()
        
        # Display coverage
        coverage_text = self.font.render(f"Coverage_percent: {stats['coverage_percent']:.1f}%", True, self.RED)
        self.screen.blit(coverage_text, (20, 150))
        
        # Display similarity
        similarity_text = self.font.render(f"Similarity: {stats['shape_similarity']:.2f}", True, self.RED)
        self.screen.blit(similarity_text, (20, 200))
        
        # Display out of bounds count
        out_text = self.font.render(f"Out of bounds: {stats['out_of_bounds_count']}", True, 
                                   self.RED if stats['out_of_bounds_count'] > 0 else self.GREEN)
        self.screen.blit(out_text, (20, 250))
    
    def display_game_timer(self):
        """Display the game timer"""
        elapsed_time = pygame.time.get_ticks() - self.game_start_time
        remaining_time = max(0, self.GAME_DURATION_MS - elapsed_time)
        minutes = remaining_time // 60000
        seconds = (remaining_time // 1000) % 60
        time_text = self.time_font.render(f"{minutes:02}:{seconds:02}", True, self.RED)
        self.screen.blit(time_text, ((self.WIDTH - time_text.get_width()) // 2, 80))
        return remaining_time
    
    def handle_game_over(self):
        """Handle game over state"""
        # Display game over message based on result
        if self.game_result == "success":
            title_text = self.font.render("WIN", True, self.GREEN)
            stats = self.drawing_app.get_completion_stats()
            score_text = self.font.render(f"Score: {stats['shape_similarity'] * 100:.0f}", True, self.GREEN)
            self.screen.blit(score_text, (self.WIDTH // 2 - score_text.get_width() // 2,
                                  self.HEIGHT // 2 + 50))
        elif self.game_result == "failure":
            title_text = self.font.render("Fail", True, self.RED)
        else:  # timeout
            title_text = self.font.render("Time out", True, self.RED)
            
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2,
                               self.HEIGHT // 2 - title_text.get_height() // 2))
        
        # Return to main menu after a delay
        if pygame.time.get_ticks() - self.game_over_time >= 3000:
            self.reset_game_state()
            self.sound_manager.play_bg_music()
    
    def reset_game_state(self):
        """Reset the game state to initial values"""
        self.game_state = "main_menu"
        self.difficulty = None
        self.countdown_time = self.COUNTDOWN_SECONDS
        self.preparation_time = self.PREPARATION_SECONDS
        self.game_start_time = None
        self.cookie_image = None
        self.processed_image_path = None
        self.drawing_app = None
        self.game_over_time = None
        self.game_result = None
    
    def draw_button(self, text, x, y, width, height, color, hover_color, border_color):
        """Draw a button with hover effect"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        button_color = hover_color if (x < mouse_x < x + width and y < mouse_y < y + height) else color
        
        pygame.draw.rect(self.screen, button_color, (x, y, width, height))
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 5)
        
        text_surface = self.font.render(text, True, self.FONT_COLOR)
        self.screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2,
                               y + (height - text_surface.get_height()) // 2))
    
    def handle_click_on_main_menu(self, mouse_x, mouse_y):
        """Handle click events on the main menu"""
        if self.WIDTH // 4 - 150 < mouse_x < self.WIDTH // 4 + 150:
            if self.HEIGHT // 2 - 40 < mouse_y < self.HEIGHT // 2 + 40:
                self.sound_manager.play_click_sound()
                self.game_state = "difficulty_selection"
                return True
            elif self.HEIGHT // 2 + 100 < mouse_y < self.HEIGHT // 2 + 180:
                self.sound_manager.play_click_sound()
                self.running = False
                return True
        return False
    
    def handle_click_on_difficulty(self, mouse_x, mouse_y):
        """Handle click events on the difficulty selection screen"""
        button_width = 300
        button_height = 80
        button_spacing = 20
        button_y_start = self.HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2
        
        # ค่าพารามิเตอร์สำหรับแต่ละความยาก
        difficulty_params = {
            "Easy": {
                "template": f"{self.ASSET_PATH}template/cookie_template_easy.png",
                "processed": f"{self.ASSET_PATH}processed/cookie_template_easy.png",
                "max_out_of_bounds": 10000000,   # ปรับให้ยอมออกนอกกรอบได้มากขึ้น (เดิม 50)
                "min_coverage": 5,         # ลดเปอร์เซ็นต์การครอบคลุมลง (เดิม 70)
                "similarity_threshold": 0.1,  # ลดความคล้ายลง (เดิม 0.7)
                "line_thickness": 15         # เพิ่มพารามิเตอร์ความหนาของเส้น
            },
            "Normal": {
                "template": f"{self.ASSET_PATH}template/cookie_template_normal.png",
                "processed": f"{self.ASSET_PATH}processed/cookie_template_normal.png",
                "max_out_of_bounds": 30,
                "min_coverage": 80,
                "similarity_threshold": 0.75,
                "line_thickness": 15
            },
            "Hard": {
                "template": f"{self.ASSET_PATH}template/cookie_template_hard.png",
                "processed": f"{self.ASSET_PATH}processed/cookie_template_hard.png",
                "max_out_of_bounds": 20,
                "min_coverage": 90,
                "similarity_threshold": 0.8,
                "line_thickness": 15
            }
        }
        
        if self.WIDTH // 2 - button_width // 2 < mouse_x < self.WIDTH // 2 + button_width // 2:
            for i, difficulty in enumerate(["Easy", "Normal", "Hard"]):
                button_y = button_y_start + i * (button_height + button_spacing)
                if button_y < mouse_y < button_y + button_height:
                    self.difficulty = difficulty
                    params = difficulty_params[difficulty]
                    
                    # ตั้งค่าพารามิเตอร์ตามความยาก
                    self.cookie_image = pygame.image.load(params["template"])
                    self.processed_image_path = params["processed"]
                    
                    # สร้าง DrawingApp ด้วยพารามิเตอร์ที่เหมาะสม
                    self.drawing_app = DrawingApp(
                        self.WIDTH, 
                        self.HEIGHT,
                        params["template"],
                        params["processed"],
                        params["max_out_of_bounds"],
                        params["min_coverage"],
                        params["similarity_threshold"],
                        params["line_thickness"]  # ส่งพารามิเตอร์ความหนาของเส้นเข้าไป
                    )
                    return True
        return False
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.drawing_app:
                    self.drawing_app.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_s and self.game_state == "gameplay":
                    # ปุ่ม S สำหรับทำให้เกมจบอย่างรวดเร็ว (สำหรับ debug)
                    self.game_result = "success"
                    self.game_state = "game_over"
                    self.game_over_time = pygame.time.get_ticks()
                    pygame.mixer.music.stop()
                elif event.key == pygame.K_p and self.game_state == "preparation":
                    # ปุ่ม P สำหรับข้ามช่วงเตรียมพร้อม (สำหรับ debug)
                    self.game_state = "gameplay"
                    self.game_start_time = pygame.time.get_ticks()
                    self.sound_manager.play_in_game_music()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if self.game_state == "main_menu":
                    if self.handle_click_on_main_menu(mouse_x, mouse_y):
                        continue
                
                elif self.game_state == "difficulty_selection":
                    if self.handle_click_on_difficulty(mouse_x, mouse_y):
                        self.sound_manager.play_click_sound()
                        self.game_state = "starting_game"
                
                elif self.game_state == "starting_game" and self.cookie_image:
                    pygame.mixer.music.stop()
                    print(f"Starting Game with Difficulty: {self.difficulty}")
                    self.game_state = "countdown"
                    self.countdown_start = time.time()


if __name__ == "__main__":
    game = CookieCutterGame()
    game.run()