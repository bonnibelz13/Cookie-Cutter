# sound_manager.py

import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.bg_music = "sounds/bg_music.mp3"
        self.click_sound = pygame.mixer.Sound("sounds/click.mp3")  # โหลดเสียงคลิก
        self.in_game_music = "sounds/in_game_music.mp3"

    def play_bg_music(self):
        pygame.mixer.music.load(self.bg_music)
        pygame.mixer.music.play(-1) # loop

    def play_click_sound(self):
        self.click_sound.play()  # เล่นเสียงคลิก 1 ครั้ง

    def play_in_game_music(self):
        pygame.mixer.music.load(self.in_game_music)
        pygame.mixer.music.play(-1) # loop

    def play_failure_sound(self):
        failure_sound = pygame.mixer.Sound(self.click_sound)
        failure_sound.play()