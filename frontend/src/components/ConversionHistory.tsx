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
  const [forceUpdate, setForceUpdate] = useState(0); // eslint-disable-line @typescript-eslint/no-unused-vars
  const { user } = useAuth();
  const { t, i18n } = useTranslation();

  // Forzar re-render cuando cambie el idioma
  useEffect(() => {
    const handleLanguageChange = () => {
      console.log('ConversionHistory - Language changed, forcing update');
      setForceUpdate(prev => prev + 1);
    };

    i18n.on('languageChanged', handleLanguageChange);
    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n]);

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
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 mx-auto mb-4 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: 'var(--accent-primary)' }}></div>
        <p style={{ color: 'var(--text-secondary)' }}>{t('common.loading')}</p>
      </div>
    );
  }

  return (
    <div className="conversion-history">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-700 text-sm font-medium">{t('common.error')}: {error}</p>
        </div>
      )}
      {!error && history.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ background: 'var(--bg-secondary)' }}>
            <span className="text-2xl">📄</span>
          </div>
          <p className="text-lg mb-2 font-medium" style={{ color: 'var(--text-primary)' }}>
            {t('history.empty')}
          </p>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {t('history.emptyDescription')}
          </p>
        </div>
      )}
      {history.length > 0 && (
        <div className="overflow-x-auto rounded-lg shadow">
          <table className="w-full border-collapse" style={{ background: 'var(--bg-primary)' }}>
            <thead>
              <tr style={{ background: 'var(--bg-secondary)' }}>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  Task ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  {t('history.columns.file')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  {t('history.columns.status')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  {t('history.columns.date')}
                </th>
              </tr>
            </thead>
          <tbody>
            {history.map(item => {
              // Función para traducir el estado
              const getStatusTranslation = (status: string | undefined) => {
                if (!status) return '-';
                const statusKey = status.toLowerCase();
                const translationKey = `history.status.${statusKey}`;
                const translated = t(translationKey);
                // Si no hay traducción específica, devolver el estado original
                return translated === translationKey ? status : translated;
              };

              // Función para formatear la fecha
              const formatDate = (dateString: string) => {
                const date = new Date(dateString);
                return date.toLocaleDateString(i18n.language === 'es' ? 'es-ES' : 'en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                });
              };

              return (
                <tr key={item.task_id} className="hover:opacity-75 transition-opacity" style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono" style={{ color: 'var(--text-secondary)' }}>
                    {item.task_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                    {item.input_filename || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      item.status === 'completed' ? 'bg-green-100 text-green-800' :
                      item.status === 'failed' ? 'bg-red-100 text-red-800' :
                      item.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {getStatusTranslation(item.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {item.created_at ? formatDate(item.created_at) : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        </div>
      )}
    </div>
  );
};

export default ConversionHistory;
