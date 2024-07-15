# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect
import asyncio
import threading
import time
import os
import numpy as np
import base64
import io
from PIL import Image
from emulators.simulate_emulator import EmulatorSimulator
from emulators import CHIP8
from experiment_tracking.Logger import Logger

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = Logger()

# Global variables to store emulator states
chip8 = None
simulator = None
current_frame = None
emulation_thread = None
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.get("/api/experiments")
async def get_experiments():
    try:
        return logger.get_experiment_list()
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/test")
async def test_route():
    return {"message": "Test route working"}

@app.get("/api/experiments/{experiment_id}/metrics")
async def get_experiment_metrics(experiment_id: str):
    print(f"Received request for experiment: {experiment_id}")
    logger.experiment_name = experiment_id
    try:
        print("Attempting to get metrics")
        metrics = logger.get_saved_metrics()
        if not metrics:
            print("No metrics found")
            raise HTTPException(status_code=404, detail="Experiment not found or no metrics available")
        print(f"Returning metrics: {metrics}")
        return JSONResponse(content=jsonable_encoder(metrics))
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/upload")
async def upload_files(
    rom: UploadFile = File(...),
    model: UploadFile = File(...),
    config_path: str = Form("config.json"),
    sync_interval: int = Form(0)
):
    global chip8, simulator, current_frame, emulation_thread
    
    rom_path = os.path.join(UPLOAD_FOLDER, rom.filename)
    model_path = os.path.join(UPLOAD_FOLDER, model.filename)
    
    with open(rom_path, "wb") as buffer:
        buffer.write(await rom.read())
    with open(model_path, "wb") as buffer:
        buffer.write(await model.read())
    
    chip8 = CHIP8(config_path)
    chip8.load_rom(rom_path)
    simulator = EmulatorSimulator(model_path)
    current_frame = np.zeros((32, 64), dtype=np.uint8)
    
    if emulation_thread is None or not emulation_thread.is_alive():
        emulation_thread = threading.Thread(target=emulation_loop, args=(sync_interval,), daemon=True)
        emulation_thread.start()
    
    return JSONResponse(content={"message": "Emulation started successfully"}, status_code=200)

def emulation_loop(sync_interval):
    global chip8, simulator, current_frame
    frame_count = 0
    while True:
        chip8_frame = chip8.run_frame()
        current_frame = chip8_frame
        frames = {
            "CHIP-8": encode_frame(chip8_frame)
        }
        simulator.set_frame(chip8_frame)
        ai_frame = simulator.run_frame()
        frames["AI Simulation"] = encode_frame(ai_frame)
        # We'll handle WebSocket broadcasting in a separate function
        broadcast_frames(frames)
        frame_count += 1
        if sync_interval > 0 and frame_count % sync_interval == 0:
            simulator.set_frame(chip8_frame)
        time.sleep(1/60)  # Cap at 60 FPS

def encode_frame(frame):
    return (frame.astype(np.uint8)).tolist()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def broadcast_frames(frames):
    asyncio.create_task(manager.broadcast(frames))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)