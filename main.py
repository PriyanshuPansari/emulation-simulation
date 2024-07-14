# main.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from models.simple_models import SimpleCNN
from training.trainer import Trainer
from data.capture import create_dataset
from data.preprocessing import Preprocessor
import os

def main():
    # Data capture and preprocessing
    rom_path = "chip8-roms/games/Airplane.ch8"
    frames, states = create_dataset(rom_path, num_frames=100, sampling_rate=2)

    preprocessor = Preprocessor(normalize=True, augment=True)
    processed_frames = preprocessor.preprocess_dataset(frames)

    processed_frames = processed_frames.reshape(-1, 1, 32, 64)
    # Create dataset and dataloaders
    X = processed_frames[:-1]  # Input frames
    y = processed_frames[1:]   # Target frames (next frame prediction)
    dataset = TensorDataset(torch.from_numpy(X), torch.from_numpy(y))
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(dataset, batch_size=32)  # Using same data for simplicity
    
    # Model, optimizer, and loss function
    model = SimpleCNN(input_channels=1, output_channels=1)  # Adjust channels as needed
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    # Create trainer and train
    trainer = Trainer(model, optimizer, criterion)
    trainer.train(train_loader, val_loader, epochs=10)
    
    # Save the model
    os.makedirs('models', exist_ok=True)
    model.save(f'models/simple_cnn_{trainer.logger.experiment_id}.pth')
    trainer.logger.log_artifact('model', f'models/simple_cnn_{trainer.logger.experiment_id}.pth')
    trainer.logger.save()

if __name__ == "__main__":
    main() 