# src/experiment_tracking/logger.py
import json
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"experiment_{self.experiment_id}.json")
        self.data = {"metrics": [], "parameters": {}, "artifacts": []}
    
    def log_metric(self, name, value, step):
        self.data["metrics"].append({"name": name, "value": value, "step": step})
    
    def log_parameter(self, name, value):
        self.data["parameters"][name] = value
    
    def log_artifact(self, name, file_path):
        self.data["artifacts"].append({"name": name, "path": file_path})
    
    def save(self):
        os.makedirs(self.log_dir,exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def load(self, experiment_id):
        log_file = os.path.join(self.log_dir, f"experiment_{experiment_id}.json")
        with open(log_file, 'r') as f:
            self.data = json.load(f)