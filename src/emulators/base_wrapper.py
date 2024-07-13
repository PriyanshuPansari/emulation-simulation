# File: src/emulators/base_emulator.py

from abc import ABC, abstractmethod
import numpy as np
from typing import List, Tuple

class BaseEmulator(ABC):
    @abstractmethod
    def load_rom(self, rom_path: str) -> bool:
        """
        Load a ROM file into the emulator.
        
        :param rom_path: Path to the ROM file
        :return: True if ROM was loaded successfully, False otherwise
        """
        pass

    @abstractmethod
    def step(self) -> None:
        """
        Execute a single CPU cycle.
        """
        pass

    @abstractmethod
    def get_display(self) -> np.ndarray:
        """
        Get the current display state.
        
        :return: 2D numpy array representing the display
        """
        pass

    @abstractmethod
    def set_keys(self, keys: List[bool]) -> None:
        """
        Set the state of the keypad.
        
        :param keys: List of boolean values representing the state of each key
        """
        pass

    @abstractmethod
    def get_state(self) -> bytes:
        """
        Get the current state of the emulator.
        
        :return: Bytes object representing the current state
        """
        pass

    @abstractmethod
    def set_state(self, state: bytes) -> None:
        """
        Set the state of the emulator.
        
        :param state: Bytes object representing the state to set
        """
        pass

    @abstractmethod
    def run_frame(self) -> np.ndarray:
        """
        Run the emulator for one frame and return the display.
        
        :return: 2D numpy array representing the display
        """
        pass

    @staticmethod
    @abstractmethod
    def get_key_map() -> dict:
        """
        Get the key mapping for the emulator.
        
        :return: Dictionary mapping emulator keys to keyboard keys
        """
        pass