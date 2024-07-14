# File: src/emulators/simulate_emulator.py

import torch
import numpy as np
from models.simple_models import SimpleCNN

class EmulatorSimulator:
    def __init__(self, model_path, config_path="config.json"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SimpleCNN(input_channels=1, output_channels=1)
        self.model.load(model_path)
        self.model.to(self.device)
        self.model.eval()

        self.current_frame = None
        self.display = None
        self.keys = [False] * 16  # Assuming 16 keys for CHIP-8

        self.screen_width = 64  # Assuming CHIP-8 dimensions
        self.screen_height = 32
        self.initialize_frame()
    def initialize_frame(self):
        self.current_frame = np.zeros((1, 1, self.screen_height, self.screen_width), dtype=np.float32)

    def set_frame(self, frame):
        # Ensure the frame is in the correct shape and type
        if frame.shape != (self.screen_height, self.screen_width):
            raise ValueError(f"Frame shape should be ({self.screen_height}, {self.screen_width})")
        
        # Normalize the frame to float32 in range [0, 1]
        normalized_frame = frame.astype(np.float32) / 255.0
        
        # Reshape to (1, 1, height, width) for the model input
        self.current_frame = normalized_frame.reshape(1, 1, self.screen_height, self.screen_width)

    def step(self):
        with torch.no_grad():
            input_tensor = torch.from_numpy(self.current_frame).float().to(self.device)
            predicted_frame = self.model(input_tensor)
        
        self.current_frame = predicted_frame.cpu().numpy()

    def get_frame(self):
        return (self.current_frame.squeeze() * 255).astype(np.uint8)

    def set_keys(self, keys):
        self.keys = keys

    def get_keys(self):
        return self.keys

    def get_key_map(self):
        # Return a dummy key map, adjust as needed
        return {str(i): i for i in range(16)}

    # Dummy methods to match CHIP-8 interface
    def load_rom(self, rom_path):
        print(f"Simulating ROM load: {rom_path}")
        return True

    def reset(self):
        self.initialize_frame()

    def get_state(self):
        return self.current_frame

    def set_state(self, state):
        self.current_frame = state

    def run_frame(self):
        self.step()
        return self.get_frame()