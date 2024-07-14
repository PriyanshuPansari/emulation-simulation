# File: src/emulators/display_utils.py

import numpy as np
import pygame
from .config import Config

class PygameDisplay:
    def __init__(self, width, height,key_map, config_path="config.json"):
        self.config = Config(config_path)
        pygame.init()
        self.width = width
        self.height = height
        self.scale = self.config.get("display_scale")
        self.screen = pygame.display.set_mode((width * self.scale, height * self.scale))
        pygame.display.set_caption("CHIP-8 Emulator")
        self.keys = [False] * 16
        self.key_map = key_map
        self.bg_color = self.config.get("background_color")
        self.fg_color = self.config.get("foreground_color")

    def update(self, frame):
        frame_surface = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame_surface[frame == 255] = self.fg_color
        frame_surface[frame == 0] = self.bg_color
        surface = pygame.surfarray.make_surface(frame_surface.transpose(1, 0, 2))
        scaled_surface = pygame.transform.scale(surface, (self.width * self.scale, self.height * self.scale))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                key = pygame.key.name(event.key)
                if key in self.key_map:
                    self.keys[self.key_map[key]] = (event.type == pygame.KEYDOWN)
        return False

    def get_keys(self):
        return self.keys

    def close(self):
        pygame.quit()
