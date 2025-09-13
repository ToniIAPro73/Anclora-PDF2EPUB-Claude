import React, { useState } from 'react';
import FileUploader from './FileUploader';
import MetricsDisplay from './MetricsDisplay';

interface Metrics {
  pages: number;
  time: number;
}

interface HistoryItem {
  id: number;
  fileName: string;
  date: string;
}

const ConversionPanel: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  const handleFileSelected = (file: File) => {
    const newMetrics: Metrics = {
      pages: Math.floor(Math.random() * 10) + 1,
      time: parseFloat((Math.random() * 5 + 1).toFixed(2)),
    };
    setMetrics(newMetrics);

    const entry: HistoryItem = {
      id: Date.now(),
      fileName: file.name,
      date: new Date().toLocaleString(),
    };
    const history: HistoryItem[] = JSON.parse(localStorage.getItem('history') || '[]');
    history.unshift(entry);
    localStorage.setItem('history', JSON.stringify(history));
  };

  return (
    <div className="space-y-6">
      <FileUploader onFileSelected={handleFileSelected} />
      {metrics && <MetricsDisplay metrics={metrics} />}
    </div>
  );
};

export default ConversionPanel;
