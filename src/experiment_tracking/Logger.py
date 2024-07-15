import os
import json
import asyncio
from datetime import datetime

class Logger:
    def __init__(self, log_dir='experiments', experiment_name=None):
        self.log_dir = log_dir
        self.experiment_name = experiment_name or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.experiment_dir = os.path.join(log_dir, self.experiment_name)
        os.makedirs(self.experiment_dir, exist_ok=True)
        self.metrics = {}
        self.artifacts = {}
        self.websocket_connections = []

    def log_metric(self, name, value, step=None):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append((step, value))
        self._save_metrics()
        asyncio.create_task(self._broadcast_metric(name, value, step))

    def log_artifact(self, name, file_path):
        self.artifacts[name] = file_path
        self._save_artifacts()

    def save(self):
        self._save_metrics()
        self._save_artifacts()

    def _save_metrics(self):
        with open(os.path.join(self.experiment_dir, 'metrics.json'), 'w') as f:
            json.dump(self.metrics, f)

    def _save_artifacts(self):
        with open(os.path.join(self.experiment_dir, 'artifacts.json'), 'w') as f:
            json.dump(self.artifacts, f)

    def add_websocket(self, websocket):
        self.websocket_connections.append(websocket)

    def remove_websocket(self, websocket):
        self.websocket_connections.remove(websocket)

    async def _broadcast_metric(self, name, value, step):
        message = json.dumps({
            'type': 'metric',
            'name': name,
            'value': value,
            'step': step
        })
        for websocket in self.websocket_connections:
            await websocket.send_text(message)

    async def broadcast_message(self, message):
        for websocket in self.websocket_connections:
            await websocket.send_text(json.dumps(message))

    def get_experiment_id(self):
        return self.experiment_name

    def get_saved_metrics(self):
        self.experiment_dir = os.path.join(self.log_dir, self.experiment_name)
        print(self.experiment_dir)
        metrics_file = os.path.join(self.experiment_dir, 'metrics.json')
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                return json.load(f)
        return {}

    def get_experiment_list(self):
        return [d for d in os.listdir(self.log_dir) if os.path.isdir(os.path.join(self.log_dir, d))]