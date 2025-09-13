import React from 'react';

interface Metrics {
  pages: number;
  time: number;
}

interface MetricsDisplayProps {
  metrics: Metrics;
}

const MetricsDisplay: React.FC<MetricsDisplayProps> = ({ metrics }) => {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="text-lg font-semibold mb-2">Métricas</h2>
      <p>Páginas procesadas: {metrics.pages}</p>
      <p>Tiempo: {metrics.time.toFixed(2)}s</p>
    </div>
  );
};

export default MetricsDisplay;
