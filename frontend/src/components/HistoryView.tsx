import React, { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';

interface ConversionItem {
  id: number;
  task_id: string;
  status: string;
  output_path?: string;
  thumbnail_url?: string;
  created_at?: string;
}

const HistoryView: React.FC = () => {
  const [history, setHistory] = useState<ConversionItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('/api/history', {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
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
  }, [token]);

  return (
    <div className="history-view">
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Miniatura</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {history.map(item => (
            <tr key={item.task_id}>
              <td>
                {item.thumbnail_url && (
                  <img src={item.thumbnail_url} alt={item.task_id} width={60} />
                )}
              </td>
              <td>{item.status}</td>
              <td>{item.created_at ? new Date(item.created_at).toLocaleString() : '-'}</td>
              <td>
                {item.output_path && (
                  <>
                    <a href={item.output_path} download>
                      Descargar
                    </a>{' '}
                    <a href={item.output_path} target="_blank" rel="noopener noreferrer">
                      Ver
                    </a>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default HistoryView;
