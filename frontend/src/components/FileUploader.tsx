import React, { useCallback, useState, useEffect, useMemo } from "react";
import { useDropzone } from "react-dropzone";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { ApiError, NetworkError, ValidationError, FileProcessingError } from "../lib/errors";
import { apiPost, createFormData } from "../lib/apiClient";
import Container from "./Container";
import Toast from "./Toast";

// File storage key in localStorage
const PENDING_FILE_KEY = "pendingFile";

// Toast configuration interface
interface ToastConfig {
  title: string;
  message: string;
  variant: "success" | "error" | "warning" | "info";
}

// File analysis result interface
interface AnalysisResult {
  pipelines: Array<{
    id: string;
    quality: string;
    estimated_time: number;
  }>;
  recommended?: string;
  pipeline_id?: string;
}

// Conversion result interface
interface ConversionResult {
  task_id: string;
  status: string;
}

interface FileUploaderProps {
  onFileSelected?: (file: File) => void;
  onConversionStarted?: (taskId: string) => void;
}

/**
 * Enhanced FileUploader component with optimized file handling and error management
 */
const FileUploader: React.FC<FileUploaderProps> = ({ 
  onFileSelected, 
  onConversionStarted 
}) => {
  // State management
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<ApiError | Error | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [toast, setToast] = useState<ToastConfig | null>(null);
  
  // Hooks
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, token, session } = useAuth();

  // Debug logging for authentication state
  useEffect(() => {
    console.info("🔐 Auth state:", { 
      user: !!user, 
      token: token ? `${token.substring(0, 10)}...` : null,
      session: !!session 
    });
  }, [user, token, session]);

  /**
   * Clear any pending file from localStorage
   */
  const clearPendingFile = useCallback(() => {
    localStorage.removeItem(PENDING_FILE_KEY);
  }, []);

  /**
   * Save file to localStorage for persistence across login
   */
  const savePendingFile = useCallback(async (file: File): Promise<void> => {
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
              timestamp: Date.now() // Add timestamp for expiration
            })
          );
          console.info("📁 File saved to localStorage:", file.name);
          resolve();
        } catch (e) {
          console.error("❌ Error saving file to localStorage:", e);
          reject(e);
        }
      };
      
      reader.onerror = () => {
        console.error("❌ Error reading file:", reader.error);
        reject(reader.error);
      };
      
      reader.readAsDataURL(file);
    });
  }, []);

  /**
   * Retrieve pending file from localStorage
   */
  const getPendingFile = useCallback(async (): Promise<{ file: File; route: string } | null> => {
    const raw = localStorage.getItem(PENDING_FILE_KEY);
    if (!raw) return null;
    
    try {
      const { name, type, dataUrl, route, timestamp } = JSON.parse(raw);
      
      // Check if the saved file has expired (24 hours)
      const MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
      if (Date.now() - timestamp > MAX_AGE) {
        console.info("📁 Saved file expired, removing from localStorage");
        clearPendingFile();
        return null;
      }
      
      const res = await fetch(dataUrl);
      const blob = await res.blob();
      console.info("📁 File retrieved from localStorage:", name);
      return { file: new File([blob], name, { type }), route };
    } catch (e) {
      console.error("❌ Error reconstructing file from localStorage:", e);
      clearPendingFile();
      return null;
    }
  }, [clearPendingFile]);

  /**
   * Display a toast message
   */
  const showToast = useCallback((config: ToastConfig) => {
    setToast(config);
    // Auto-dismiss success and info toasts after 5 seconds
    if (config.variant === 'success' || config.variant === 'info') {
      setTimeout(() => setToast(null), 5000);
    }
  }, []);

  /**
   * Handle API errors with appropriate user feedback
   */
  const handleApiError = useCallback((error: unknown, context: string) => {
    console.error(`❌ Error in ${context}:`, error);
    
    let errorMessage: string;
    
    if (error instanceof ApiError) {
      // Use user-friendly message from specialized error classes
      errorMessage = error.getUserMessage();
      
      // Handle authentication errors
      if (error.isAuthError()) {
        return { requiresAuth: true, message: errorMessage };
      }
      
      // Log detailed diagnostics for debugging
      console.debug("🔍 Error diagnostics:", error.getDiagnostics());
    } else if (error instanceof Error) {
      errorMessage = error.message;
    } else {
      errorMessage = "An unknown error occurred";
    }
    
    return { requiresAuth: false, message: errorMessage };
  }, []);

  /**
   * Start the actual conversion process
   */
  const startActualConversion = useCallback(async (engineName: string) => {
    if (!file) return;

    try {
      setIsConverting(true);
      
      // Show starting conversion toast
      showToast({ 
        title: "Info", 
        message: `🚀 ${t("fileUploader.startingConversion")}\n\n` +
                 `🎯 ${t("fileUploader.usingEngine")}: ${engineName}\n\n` +
                 `⏳ ${t("fileUploader.pleaseWait")}`,
        variant: "info" 
      });

      // Create optimized FormData with diagnostic logging
      const formData = createFormData({
        file,
        pipeline_id: engineName
      });

      // Make API request with enhanced error handling
      const data = await apiPost<ConversionResult>("convert", formData, token);
      console.info("✅ Conversion started successfully:", data);

      // Show success toast
      showToast({ 
        title: "Success", 
        message: `✅ ${t("fileUploader.conversionStarted")}\n\n` +
                 `🆔 Task ID: ${data.task_id}\n\n` +
                 `📊 ${t("fileUploader.checkHistory")}`,
        variant: "success" 
      });

      // Call the callback if provided
      if (onConversionStarted) {
        onConversionStarted(data.task_id);
      }

      // Redirect to history page after a short delay
      setTimeout(() => {
        navigate("/");
      }, 2000);

    } catch (error) {
      const { requiresAuth, message } = handleApiError(error, "conversion");
      
      if (requiresAuth) {
        // Save file and redirect to login
        await savePendingFile(file);
        navigate("/login");
        return;
      }
      
      setError(error instanceof Error ? error : new Error(message));
      showToast({ 
        title: "Error", 
        message: `❌ ${t("fileUploader.conversionError")}\n\n${message}`,
        variant: "error" 
      });
    } finally {
      setIsConverting(false);
      clearPendingFile();
    }
  }, [file, token, t, navigate, showToast, handleApiError, savePendingFile, clearPendingFile, onConversionStarted]);

  /**
   * Process any pending file when user is authenticated
   */
  useEffect(() => {
    const processPendingFile = async () => {
      if (!user || !session) return;
      
      const pending = await getPendingFile();
      if (pending) {
        // Navigate to the original route if needed
        if (pending.route && pending.route !== window.location.pathname) {
          navigate(pending.route);
        }
        
        // Set the file and notify parent component
        setFile(pending.file);
        if (onFileSelected) {
          onFileSelected(pending.file);
        }
        
        // Start quick conversion process
        await startQuickConversion(pending.file);
      }
    };
    
    processPendingFile();
  }, [user, session, getPendingFile, navigate, onFileSelected, startQuickConversion]);

  /**
   * Quick analysis and conversion process
   */
  const startQuickConversion = useCallback(async (inputFile?: File) => {
    const fileToUse = inputFile || file;
    if (!fileToUse || isConverting) return;

    setFile(fileToUse);
    setError(null);
    setIsConverting(true);

    try {
      // Show analyzing toast
      showToast({ 
        title: "Info", 
        message: `🔍 ${t("fileUploader.analyzing")}`,
        variant: "info" 
      });
      
      // Create FormData with diagnostic logging
      const formData = createFormData({
        file: fileToUse
      });

      // Make API request with enhanced error handling
      console.info("🔍 Analyzing file:", fileToUse.name);
      const analyzeData = await apiPost<AnalysisResult>("analyze", formData, token);
      console.info("✅ Analysis complete:", analyzeData);

      // Determine recommended engine
      const engineName = analyzeData.recommended || analyzeData.pipeline_id || "balanced";
      const engineNames: Record<string, string> = {
        "rapid": t("engines.rapid"),
        "balanced": t("engines.balanced"),
        "quality": t("engines.quality")
      };
      const recommendedName = engineNames[engineName] || engineName;

      // Check if user is authenticated
      if (!user || !token) {
        // User not authenticated - show message and redirect to login
        showToast({ 
          title: "Info", 
          message: `📊 ${t("fileUploader.analysisComplete")}\n\n` +
                   `🎯 ${t("fileUploader.recommendedEngine")}: ${recommendedName}\n\n` +
                   `💡 ${t("fileUploader.loginToConvert")}`,
          variant: "info" 
        });

        await savePendingFile(fileToUse);

        // Redirect to login after showing the information
        setTimeout(() => {
          navigate("/login");
        }, 1500);
        return;
      } else {
        // User authenticated - proceed with conversion
        await startActualConversion(engineName);
      }
    } catch (error) {
      const { requiresAuth, message } = handleApiError(error, "analysis");
      
      if (requiresAuth) {
        // Save file and redirect to login
        await savePendingFile(fileToUse);
        navigate("/login");
        return;
      }
      
      setError(error instanceof Error ? error : new Error(message));
      showToast({
        title: "Error",
        message: `❌ ${t("fileUploader.analyzeError")}\n\n${message}`,
        variant: "error"
      });
    } finally {
      setIsConverting(false);
    }
  }, [file, isConverting, token, user, t, navigate, showToast, handleApiError, savePendingFile, startActualConversion]);

  /**
   * Handle file drop
   */
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const selectedFile = acceptedFiles[0];
    console.info("📄 File selected:", selectedFile.name, `(${formatFileSize(selectedFile.size)})`);
    
    setFile(selectedFile);
    setError(null);

    if (onFileSelected) {
      onFileSelected(selectedFile);
    }
  }, [onFileSelected]);

  /**
   * Configure dropzone
   */
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"]
    },
    multiple: false,
    maxSize: 25 * 1024 * 1024, // 25MB
    onDropRejected: (rejections) => {
      const rejection = rejections[0];
      if (rejection) {
        if (rejection.errors[0]?.code === "file-too-large") {
          setError(new ValidationError("El archivo excede el tamaño máximo permitido (25MB)"));
        } else {
          setError(new ValidationError(rejection.errors[0]?.message || "Archivo rechazado"));
        }
      }
    }
  });

  /**
   * Reset the upload state
   */
  const resetUpload = useCallback(() => {
    setFile(null);
    setError(null);
    clearPendingFile();
  }, [clearPendingFile]);

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  /**
   * Get CSS classes for the dropzone based on state
   */
  const dropzoneClasses = useMemo(() => {
    const baseClasses = "relative overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer";
    
    if (isDragActive) {
      return `${baseClasses} border-blue-400 scale-105`;
    } else if (file) {
      return `${baseClasses} border-green-400`;
    } else if (error) {
      return `${baseClasses} border-red-400`;
    } else {
      return `${baseClasses} border-gray-300 hover:border-gray-400 bg-uploader-pattern`;
    }
  }, [isDragActive, file, error]);

  /**
   * Get CSS styles for the dropzone based on state
   */
  const dropzoneStyles = useMemo(() => {
    const styles: React.CSSProperties = {};
    
    if (isDragActive) {
      styles.borderColor = "var(--accent-primary)";
      styles.backgroundColor = "rgba(46, 175, 196, 0.15)";
    } else if (file) {
      styles.borderColor = "#10b981";
      styles.backgroundColor = "rgba(16, 185, 129, 0.1)";
    } else if (error) {
      styles.borderColor = "#ef4444";
      styles.backgroundColor = "rgba(239, 68, 68, 0.1)";
    }
    
    return styles;
  }, [isDragActive, file, error]);

  return (
    <>
    <Container>
      <div
        {...getRootProps()}
        className={dropzoneClasses}
        style={dropzoneStyles}
      >
        <input {...getInputProps()} />

        {/* Loading State */}
        {isUploading && (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <div className="w-16 h-16 rounded-full mb-4 flex items-center justify-center"
                 style={{ background: "var(--gradient-action)" }}>
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-lg font-medium" style={{ color: "var(--text-primary)" }}>
              {t("fileUploader.processing")}
            </p>
          </div>
        )}

        {/* Empty State */}
        {!file && !error && !isUploading && (
          <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
            <div className="w-20 h-20 rounded-2xl mb-6 flex items-center justify-center p-3"
                 style={{ background: isDragActive ? "var(--gradient-action)" : "var(--gradient-hero)" }}>
              <img
                src="/images/iconos/Icono PDF.png"
                alt="Icono PDF"
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="text-xl font-semibold mb-2" style={{ color: "var(--text-uploader)" }}>
              {isDragActive ? t("fileUploader.dropHere") : t("fileUploader.uploadTitle")}
            </h3>
            <p className="mb-4 font-medium" style={{ color: "var(--text-uploader)", opacity: "0.9" }}>
              {t("fileUploader.uploadInstructions")}
            </p>
            <div className="flex items-center gap-4 text-sm font-medium" style={{ color: "var(--text-uploader)", opacity: "0.8" }}>
              <span>📋 {t("fileUploader.onlyPDF")}</span>
              <span>📏 Max 25MB</span>
              <span>⚡ {t("fileUploader.fastConversion")}</span>
            </div>
          </div>
        )}

        {/* Success State */}
        {file && !error && !isUploading && (
          <div className="flex items-center justify-between py-6 px-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center p-2"
                   style={{ background: "var(--gradient-nexus)" }}>
                <img
                  src="/images/iconos/Icono PDF.png"
                  alt="Icono PDF"
                  className="w-full h-full object-contain"
                />
              </div>
              <div>
                <h4 className="font-semibold text-lg" style={{ color: "var(--text-primary)" }}>
                  {file.name}
                </h4>
                <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
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
                 style={{ background: "var(--bg-secondary)" }}>
              <img
                src="/images/iconos/Icono PDF.png"
                alt="Icono PDF"
                className="w-full h-full object-contain opacity-60"
              />
              <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center"
                   style={{ background: "var(--accent-primary)" }}>
                <span className="text-white text-xs font-bold">!</span>
              </div>
            </div>
            <h3 className="text-lg font-semibold mb-2" style={{ color: "var(--text-primary)" }}>
              {t("fileUploader.uploadError")}
            </h3>
            <div className="mb-4 p-3 rounded-lg" style={{
              background: "var(--bg-secondary)",
              border: "1px solid var(--border-color)"
            }}>
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                {error instanceof Error ? error.message : String(error)}
              </p>
            </div>
            <button
              onClick={resetUpload}
              className="btn btn-secondary"
            >
              {t("fileUploader.tryAgain")}
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
            🔄 {t("fileUploader.changeFile")}
          </button>
          <button
            className="btn btn-primary"
            onClick={() => startQuickConversion()}
            disabled={isConverting}
          >
            {isConverting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {t("fileUploader.processing")}
              </>
            ) : (
              <>🔍 {t("fileUploader.convertNow")}</>
            )}
          </button>
        </div>
      )}

      {/* Info message about advanced options */}
      {file && !error && !isUploading && !isConverting && (
        <div className="text-center mt-3">
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            💡 {t("fileUploader.advancedOptionsBelow")}
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
