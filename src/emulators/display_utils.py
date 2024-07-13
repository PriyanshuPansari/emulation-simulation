# File: src/emulators/display_utils.py

import numpy as np
import pygame

class PygameDisplay:
    def __init__(self, width, height, scale=10,key_map=None):
        pygame.init()
        self.width = width
        self.height = height
        self.scale = scale
        self.screen = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption("CHIP-8 Emulator")
        self.keys = [False] * 16
        self.key_map = key_map

    def update(self, frame):
        # Convert frame to the correct data type and shape

        # print('\n'.join([''.join(['#' if pixel else '.' for pixel in row]) for row in frame]))
        frame_surface = np.repeat(frame.T[:, :, np.newaxis], 3, axis=2).astype(np.uint8)
        surface = pygame.surfarray.make_surface(frame_surface)
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

