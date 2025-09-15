import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import PreviewModal from './PreviewModal';
import Toast from './Toast';
import { useTranslation } from 'react-i18next';

interface ConversionPanelProps {
  file: File | null;
}

const ConversionPanel: React.FC<ConversionPanelProps> = ({ file }) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isConverting, setIsConverting] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [pipelines, setPipelines] = useState<Array<{ id: string; quality: string; estimated_time: number }>>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const analyzeFile = async () => {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
    setPipelines([]);
    setSelectedPipeline('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (res.status === 401) {
        logout();
        navigate('/login');
        setIsAnalyzing(false);
        return;
      }
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Error al analizar');
      }
      setPipelines(data.pipelines || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    if (file) {
      analyzeFile();
    } else {
      setPipelines([]);
      setSelectedPipeline('');
    }
  }, [file]);

  const startConversion = async () => {
    if (!file || !selectedPipeline) return;
    setError(null);
    setTaskId(null);
    setStatus(null);
    setProgress(0);
    setStatusMessage('');
    setIsConverting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('pipeline_id', selectedPipeline);
      const res = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (res.status === 401) {
        logout();
        navigate('/login');
        setIsConverting(false);
        return;
      }
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || t('conversionPanel.conversionError'));
      }
      setTaskId(data.task_id);
      pollStatus(data.task_id);
    } catch (err: any) {
      setError(err.message);
      setIsConverting(false);
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${id}` , {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (res.status === 401) {
          clearInterval(interval);
          logout();
          navigate('/login');
          setIsConverting(false);
          return;
        }
        const data = await res.json();
        setStatus(data.status);
        if (data.status === 'PROGRESS') {
          if (typeof data.progress === 'number') {
            setProgress(data.progress);
          }
          if (data.message) {
            setStatusMessage(data.message);
          }
        } else if (data.status === 'SUCCESS') {
          clearInterval(interval);
          setIsConverting(false);
          setProgress(100);
          setStatusMessage(t('conversionPanel.completed'));
          if (data.result && data.result.output_path) {
            const downloadRes = await fetch(data.result.output_path);
            const blob = await downloadRes.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.result.output_path.split('/').pop() || 'resultado.epub';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
          }
        } else if (data.status === 'FAILURE') {
          clearInterval(interval);
          setIsConverting(false);
          setError(data.error || t('conversionPanel.conversionError'));
          setStatusMessage('');
        }
      } catch (err: any) {
        clearInterval(interval);
        setIsConverting(false);
        setError(err.message);
      }
    }, 2000);
  };

  return (
    <div className="conversion-panel">
      {isAnalyzing && <p>{t('conversionPanel.analyzing')}</p>}
      {pipelines.length > 0 && (
        <div className="pipeline-list">
          <h3>{t('conversionPanel.options')}</h3>
          <ul>
            {pipelines.map((p) => (
              <li key={p.id}>
                <label>
                  <input
                    type="radio"
                    name="pipeline"
                    value={p.id}
                    checked={selectedPipeline === p.id}
                    onChange={() => setSelectedPipeline(p.id)}
                  />
                  {t(`engines.${p.quality}`)} - {p.estimated_time}s
                </label>
              </li>
            ))}
          </ul>
        </div>
      )}
      <button onClick={startConversion} disabled={!file || !selectedPipeline || isConverting}>
        {isConverting ? t('conversionPanel.converting') : t('conversionPanel.submit')}
      </button>
      {isConverting && (
        <div className="w-full mt-4">
          <div className="w-full bg-gray-200 rounded h-4">
            <div
              className="bg-blue-500 h-4 rounded"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="mt-2 text-sm">{statusMessage || t('conversionPanel.progress', { progress })}</p>
        </div>
      )}
      {taskId && <p>{t('conversionPanel.taskId', { id: taskId })}</p>}
      {status && !isConverting && <p>{t('conversionPanel.status', { status })}</p>}
      {error && (
        <Toast
          message={error}
          variant="error"
          onClose={() => setError(null)}
        />
      )}
    </div>
  );
};

export default ConversionPanel;
