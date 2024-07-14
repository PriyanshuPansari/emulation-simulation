# src/training/trainer.py
import torch
from torch.utils.data import DataLoader
from experiment_tracking.Logger import Logger

class Trainer:
    def __init__(self, model, optimizer, criterion, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.logger = Logger('experiments')
    
    def train(self, train_loader, val_loader, epochs):
        self.model.to(self.device)
        for epoch in range(epochs):
            train_loss = self._train_epoch(train_loader)
            val_loss = self._validate(val_loader)
            
            self.logger.log_metric('train_loss', train_loss, epoch)
            self.logger.log_metric('val_loss', val_loss, epoch)
            
            print(f'Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
    
    def _train_epoch(self, train_loader):
        self.model.train()
        total_loss = 0.0
        for batch in train_loader:
            inputs, targets = batch
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        return total_loss / len(train_loader)
    
    def _validate(self, val_loader):
        self.model.eval()
        total_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                inputs, targets = batch
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                total_loss += loss.item()
        return total_loss / len(val_loader)