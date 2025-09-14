import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../AuthContext';
import { useTranslation } from 'react-i18next';

interface HistoryItem {
  task_id: string;
  input_filename?: string;
  status?: string;
  created_at: string;
}

const ConversionHistory: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { t } = useTranslation();

  useEffect(() => {
    const fetchHistory = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const { data, error: supabaseError } = await supabase
          .from('conversions')
          .select('task_id, input_filename, status, created_at')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false });

        if (supabaseError) {
          throw new Error(supabaseError.message);
        }

        setHistory(data || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [user]);

  if (loading) {
    return <div className="text-center py-8">{t('common.loading')}</div>;
  }

  return (
    <div className="conversion-history">
      {error && <p className="error text-red-500 mb-4">{error}</p>}
      {!error && history.length === 0 && (
        <p className="text-gray-500 text-center py-8">No hay conversiones realizadas aún.</p>
      )}
      {history.length > 0 && (
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border border-gray-300 px-4 py-2">Task ID</th>
              <th className="border border-gray-300 px-4 py-2">Archivo</th>
              <th className="border border-gray-300 px-4 py-2">Estado</th>
              <th className="border border-gray-300 px-4 py-2">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {history.map(item => (
              <tr key={item.task_id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-4 py-2">{item.task_id}</td>
                <td className="border border-gray-300 px-4 py-2">{item.input_filename || '-'}</td>
                <td className="border border-gray-300 px-4 py-2">{item.status || '-'}</td>
                <td className="border border-gray-300 px-4 py-2">
                  {item.created_at ? new Date(item.created_at).toLocaleDateString() : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ConversionHistory;
