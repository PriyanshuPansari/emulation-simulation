# src/data/capture.py

import numpy as np
from emulators.chip8_wrapper import CHIP8

class DataCapture:
    def __init__(self, emulator, sampling_rate=1):
        self.emulator = emulator
        self.sampling_rate = sampling_rate
        self.frame_count = 0

    def capture_frame(self):
        frame = self.emulator.get_display()
        return np.array(frame, dtype=np.uint8).reshape((32, 64))

    def capture_state(self):
        return self.emulator.get_state()

    def run_and_capture(self, num_frames):
        frames = []
        states = []
        for _ in range(num_frames):
            self.emulator.run_frame()
            self.frame_count += 1
            if self.frame_count % self.sampling_rate == 0:
                frames.append(self.capture_frame())
                states.append(self.capture_state())
        return frames, states

def create_dataset(rom_path, num_frames, sampling_rate=1):
    emulator = CHIP8()
    emulator.load_rom(rom_path)
    
    capturer = DataCapture(emulator, sampling_rate)
    frames, states = capturer.run_and_capture(num_frames)
    
    return frames, states

# Example usage
if __name__ == "__main__":
    rom_path = "chip8-roms/games/Airplane.ch8"
    frames, states = create_dataset(rom_path, num_frames=1000, sampling_rate=4)
    print(f"Captured {len(frames)} frames and states")