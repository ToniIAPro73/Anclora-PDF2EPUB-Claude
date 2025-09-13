import React, { useState } from 'react';

interface ConversionPanelProps {
  file: File | null;
}

const ConversionPanel: React.FC<ConversionPanelProps> = ({ file }) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConverting, setIsConverting] = useState<boolean>(false);

  const startConversion = async () => {
    if (!file) return;
    setError(null);
    setTaskId(null);
    setStatus(null);
    setIsConverting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });
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
        const res = await fetch(`/api/status/${id}`);
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
      <button onClick={startConversion} disabled={!file || isConverting}>
        {isConverting ? 'Convirtiendo...' : 'Enviar a convertir'}
      </button>
      {taskId && <p>Task ID: {taskId}</p>}
      {status && <p>Estado: {status}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default ConversionPanel;
