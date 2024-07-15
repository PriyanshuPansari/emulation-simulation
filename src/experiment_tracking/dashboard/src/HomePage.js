import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const HomePage = () => {
  const [metrics, setMetrics] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [lastEpochSummary, setLastEpochSummary] = useState(null);

  useEffect(() => {
    let ws;

    const connectWebSocket = () => {
      ws = new WebSocket('ws://localhost:5000/ws');

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'metric') {
          setMetrics(prevMetrics => ({
            ...prevMetrics,
            [data.name]: [...(prevMetrics[data.name] || []), { x: data.step, y: data.value }]
          }));
        } else if (data.type === 'epoch_summary') {
          console.log('Epoch summary:', data);
          setLastEpochSummary(data);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleReconnect = () => {
    window.location.reload();
  };


  const getMetricColor = (metricName, alpha = 1) => {
    const colors = [
      `rgba(255, 99, 132, ${alpha})`,
      `rgba(53, 162, 235, ${alpha})`,
      `rgba(75, 192, 192, ${alpha})`,
      `rgba(255, 206, 86, ${alpha})`,
      `rgba(153, 102, 255, ${alpha})`,
      `rgba(255, 159, 64, ${alpha})`
    ];
    const index = Object.keys(metrics).indexOf(metricName) % colors.length;
    return colors[index];
  };

 
  const getLatestMetricValue = (metricName) => {
    const metricArray = metrics[metricName];
    if (metricArray && metricArray.length > 0) {
      return metricArray[metricArray.length - 1].y.toFixed(4);
    }
    return 'N/A';
  };

  const createChartData = (metricName) => ({
    datasets: [
      {
        label: metricName,
        data: metrics[metricName],
        borderColor: getMetricColor(metricName),
        backgroundColor: getMetricColor(metricName, 0.5),
        fill: false,
      }
    ],
  });

  const options = (title) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: title, font: { size: 14 } },
    },
    scales: {
      x: { type: 'linear', position: 'bottom', title: { display: true, text: 'Step' } },
      y: { type: 'linear', position: 'left', title: { display: true, text: 'Value' } },
    },
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.keys(metrics).map((metricName) => (
          <div key={metricName} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">{metricName}</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">
                {getLatestMetricValue(metricName)}
              </dd>
            </div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.keys(metrics).map((metricName) => (
          <div key={metricName} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">{metricName}</h3>
              <div className="mt-5 h-48">
                <Line data={createChartData(metricName)} options={options(metricName)} />
              </div>
            </div>
          </div>
        ))}
      </div>
      {lastEpochSummary && (
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Last Epoch Summary</h3>
            <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(lastEpochSummary).map(([key, value]) => (
                <div key={key} className="text-sm">
                  <dt className="font-medium text-gray-500">{key}</dt>
                  <dd className="mt-1 text-gray-900">{typeof value === 'number' ? value.toFixed(4) : value}</dd>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;