# File: examples/demo_chip8.py

import sys
sys.path.append('src')
import argparse
from emulators import CHIP8
from emulators.display_utils import PygameDisplay
import time

def run_emulator_pygame(rom_path, config_path="config.json"):
    emulator = CHIP8(config_path)
    if not emulator.load_rom(rom_path):
        print(f"Failed to load ROM: {rom_path}")
        return

    display = PygameDisplay(emulator.screen_width, emulator.screen_height,emulator.get_key_map(), config_path)
    
    quit = False
    while not quit:
        # Handle input
        quit = display.handle_input() 

        # Update emulator state
        keys = display.get_keys()
        emulator.set_keys(keys)
        
        # Run a frame
        frame = emulator.run_frame()
        display.update(frame)
        
        time.sleep(1/60)  # Cap at 60 FPS

    display.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CHIP-8 ROM')
    parser.add_argument('--rom_path', type=str, required=True, help='Path to the ROM file')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file')
    args = parser.parse_args()
    
    print("Running with Pygame display...")
    run_emulator_pygame(args.rom_path, args.config)