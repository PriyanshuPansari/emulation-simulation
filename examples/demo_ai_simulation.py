# File: examples/demo_ai_simulation.py

import sys
sys.path.append('src')
import argparse
from emulators.display_utils import PygameDisplay
from emulators.simulate_emulator import EmulatorSimulator
import time

def run_ai_simulation(model_path, config_path="config.json"):
    simulator = EmulatorSimulator(model_path)
    
    # Assuming CHIP-8 dimensions, adjust if needed
    display = PygameDisplay(64, 32, simulator.get_keys(), config_path)
    # simulator.set_display(display)

    quit = False
    while not quit:
        # Handle input
        quit = display.handle_input() 
        
        # Update simulator state
        keys = display.get_keys()
        simulator.set_keys(keys)
        
        # Run a frame
        simulator.step()
        frame = simulator.get_frame()
        display.update(frame)
        
        time.sleep(1/60)  # Cap at 60 FPS

    display.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run AI Simulation')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the trained model file')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file')
    args = parser.parse_args()
    
    print("Running AI Simulation with Pygame display...")
    run_ai_simulation(args.model_path, args.config)