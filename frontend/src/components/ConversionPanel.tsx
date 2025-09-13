import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

interface ConversionPanelProps {
  file: File | null;
}

const ConversionPanel: React.FC<ConversionPanelProps> = ({ file }) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConverting, setIsConverting] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [pipelines, setPipelines] = useState<Array<{ id: string; quality: string; estimated_time: number }>>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<string>('');
  const { token, logout } = useAuth();
  const navigate = useNavigate();

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
        throw new Error(data.error || 'Error en la conversión');
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
        if (data.status === 'SUCCESS') {
          clearInterval(interval);
          setIsConverting(false);
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
          setError(data.error || 'Error en la conversión');
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
      {isAnalyzing && <p>Analizando...</p>}
      {pipelines.length > 0 && (
        <div className="pipeline-list">
          <h3>Opciones de conversión</h3>
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
                  {p.quality} - {p.estimated_time}s
                </label>
              </li>
            ))}
          </ul>
        </div>
      )}
      <button onClick={startConversion} disabled={!file || !selectedPipeline || isConverting}>
        {isConverting ? 'Convirtiendo...' : 'Enviar a convertir'}
      </button>
      {taskId && <p>Task ID: {taskId}</p>}
      {status && <p>Estado: {status}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default ConversionPanel;
