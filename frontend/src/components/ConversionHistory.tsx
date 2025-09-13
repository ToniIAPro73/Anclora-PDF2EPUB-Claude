import React, { useEffect, useState } from 'react';

interface HistoryItem {
  id: number;
  fileName: string;
  date: string;
}

const ConversionHistory: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('history');
    if (stored) {
      setHistory(JSON.parse(stored));
    }
  }, []);

  if (history.length === 0) {
    return <p className="text-center">No hay conversiones registradas.</p>;
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Historial de Conversiones</h2>
      <ul className="space-y-2">
        {history.map((item) => (
          <li key={item.id} className="bg-white dark:bg-gray-800 p-4 rounded shadow">
            <p className="font-medium">{item.fileName}</p>
            <p className="text-sm text-gray-500">{item.date}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ConversionHistory;
