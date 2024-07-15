# main.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from models.simple_models import SimpleCNN
from training.trainer import Trainer
from data.capture import create_dataset
from data.preprocessing import Preprocessor
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from experiment_tracking.Logger import Logger

app = FastAPI()
# 
# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Store active WebSocket connections
logger = Logger('experiments')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.add_websocket(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process received data if needed
    except WebSocketDisconnect:
        logger.remove_websocket(websocket)

async def main_async():
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
    trainer = Trainer(model, optimizer, criterion, logger=logger)
    await trainer.train_async(train_loader, val_loader, epochs=2000)

    # Save the model
    os.makedirs('models', exist_ok=True)
    torch.save(model.state_dict(), f'models/simple_cnn_{trainer.logger.experiment_name}.pth')
    trainer.logger.log_artifact('model', f'models/simple_cnn_{trainer.logger.experiment_name}.pth')
    trainer.logger.save()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main_async())   

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)