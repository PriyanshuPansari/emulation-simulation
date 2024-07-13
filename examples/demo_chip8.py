# File: examples/demo_chip8.py

import sys
sys.path.append('src')  # Add the src directory to the Python path
import argparse

from emulators import CHIP8
from emulators.display_utils import PygameDisplay
import numpy as np
import time
import pygame

def run_emulator_pygame(rom_path, num_frames=None):
    emulator = CHIP8()
    emulator.load_rom(rom_path)

    display = PygameDisplay(emulator.screen_width, emulator.screen_height,key_map=CHIP8.get_key_map())

    quit = False
    frame_count = 0
    while not quit and (num_frames is None or frame_count < num_frames):
        # Handle input
        quit = display.handle_input()
        if quit:
            break

        # Update emulator state
        keys = display.get_keys()
        emulator.set_keys(keys)
        
        # Run a frame
        frame = emulator.run_frame()
        display.update(frame)
        
        time.sleep(1/60)  # Cap at 60 FPS
        frame_count += 1

    display.close()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--rom_path', type=str, help='Specify the ROM name')

    args = parser.parse_args()

    print("Running with Pygame display...")
    run_emulator_pygame(args.rom_path)
