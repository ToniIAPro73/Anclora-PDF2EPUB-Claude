import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploaderProps {
  onFileSelected?: (file: File) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelected }) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

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
      setError('Solo se permiten archivos PDF');
      setIsUploading(false);
      return;
    }

    // Verificar tamaño (máximo 50MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('El archivo es demasiado grande (máximo 50MB)');
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
  }, [onFileSelected]);

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
            ? 'border-blue-400 bg-blue-50 scale-105'
            : file
              ? 'border-green-400 bg-green-50'
              : error
                ? 'border-red-400 bg-red-50'
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
          ${isUploading ? 'pointer-events-none' : ''}
        `}
        style={{
          borderColor: isDragActive ? 'var(--accent-primary)' :
                      file ? '#10b981' :
                      error ? '#ef4444' : 'var(--border-color)',
          backgroundColor: isDragActive ? 'rgba(46, 175, 196, 0.1)' :
                          file ? 'rgba(16, 185, 129, 0.1)' :
                          error ? 'rgba(239, 68, 68, 0.1)' : 'transparent'
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
              Procesando archivo...
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
              {isDragActive ? '¡Suelta tu PDF aquí!' : 'Sube tu archivo PDF'}
            </h3>
            <p className="mb-4 font-medium" style={{ color: 'var(--text-uploader)', opacity: '0.9' }}>
              Arrastra y suelta tu archivo o haz clic para seleccionarlo
            </p>
            <div className="flex items-center gap-4 text-sm font-medium" style={{ color: 'var(--text-uploader)', opacity: '0.8' }}>
              <span>📋 Solo PDF</span>
              <span>📏 Máx. 50MB</span>
              <span>⚡ Conversión rápida</span>
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
                <p className="text-sm text-gray-600">
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
              Error al subir archivo
            </h3>
            <p className="text-red-500 mb-4">
              {error}
            </p>
            <button
              onClick={resetUpload}
              className="btn btn-secondary"
            >
              Intentar de nuevo
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
          >
            🔄 Cambiar archivo
          </button>
          <button
            className="btn btn-primary"
            onClick={() => {
              // Aquí se podría agregar lógica para iniciar la conversión directamente
              console.log('Iniciar conversión de:', file.name);
            }}
          >
            ⚡ Convertir ahora
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
