import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../AuthContext';
import { useNavigate } from 'react-router-dom';

interface FileUploaderProps {
  onFileSelected?: (file: File) => void;
  onConversionStarted?: (taskId: string) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelected, onConversionStarted }) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(0); // eslint-disable-line @typescript-eslint/no-unused-vars
  const { t, i18n } = useTranslation();
  const { session, logout } = useAuth();
  const navigate = useNavigate();

  // Debug logging
  console.log('FileUploader - Current language:', i18n.language);
  console.log('FileUploader - uploadTitle translation:', t('fileUploader.uploadTitle'));

  // Forzar re-render cuando cambie el idioma
  useEffect(() => {
    const handleLanguageChange = () => {
      console.log('FileUploader - Language changed, forcing update');
      setForceUpdate(prev => prev + 1);
    };

    i18n.on('languageChanged', handleLanguageChange);
    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n]);

  // Función para iniciar conversión automática con engine recomendado
  const startQuickConversion = async () => {
    if (!file || isConverting) return;

    setError(null);
    setIsConverting(true);

    try {
      // 1. Analizar el archivo para obtener el engine recomendado
      const formData = new FormData();
      formData.append('file', file);

      const analyzeRes = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
        headers: session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : undefined,
      });

      if (analyzeRes.status === 401) {
        logout();
        navigate('/login');
        setIsConverting(false);
        return;
      }

      const analyzeData = await analyzeRes.json();
      if (!analyzeRes.ok) {
        throw new Error(analyzeData.error || 'Error al analizar el archivo');
      }

      // 2. Usar el pipeline recomendado o el primero disponible
      const recommendedPipeline = analyzeData.pipelines?.[0]?.id || 'balanced';

      // 3. Iniciar la conversión
      const convertFormData = new FormData();
      convertFormData.append('file', file);
      convertFormData.append('pipeline_id', recommendedPipeline);

      const convertRes = await fetch('/api/convert', {
        method: 'POST',
        body: convertFormData,
        headers: session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : undefined,
      });

      if (convertRes.status === 401) {
        logout();
        navigate('/login');
        setIsConverting(false);
        return;
      }

      const convertData = await convertRes.json();
      if (!convertRes.ok) {
        throw new Error(convertData.error || 'Error en la conversión');
      }

      // 4. Notificar éxito y llamar callback
      console.log('Conversión iniciada con task_id:', convertData.task_id);

      // Mostrar mensaje de éxito más informativo
      const successMessage = `${t('fileUploader.success')}\n\nTask ID: ${convertData.task_id}\n\n${t('history.subtitle')}`;
      alert(successMessage);

      // Notificar al componente padre si hay callback
      if (onConversionStarted) {
        onConversionStarted(convertData.task_id);
      }

    } catch (err: any) {
      setError(err.message);
      console.error('Error en conversión rápida:', err);
    } finally {
      setIsConverting(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setError(null);
    setIsUploading(true);

    // Verificar si hay algún archivo
    if (acceptedFiles.length === 0) {
      setIsUploading(false);
      return;
    }

    const selectedFile = acceptedFiles[0];

    // Verificar que sea un PDF
    if (selectedFile.type !== 'application/pdf') {
      setError(t('fileUploader.supportedFormats'));
      setIsUploading(false);
      return;
    }

    // Verificar tamaño (máximo 50MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError(t('fileUploader.maxSize'));
      setIsUploading(false);
      return;
    }

    // Simular un pequeño delay para mostrar el loading
    await new Promise(resolve => setTimeout(resolve, 500));

    setFile(selectedFile);
    setIsUploading(false);

    if (onFileSelected) {
      onFileSelected(selectedFile);
    }
  }, [onFileSelected, t]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const resetUpload = () => {
    setFile(null);
    setError(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer
          ${isDragActive
            ? 'border-blue-400 scale-105'
            : file
              ? 'border-green-400'
              : error
                ? 'border-red-400'
                : 'border-gray-300 hover:border-gray-400'
          }
          ${isUploading ? 'pointer-events-none' : ''}
          ${!isDragActive && !file && !error ? 'bg-uploader-pattern' : ''}
        `}
        style={{
          borderColor: isDragActive ? 'var(--accent-primary)' :
                      file ? '#10b981' :
                      error ? '#ef4444' : 'var(--border-color)',
          backgroundColor: isDragActive ? 'rgba(46, 175, 196, 0.15)' :
                          file ? 'rgba(16, 185, 129, 0.1)' :
                          error ? 'rgba(239, 68, 68, 0.1)' : undefined
        }}
      >
        <input {...getInputProps()} />

        {/* Loading State */}
        {isUploading && (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <div className="w-16 h-16 rounded-full mb-4 flex items-center justify-center"
                 style={{ background: 'var(--gradient-action)' }}>
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-lg font-medium" style={{ color: 'var(--text-primary)' }}>
              {t('fileUploader.processing')}
            </p>
          </div>
        )}

        {/* Empty State */}
        {!file && !error && !isUploading && (
          <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
            <div className="w-20 h-20 rounded-2xl mb-6 flex items-center justify-center p-3"
                 style={{ background: isDragActive ? 'var(--gradient-action)' : 'var(--gradient-hero)' }}>
              <img
                src="/images/iconos/Icono PDF.png"
                alt="Icono PDF"
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-uploader)' }}>
              {isDragActive ? t('fileUploader.dropHere') : t('fileUploader.uploadTitle')}
            </h3>
            <p className="mb-4 font-medium" style={{ color: 'var(--text-uploader)', opacity: '0.9' }}>
              {t('fileUploader.uploadInstructions')}
            </p>
            <div className="flex items-center gap-4 text-sm font-medium" style={{ color: 'var(--text-uploader)', opacity: '0.8' }}>
              <span>📋 {t('fileUploader.onlyPDF')}</span>
              <span>📏 {t('fileUploader.maxSize')}</span>
              <span>⚡ {t('fileUploader.fastConversion')}</span>
            </div>
          </div>
        )}

        {/* Success State */}
        {file && !error && !isUploading && (
          <div className="flex items-center justify-between py-6 px-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center p-2"
                   style={{ background: 'var(--gradient-nexus)' }}>
                <img
                  src="/images/iconos/Icono PDF.png"
                  alt="Icono PDF"
                  className="w-full h-full object-contain"
                />
              </div>
              <div>
                <h4 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                  {file.name}
                </h4>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {formatFileSize(file.size)} • PDF
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full flex items-center justify-center bg-green-100 text-green-600">
                <span>✓</span>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !isUploading && (
          <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
            <div className="w-16 h-16 rounded-2xl mb-4 flex items-center justify-center bg-red-100 p-3 relative">
              <img
                src="/images/iconos/Icono PDF.png"
                alt="Icono PDF"
                className="w-full h-full object-contain opacity-60"
              />
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">!</span>
              </div>
            </div>
            <h3 className="text-lg font-semibold mb-2 text-red-600">
              {t('fileUploader.uploadError')}
            </h3>
            <p className="text-red-500 mb-4">
              {error}
            </p>
            <button
              onClick={resetUpload}
              className="btn btn-secondary"
            >
              {t('fileUploader.tryAgain')}
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {file && !error && !isUploading && (
        <div className="flex justify-center gap-3 mt-4">
          <button
            onClick={resetUpload}
            className="btn btn-secondary"
            disabled={isConverting}
          >
            🔄 {t('fileUploader.changeFile')}
          </button>
          <button
            className="btn btn-primary"
            onClick={startQuickConversion}
            disabled={isConverting}
          >
            {isConverting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {t('fileUploader.processing')}
              </>
            ) : (
              <>⚡ {t('fileUploader.convertNow')}</>
            )}
          </button>
        </div>
      )}

      {/* Info message about advanced options */}
      {file && !error && !isUploading && !isConverting && (
        <div className="text-center mt-3">
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            💡 {t('fileUploader.advancedOptionsBelow')}
          </p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;


