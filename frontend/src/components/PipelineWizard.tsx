import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

interface Pipeline {
  id: string;
  quality: string;
  estimated_time: number;
  cost: number;
}

interface PipelineWizardProps {
  file: File | null;
}

type Step = 'analysis' | 'selection' | 'confirmation';

const PipelineWizard: React.FC<PipelineWizardProps> = ({ file }) => {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>('analysis');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [selected, setSelected] = useState<Pipeline | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConverting, setIsConverting] = useState<boolean>(false);
  const [status, setStatus] = useState<string | null>(null);

  const analyzeFile = async () => {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
    setPipelines([]);
    setSelected(null);
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
      
      if (error.message === 'UNAUTHORIZED') {
          navigate('/login');
          return;
        }
      setPipelines(data.pipelines || []);
      setStep('selection');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    if (file) {
      setStep('analysis');
      analyzeFile();
    } else {
      setPipelines([]);
      setSelected(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [file]);

  const startConversion = async () => {
    if (!file || !selected) return;
    setError(null);
    setStatus(null);
    setIsConverting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('pipeline_id', selected.id);
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
      
      if (error.message === 'UNAUTHORIZED') {
          navigate('/login');
          return;
        }
      pollStatus(data.task_id);
    } catch (err: any) {
      setError(err.message);
      setIsConverting(false);
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${id}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (res.status === 401) {
          clearInterval(interval);
          logout();
          navigate('/login');
          setIsConverting(false);
          return;
        }
        
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
    <div className="pipeline-wizard">
      {error && <p className="error">{error}</p>}
      {step === 'analysis' && (
        <div>
          {isAnalyzing ? <p>Analizando...</p> : <p>Preparando análisis...</p>}
        </div>
      )}
      {step === 'selection' && (
        <div className="pipeline-selection">
          <h3>Opciones de conversión</h3>
          <ul>
            {pipelines.map((p) => (
              <li key={p.id}>
                <label>
                  <input
                    type="radio"
                    name="pipeline"
                    value={p.id}
                    checked={selected?.id === p.id}
                    onChange={() => setSelected(p)}
                  />
                  Pipeline {p.quality} - {p.estimated_time}s - {p.cost}$
                </label>
              </li>
            ))}
          </ul>
          <button disabled={!selected} onClick={() => setStep('confirmation')}>
            Confirmar
          </button>
        </div>
      )}
      {step === 'confirmation' && selected && (
        <div className="pipeline-confirmation">
          <h3>Confirmar conversión</h3>
          <p>Calidad: {selected.quality}</p>
          <p>Tiempo estimado: {selected.estimated_time}s</p>
          <p>Costo: {selected.cost}$</p>
          <button disabled={isConverting} onClick={startConversion}>
            {isConverting ? 'Convirtiendo...' : 'Convertir'}
          </button>
          {status && <p>Estado: {status}</p>}
        </div>
      )}
    </div>
  );
};

export default PipelineWizard;

