import React, { useEffect, useState } from 'react';

interface HistoryItem {
  task_id: string;
  filename?: string;
  status?: string;
  timestamp?: string;
}

const ConversionHistory: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('/api/history');
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || 'Error al obtener historial');
        }
        setHistory(data);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="conversion-history">
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Task ID</th>
            <th>Archivo</th>
            <th>Estado</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          {history.map(item => (
            <tr key={item.task_id}>
              <td>{item.task_id}</td>
              <td>{item.filename || '-'}</td>
              <td>{item.status || '-'}</td>
              <td>{item.timestamp || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ConversionHistory;
