# File: src/experiment_tracking/visualize_comparison.py

import sys
sys.path.append('src')
import argparse
import pygame
import numpy as np
from emulators import CHIP8
from emulators.simulate_emulator import EmulatorSimulator
import time
from emulators.config import Config

class SideBySideDisplay:
    def __init__(self, width, height, scale=10,config_path="config.json"):
        self.config = Config(config_path)
        self.width = width
        self.height = height
        self.scale = scale
        pygame.init()
        self.screen = pygame.display.set_mode((width * 2 * scale, height * scale))
        pygame.display.set_caption("CHIP-8 vs AI Simulation")
        self.font = pygame.font.Font(None, 24)
        self.bg_color = self.config.get("background_color")
        self.fg_color = self.config.get("foreground_color")

    def update(self, chip8_frame, ai_frame):
        self.screen.fill((0, 0, 0))

        # Display CHIP-8 frame
        frame_surface = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame_surface[chip8_frame == 255] = self.fg_color
        frame_surface[chip8_frame == 0] = self.bg_color
        surface = pygame.surfarray.make_surface(frame_surface.transpose(1, 0, 2))
        scaled_surface = pygame.transform.scale(surface, (self.width * self.scale, self.height * self.scale))
        self.screen.blit(scaled_surface, (0, 0))

        # Display AI frame
        ai_frame_surface = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        ai_frame_surface[ai_frame == 255] = self.fg_color
        ai_frame_surface[ai_frame == 0] = self.bg_color
        ai_surface = pygame.surfarray.make_surface(ai_frame_surface.transpose(1, 0, 2))
        ai_scaled_surface = pygame.transform.scale(ai_surface, (self.width * self.scale, self.height * self.scale))
        self.screen.blit(ai_scaled_surface, (self.width * self.scale, 0))

        # Add labels
        chip8_label = self.font.render("CHIP-8", True, (255, 255, 255))
        ai_label = self.font.render("AI Simulation", True, (255, 255, 255))
        self.screen.blit(chip8_label, (10, 10))
        self.screen.blit(ai_label, (self.width * self.scale + 10, 10))

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def get_keys(self):
        keys = pygame.key.get_pressed()
        return [keys[pygame.K_x], keys[pygame.K_1], keys[pygame.K_2], keys[pygame.K_3],
                keys[pygame.K_q], keys[pygame.K_w], keys[pygame.K_e], keys[pygame.K_a],
                keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_z], keys[pygame.K_c],
                keys[pygame.K_4], keys[pygame.K_r], keys[pygame.K_f], keys[pygame.K_v]]

    def close(self):
        pygame.quit()

def run_comparison(rom_path, model_path, config_path, sync_interval):
    chip8 = CHIP8(config_path)
    if not chip8.load_rom(rom_path):
        print(f"Failed to load ROM: {rom_path}")
        return

    ai_simulator = EmulatorSimulator(model_path, config_path)

    display = SideBySideDisplay(chip8.screen_width, chip8.screen_height)

    frame_count = 0
    quit = False
    while not quit:
        # Handle input
        quit = display.handle_input()
        keys = display.get_keys()

        # Update CHIP-8 emulator
        chip8.set_keys(keys)
        chip8_frame = chip8.run_frame()

        # Update AI simulator
        ai_simulator.set_keys(keys)
        ai_simulator.step()
        ai_frame = ai_simulator.get_frame()

        # Sync AI simulator with CHIP-8 every sync_interval frames
        if sync_interval > 0 and frame_count % sync_interval == 0:
            ai_simulator.set_frame(chip8_frame)

        # Display frames
        display.update(chip8_frame, ai_frame)

        frame_count += 1
        time.sleep(1/60)  # Cap at 60 FPS

    display.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize CHIP-8 vs AI Simulation')
    parser.add_argument('--rom_path', type=str, required=True, help='Path to the CHIP-8 ROM file')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the trained model file')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file')
    parser.add_argument('--sync_interval', type=int, default=0, help='Interval to sync AI with CHIP-8 (0 for no sync)')
    args = parser.parse_args()

    print("Running CHIP-8 vs AI Simulation comparison...")
    run_comparison(args.rom_path, args.model_path, args.config, args.sync_interval)