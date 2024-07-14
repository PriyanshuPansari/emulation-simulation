# File: src/emulators/config.py

import json
import os

DEFAULT_CONFIG = {
    "clock_speed": 600,
    "display_scale": 10,
    "background_color": [0, 0, 0],
    "foreground_color": [255, 255, 255],
    "sound_enabled": True
}

class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()