# File: examples/demo_chip8.py

import sys
sys.path.append('src')  # Add the src directory to the Python path
import argparse

from emulators import CHIP8
from emulators.display_utils import PygameDisplay
import numpy as np
import time
import pygame

def run_emulator_pygame(rom_path, num_frames=1000):
    emulator = CHIP8()
    emulator.load_rom(rom_path)

    display = PygameDisplay(emulator.screen_width, emulator.screen_height)

    quit = False
    while not quit and num_frames > 0:
        frame = emulator.run_frame()
        display.update(frame)
        
        quit=display.check_quit()

        time.sleep(1/60)  # Cap at 60 FPS
        num_frames -= 1

    display.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--rom_path', type=str, help='Specify the ROM name')

    args = parser.parse_args()

    print("Running with Pygame display...")
    run_emulator_pygame(args.rom_path)
