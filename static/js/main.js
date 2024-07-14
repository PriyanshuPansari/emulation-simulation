const socket = io();
let metricCharts = {};

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('update', (data) => {
    updateFrames(data);
    updateMetrics(data.metrics);
});

function updateFrames(data) {
    document.getElementById('chip8-frame').src = `data:image/png;base64,${data.chip8}`;
    
    const modelContainer = document.getElementById('model-frames');
    modelContainer.innerHTML = '';
    
    for (const [name, frame] of Object.entries(data.models)) {
        const frameElement = document.createElement('div');
        frameElement.className = 'frame';
        frameElement.innerHTML = `
            <h3>${name}</h3>
            <img src="data:image/png;base64,${frame}" alt="${name} frame">
        `;
        modelContainer.appendChild(frameElement);
    }
}

function updateMetrics(metrics) {
    const metricsContainer = document.getElementById('metrics-container');
    
    for (const [modelName, modelMetrics] of Object.entries(metrics)) {
        for (const [metricName, metricValue] of Object.entries(modelMetrics)) {
            const chartId = `${modelName}-${metricName}`.replace(/\s+/g, '-');
            let chart = metricCharts[chartId];
            
            if (!chart) {
                // Create new chart
                const chartElement = document.createElement('div');
                chartElement.className = 'metric-chart';
                chartElement.innerHTML = `<canvas id="${chartId}"></canvas>`;
                metricsContainer.appendChild(chartElement);
                
                const ctx = document.getElementById(chartId).getContext('2d');
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: `${modelName} - ${metricName}`,
                            data: [],
                            borderColor: getRandomColor(),
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                            display: true,
                            text: `${modelName} - ${metricName}`
                        },
                        scales: {
                            x: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Frame'
                                }
                            },
                            y: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Value'
                                }
                            }
                        }
                    }
                });
                metricCharts[chartId] = chart;
            }
            
            // Update chart data
            chart.data.labels.push(chart.data.labels.length);
            chart.data.datasets[0].data.push(metricValue);
            
            // Limit the number of data points to prevent overcrowding
            const maxDataPoints = 100;
            if (chart.data.labels.length > maxDataPoints) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update();
        }
    }
}

function getRandomColor() {
    return '#' + Math.floor(Math.random()*16777215).toString(16);
}

document.getElementById('start-button').addEventListener('click', startEmulation);
document.getElementById('stop-button').addEventListener('click', stopEmulation);

function startEmulation() {
    const romPath = document.getElementById('rom-path').value;
    const modelPaths = {};
    document.getElementById('model-paths').value.split(',').forEach((path, index) => {
        modelPaths[`Model ${index + 1}`] = path.trim();
    });
    const configPath = document.getElementById('config-path').value;

    fetch('/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            romPath: romPath,
            modelPaths: modelPaths,
            configPath: configPath
        })
    })
    .then(response => response.json())
    .then(data => console.log(data.message))
    .catch(error => console.error('Error:', error));
}

function stopEmulation() {
    fetch('/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => console.log(data.message))
    .catch(error => console.error('Error:', error));
}