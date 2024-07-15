import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const PastRuns = () => {
  const [experiments, setExperiments] = useState([]);
  const [selectedExperiment, setSelectedExperiment] = useState('');
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    fetchExperiments();
  }, []);

  useEffect(() => {
    if (selectedExperiment) {
      fetchMetrics(selectedExperiment);
    }
  }, [selectedExperiment]);

  const fetchExperiments = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/experiments');
      if (!response.ok) {
        throw new Error('HTTP error ' + response.status);
      }
      const data = await response.json();
      // console.log('Experiments:', data);
      setExperiments(data);
      if (data.length > 0) {
        setSelectedExperiment(data[0]);
      }
    } catch (error) {
      console.error('Error fetching experiments:', error);
    }
  };

  const fetchMetrics = async (experimentId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/experiments/${experimentId}/metrics`);
      console.log(response);
      if (!response.ok) {
        throw new Error('HTTP error ' + response.status);
      }
      const data = await response.json();
      console.log('Metrics:', data);
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const createChartData = (metricName) => ({
    labels: metrics[metricName].map(([step, _]) => step),
    datasets: [
      {
        label: metricName,
        data: metrics[metricName].map(([_, value]) => value),
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
    const metricData = metrics[metricName];
    if (metricData && metricData.length > 0) {
      return metricData[metricData.length - 1][1].toFixed(4);
    }
    return 'N/A';
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-4">
        <label htmlFor="experiment-select" className="block text-sm font-medium text-gray-700">
          Select Experiment
        </label>
        <select
          id="experiment-select"
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          value={selectedExperiment}
          onChange={(e) => setSelectedExperiment(e.target.value)}
        >
          {experiments.map((exp) => (
            <option key={exp} value={exp}>{exp}</option>
          ))}
        </select>
      </div>

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
    </div>
  );
};

export default PastRuns;
