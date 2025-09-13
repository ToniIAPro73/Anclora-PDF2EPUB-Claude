import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploaderProps {
  onFileSelected?: (file: File) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelected }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null);
    
    // Verificar si hay algún archivo
    if (acceptedFiles.length === 0) {
      return;
    }
    
    const selectedFile = acceptedFiles[0];
    
    // Verificar que sea un PDF
    if (selectedFile.type !== 'application/pdf') {
      setError('Solo se permiten archivos PDF');
      return;
    }
    
    // Verificar tamaño (máximo 50MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('El archivo es demasiado grande (máximo 50MB)');
      return;
    }
    
    setFile(selectedFile);
    
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
  
  const startConversion = () => {
    if (!file) return;
    
    setIsUploading(true);
    
    // Simulación de carga para demo
    setTimeout(() => {
      setIsUploading(false);
      console.log('Conversión iniciada para:', file.name);
      
      // Aquí iría la lógica real de envío al backend
    }, 1500);
  };
  
  const resetUpload = () => {
    setFile(null);
    setError(null);
    setIsUploading(false);
  };
  
  return (
    <div className="file-uploader">
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''} ${file ? 'has-file' : ''} ${error ? 'has-error' : ''}`}
      >
        <input {...getInputProps()} />
        
        {!file && !error && (
          <div className="upload-prompt">
            <div className="upload-icon">📄</div>
            <p>Arrastra tu PDF aquí o haz clic para seleccionarlo</p>
          </div>
        )}
        
        {file && !error && (
          <div className="file-info">
            <span className="file-name">{file.name}</span>
            <span className="file-size">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
      </div>
      
      <div className="action-buttons">
        <button 
          className={`convert-button ${!file || isUploading ? 'disabled' : 'active'}`}
          disabled={!file || isUploading}
          onClick={startConversion}
        >
          {isUploading ? 'Procesando...' : 'Iniciar Conversión'}
        </button>
        
        <button 
          className={`reset-button ${!file ? 'disabled' : 'active'}`}
          disabled={!file}
          onClick={resetUpload}
        >
          Reiniciar
        </button>
      </div>
    </div>
  );
};

export default FileUploader;