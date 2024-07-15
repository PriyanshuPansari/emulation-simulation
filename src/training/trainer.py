# src/training/trainer.py
import torch
from torch.utils.data import DataLoader
from experiment_tracking.Logger import Logger
import asyncio

class Trainer:
    def __init__(self, model, optimizer, criterion, device='cuda' if torch.cuda.is_available() else 'cpu', logger=None):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.logger = logger or Logger('experiments')

    async def train_async(self, train_loader, val_loader, epochs):
        self.model.to(self.device)
        for epoch in range(epochs):
            train_loss = await self._train_epoch_async(train_loader)
            val_loss = await self._validate_async(val_loader)
            
            self.logger.log_metric('train_loss', train_loss, epoch)
            self.logger.log_metric('val_loss', val_loss, epoch)
            
            print(f'Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
            
            await self.logger.broadcast_message({
                'type': 'epoch_summary',
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss
            })

    async def _train_epoch_async(self, train_loader):
        self.model.train()
        total_loss = 0.0
        for i, batch in enumerate(train_loader):
            inputs, targets = batch
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            if i % 10 == 0:  # Log every 10 batches
                self.logger.log_metric('batch_loss', loss.item(), i)
            await asyncio.sleep(0)  # Allow other async operations to run
        return total_loss / len(train_loader)

    async def _validate_async(self, val_loader):
        self.model.eval()
        total_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                inputs, targets = batch
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                total_loss += loss.item()
                await asyncio.sleep(0)  # Allow other async operations to run
        return total_loss / len(val_loader)

    # Keep the original synchronous methods for backwards compatibility
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