# File: src/emulators/chip8.py

import numpy as np
from typing import List
from .base_wrapper import BaseEmulator
from .emulator_module import CHIP8Emulator as _CHIP8Emulator
import os
from .config import Config

class CHIP8(BaseEmulator):
    def __init__(self,config_path="config.json"):
        self._emulator = _CHIP8Emulator()
        self.screen_width = 64
        self.screen_height = 32
        self.config = Config(config_path)
        self.clock_speed = self.config.get("clock_speed")
       

    def load_rom(self, rom_path: str) -> bool:
        return self._emulator.load_rom(rom_path)

    def step(self) -> None:
        self._emulator.step()

    def get_display(self) -> np.ndarray:
        frame = self._emulator.get_frame()
        return frame.reshape((self.screen_height, self.screen_width))

    def set_keys(self, keys: List[bool]) -> None:
        if len(keys) != 16:
            raise ValueError("Keys must be a list of 16 boolean values")
        self._emulator.set_input(keys)

    def get_state(self) -> bytes:
        return bytes(self._emulator.get_state())

    def set_state(self, state: bytes) -> None:
        self._emulator.set_state(list(state))

    def save_state(self, filepath):
        state = self.get_state()
        with open(filepath, 'wb') as f:
            f.write(state)

    def load_state(self, filepath):
        if not os.path.exists(filepath):
            return False
        with open(filepath, 'rb') as f:
            state = f.read()
        self.set_state(state)
        return True

    def run_frame(self) -> np.ndarray:
        for _ in range( self.clock_speed // 60):  # Assuming 600Hz CPU clock and 60Hz display refresh
            self.step()
        return self.get_display()
    
    def debug_display(self) -> str:
        frame = self.get_display()
        return '\n'.join([''.join(['#' if pixel else '.' for pixel in row]) for row in frame])
    @staticmethod
    def get_key_map() -> dict:
        return {
            '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
            'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
            'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
            'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
        }