# src/data/preprocessing.py

import numpy as np

def normalize_frame(frame):
    """Normalize the frame data to range [0, 1]"""
    return frame.astype(np.float32) / 255.0

def augment_frame(frame):
    """Apply simple data augmentation (horizontal flip)"""
    return np.fliplr(frame)

class Preprocessor:
    def __init__(self, normalize=True, augment=False):
        self.normalize = normalize
        self.augment = augment

    def preprocess_frame(self, frame):
        if self.normalize:
            frame = normalize_frame(frame)
        if self.augment:
            frame = augment_frame(frame)
        return frame

    def preprocess_dataset(self, frames):
        return np.array([self.preprocess_frame(frame) for frame in frames])

# Example usage
if __name__ == "__main__":
    from capture import create_dataset

    rom_path = "path/to/your/rom.ch8"
    frames, states = create_dataset(rom_path, num_frames=100, sampling_rate=2)

    preprocessor = Preprocessor(normalize=True, augment=True)
    processed_frames = preprocessor.preprocess_dataset(frames)

    print(f"Preprocessed {len(processed_frames)} frames")
    print(f"Sample frame shape: {processed_frames[0].shape}")
    print(f"Sample frame min value: {processed_frames[0].min()}")
    print(f"Sample frame max value: {processed_frames[0].max()}")