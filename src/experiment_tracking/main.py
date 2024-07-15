# main.py
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from datetime import datetime
import json

app = FastAPI()

# ... (keep previous code for file uploads and database operations)

# Store active WebSocket connections
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process received data if needed
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Function to broadcast messages to all connected clients
async def broadcast_message(message: dict):
    for connection in active_connections:
        await connection.send_json(message)

# Simulate a training loop (in practice, this would be your actual training process)
async def training_loop():
    import asyncio
    import random
    
    for epoch in range(100):
        loss = random.random()
        accuracy = random.random()
        
        # Send update to all connected clients
        await broadcast_message({
            "epoch": epoch,
            "loss": loss,
            "accuracy": accuracy
        })
        
        await asyncio.sleep(1)  # Simulate some processing time

# Start the training loop when the app starts
@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(training_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)