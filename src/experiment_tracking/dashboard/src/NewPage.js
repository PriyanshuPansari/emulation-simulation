// NewPage.js
import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

function NewPage() {
  const [romFile, setRomFile] = useState('models/simple_cnn_20240715-003007.pth');
  const [modelFile, setModelFile] = useState('Airplane.ch8');
  const [configPath, setConfigPath] = useState('config.json');
  const [syncInterval, setSyncInterval] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState('');
  const chip8CanvasRef = useRef(null);
  const aiCanvasRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io('http://localhost:5000');

    socketRef.current.on('frames', (frames) => {
      updateCanvas(chip8CanvasRef.current, frames['CHIP-8']);
      updateCanvas(aiCanvasRef.current, frames['AI Simulation']);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const updateCanvas = (canvas, frameData) => {
    const ctx = canvas.getContext('2d');
    const width = 64;
    const height = 32;
    const scale = 10; // Increase this value for a larger display
  
    canvas.width = width * scale;
    canvas.height = height * scale;
  
    ctx.imageSmoothingEnabled = false;
  
    // Create an ImageData object
    const imageData = ctx.createImageData(width, height);
  
    // Set the pixel values
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const value = frameData[y][x] ? 255 : 0; // Use 255 for on pixels, 0 for off pixels
        const index = (y * width + x) * 4;
        imageData.data[index] = value;     // R
        imageData.data[index + 1] = value; // G
        imageData.data[index + 2] = value; // B
        imageData.data[index + 3] = 255;   // A
      }
    }
  
    // Create a temporary canvas to hold the original size image
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const tempCtx = tempCanvas.getContext('2d');
  
    // Put the ImageData on the temporary canvas
    tempCtx.putImageData(imageData, 0, 0);
  
    // Clear the main canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  
    // Draw the scaled image
    ctx.drawImage(tempCanvas, 0, 0, width, height, 0, 0, canvas.width, canvas.height);
  };

  const handleStart = async () => {
    if (romFile && modelFile) {
      setIsRunning(true);
      setMessage('Starting emulation...');

      const formData = new FormData();
      formData.append('rom', romFile);
      formData.append('model', modelFile);
      formData.append('config_path', configPath);
      formData.append('sync_interval', syncInterval.toString());

      try {
        const response = await fetch('http://localhost:5000/upload', {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();

        if (response.ok) {
          setMessage(data.message);
        } else {
          setMessage(`Error: ${data.error}`);
          setIsRunning(false);
        }
      } catch (error) {
        setMessage(`Error: ${error.message}`);
        setIsRunning(false);
      }
    } else {
      setMessage('Please select both ROM and model files.');
    }
  };

  const handleStop = () => {
    setIsRunning(false);
    setMessage('Emulation stopped.');
    // You may want to send a stop signal to the backend here
  };

  
  return (
    <div className="emulator-container">
      <h1 className="title">CHIP-8 vs AI Simulation</h1>
      <div className="control-panel">
        <div className="file-inputs">
          <div className="file-input">
            <label htmlFor="rom-file">ROM File:</label>
            <input
              id="rom-file"
              type="file"
              onChange={(e) => setRomFile(e.target.files[0])}
              accept=".ch8"
            />
            <span className="file-name">{romFile ? romFile.name : 'No file selected'}</span>
          </div>
          <div className="file-input">
            <label htmlFor="model-file">Model File:</label>
            <input
              id="model-file"
              type="file"
              onChange={(e) => setModelFile(e.target.files[0])}
              accept=".pth,.pt"
            />
            <span className="file-name">{modelFile ? modelFile.name : 'No file selected'}</span>
          </div>
        </div>
        <div className="config-inputs">
          <div className="input-group">
            <label htmlFor="config-path">Config Path:</label>
            <input
              id="config-path"
              type="text"
              value={configPath}
              onChange={(e) => setConfigPath(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label htmlFor="sync-interval">Sync Interval:</label>
            <input
              id="sync-interval"
              type="number"
              value={syncInterval}
              onChange={(e) => setSyncInterval(parseInt(e.target.value))}
            />
          </div>
        </div>
        <div className="button-group">
          <button
            className={`start-button ${isRunning ? 'running' : ''}`}
            onClick={handleStart}
            disabled={isRunning || !romFile || !modelFile}
          >
            {isRunning ? 'Running...' : 'Start Emulation'}
          </button>
          <button
            className="stop-button"
            onClick={handleStop}
            disabled={!isRunning}
          >
            Stop Emulation
          </button>
        </div>
      </div>
      {message && <div className="message">{message}</div>}
      <div className="emulator-displays">
        <div className="display-container">
          <h3>CHIP-8</h3>
          <canvas ref={chip8CanvasRef} />
        </div>
        <div className="display-container">
          <h3>AI Simulation</h3>
          <canvas ref={aiCanvasRef} />
        </div>
      </div>
    </div>
  );
}

export default NewPage;