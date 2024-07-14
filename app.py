# File: app.py

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from emulators.simulate_emulator import EmulatorSimulator
from emulators import CHIP8
import numpy as np
import base64
import io
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Global variables to store emulator states
chip8 = None
simulators = {}
current_frame = None
training_logs = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_emulation', methods=['POST'])
def start_emulation():
    global chip8, simulators, current_frame
    rom_path = request.json['rom_path']
    model_paths = request.json['model_paths']
    
    chip8 = CHIP8('config.json')
    chip8.load_rom(rom_path)
    
    simulators = {
        model_path: EmulatorSimulator(model_path) for model_path in model_paths
    }
    
    current_frame = np.zeros((32, 64), dtype=np.uint8)
    
    threading.Thread(target=emulation_loop, daemon=True).start()
    return jsonify({"status": "success"})

def emulation_loop():
    global chip8, simulators, current_frame
    while True:
        chip8_frame = chip8.run_frame()
        current_frame = chip8_frame
        
        frames = {
            "CHIP-8": encode_frame(chip8_frame)
        }
        
        for name, simulator in simulators.items():
            simulator.set_frame(chip8_frame)
            ai_frame = simulator.run_frame()
            frames[name] = encode_frame(ai_frame)
        
        socketio.emit('frames', frames)
        time.sleep(1/60)  # Cap at 60 FPS

def encode_frame(frame):
    img = Image.fromarray(frame)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@app.route('/start_training', methods=['POST'])
def start_training():
    model_name = request.json['model_name']
    training_logs[model_name] = []
    threading.Thread(target=simulate_training, args=(model_name,), daemon=True).start()
    return jsonify({"status": "success"})

def simulate_training(model_name):
    for i in range(100):
        loss = np.random.rand()
        accuracy = np.random.rand()
        training_logs[model_name].append({
            "epoch": i,
            "loss": loss,
            "accuracy": accuracy
        })
        socketio.emit('training_update', {
            "model_name": model_name,
            "epoch": i,
            "loss": loss,
            "accuracy": accuracy
        })
        time.sleep(1)  # Simulate training time

if __name__ == '__main__':
    socketio.run(app, debug=True)