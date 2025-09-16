import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import Container from './Container';
import Toast from './Toast';

interface FileUploaderProps {
  onFileSelected?: (file: File) => void;
  onConversionStarted?: (taskId: string) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelected, onConversionStarted: _onConversionStarted }) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [_forceUpdate, setForceUpdate] = useState(0);
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, token, session } = useAuth();
  const [toast, setToast] = useState<{ title: string; message: string; variant: 'success' | 'error' } | null>(null);

  const PENDING_FILE_KEY = 'pendingFile';

  const clearPendingFile = () => {
    localStorage.removeItem(PENDING_FILE_KEY);
  };

  const savePendingFile = (file: File) => {
    return new Promise<void>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          localStorage.setItem(
            PENDING_FILE_KEY,
            JSON.stringify({
              name: file.name,
              type: file.type,
              dataUrl: reader.result,
              route: window.location.pathname,
            })
          );
        } catch (e) {
          console.error('Error saving file to localStorage', e);
        }
        resolve();
      };
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });
  };

  const getPendingFile = async (): Promise<{ file: File; route: string } | null> => {
    const raw = localStorage.getItem(PENDING_FILE_KEY);
    if (!raw) return null;
    try {
      const { name, type, dataUrl, route } = JSON.parse(raw);
      const res = await fetch(dataUrl);
      const blob = await res.blob();
      return { file: new File([blob], name, { type }), route };
    } catch (e) {
      console.error('Error reconstructing file from localStorage', e);
      clearPendingFile();
      return null;
    }
  };

  // Debug logging
  console.log('FileUploader - Current language:', i18n.language);
  console.log('FileUploader - uploadTitle translation:', t('fileUploader.uploadTitle'));

  // Función para iniciar la conversión real cuando el usuario está autenticado
  const startActualConversion = async (engineName: string) => {
    if (!file || !token) return;

    try {
      // Mostrar mensaje de inicio de conversión
      const startMessage = `🚀 ${t('fileUploader.startingConversion')}\n\n` +
        `🎯 ${t('fileUploader.usingEngine')}: ${engineName}\n\n` +
        `⏳ ${t('fileUploader.pleaseWait')}`;

      setToast({ title: 'Info', message: startMessage, variant: 'success' });

      // Preparar datos para la conversión
      const formData = new FormData();
      formData.append('file', file);
      formData.append('pipeline_id', engineName);

      // Debug: Log token information
      console.log('🔍 Debug: Token available:', !!token);
      console.log('🔍 Debug: Token preview:', token ? token.substring(0, 50) + '...' : 'NO TOKEN');
      console.log('🔍 Debug: User info:', user ? { id: user.id, email: user.email } : 'NO USER');
      
      // Hacer la llamada a la API de conversión (via proxy)
      const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        // Token expirado, redirigir al login
        navigate('/login');
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || t('fileUploader.conversionError'));
      }

      // Conversión iniciada exitosamente
      const successMessage = `✅ ${t('fileUploader.conversionStarted')}\n\n` +
        `🆔 Task ID: ${data.task_id}\n\n` +
        `📊 ${t('fileUploader.checkHistory')}`;

      setToast({ title: 'Success', message: successMessage, variant: 'success' });

      // Opcional: llamar al callback si existe
      if (_onConversionStarted) {
        _onConversionStarted(data.task_id);
      }

      // Redirigir al historial para ver el progreso
      setTimeout(() => {
        navigate('/');
      }, 2000);

    } catch (error: any) {
      console.error('Error en conversión:', error);
      setError(error.message);

      const errorMessage = `❌ ${t('fileUploader.conversionError')}\n\n${error.message}`;
      setToast({ title: 'Error', message: errorMessage, variant: 'error' });
    }
    finally {
      clearPendingFile();
    }
  };

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

  useEffect(() => {
    const processPendingFile = async () => {
      if (!user || !session) return;
      const pending = await getPendingFile();
      if (pending) {
        if (pending.route && pending.route !== window.location.pathname) {
          navigate(pending.route);
        }
        setFile(pending.file);
        if (onFileSelected) {
          onFileSelected(pending.file);
        }
        await startQuickConversion(pending.file);
      }
    };
    processPendingFile();
  }, [user, session]);

  // Función para análisis rápido y mostrar recomendación
  const startQuickConversion = async (inputFile?: File) => {
    const fileToUse = inputFile || file;
    if (!fileToUse || isConverting) return;

    setFile(fileToUse);
    setError(null);
    setIsConverting(true);

    try {
      // 1. Analizar el archivo para obtener recomendaciones
      const formData = new FormData();
      formData.append('file', fileToUse);

      console.log('Debug - user:', !!user, 'token:', !!token, 'session:', !!session);
      console.log('Debug - token preview:', token ? token.substring(0, 20) + '...' : 'null');

      const analyzeRes = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });

      const analyzeData = await analyzeRes.json();
      if (!analyzeRes.ok) {
        throw new Error(analyzeData.error || t('fileUploader.analyzeError'));
      }

      // 2. Mostrar análisis y recomendación
      const engineName = analyzeData.recommended || analyzeData.pipeline_id || 'balanced';
      const engineNames: Record<string, string> = {
        'rapid': t('engines.rapid'),
        'balanced': t('engines.balanced'),
        'quality': t('engines.quality')
      };

      const recommendedName = engineNames[engineName] || engineName;

      // 3. Verificar si el usuario está autenticado
      if (!user || !token) {
        // Usuario no autenticado - mostrar mensaje y redirigir al login
        const analysisMessage = `📊 ${t('fileUploader.analysisComplete')}\n\n` +
          `🎯 ${t('fileUploader.recommendedEngine')}: ${recommendedName}\n\n` +
          `💡 ${t('fileUploader.loginToConvert')}`;

        setToast({ title: 'Info', message: analysisMessage, variant: 'success' });

        await savePendingFile(fileToUse);

        // Redirigir al login después de mostrar la información
        setTimeout(() => {
          navigate('/login');
        }, 1000);
        return;
      } else {
        // Usuario autenticado - proceder con la conversión
        await startActualConversion(engineName);
      }

    } catch (err: any) {
      setError(err.message);
      console.error('Error en análisis rápido:', err);
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

    // Verificar tamaño (máximo 25MB - sincronizado con backend)
    const maxSizeMB = 25;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (selectedFile.size > maxSizeBytes) {
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
    clearPendingFile();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <>
    <Container>
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
              <span>📏 Max 25MB</span>
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
            <div className="w-16 h-16 rounded-2xl mb-4 flex items-center justify-center p-3 relative"
                 style={{ background: 'var(--bg-secondary)' }}>
              <img
                src="/images/iconos/Icono PDF.png"
                alt="Icono PDF"
                className="w-full h-full object-contain opacity-60"
              />
              <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center"
                   style={{ background: 'var(--accent-primary)' }}>
                <span className="text-white text-xs font-bold">!</span>
              </div>
            </div>
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
              {t('fileUploader.uploadError')}
            </h3>
            <div className="mb-4 p-3 rounded-lg" style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)'
            }}>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {error}
              </p>
            </div>
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
            onClick={() => startQuickConversion()}
            disabled={isConverting}
          >
            {isConverting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {t('fileUploader.processing')}
              </>
            ) : (
              <>🔍 {t('fileUploader.convertNow')}</>
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
    </Container>
    {toast && (
      <Toast
        title={toast.title}
        message={toast.message}
        variant={toast.variant}
        onClose={() => setToast(null)}
      />
    )}
    </>
  );
};

export default FileUploader;


