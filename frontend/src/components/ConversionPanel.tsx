import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { ApiError } from "../lib/errors";
import { apiGet, apiPost } from "../lib/apiClient";
import PreviewModal from "./PreviewModal";
import Toast from "./Toast";
import CircularProgress from "./CircularProgress";
import CreditBalance from "./CreditBalance";
import { useTranslation } from "react-i18next";
import AIChatBox from "./AIChatBox";

interface ConversionPanelProps {
  file: File | null;
  onConversionStateChange?: (state: {
    isConverting: boolean;
    progress: number;
    statusMessage: string;
  }) => void;
  onPipelineDataChange?: (data: {
    pipelines: PipelineOption[];
    selectedPipeline: string;
    userCredits: number;
    analysisData: any;
  }) => void;
}

interface PipelineOption {
  id: string;
  quality: string;
  estimated_time: number;
  estimated_cost?: number;
  cost_breakdown?: {
    base_cost: number;
    cost_per_page: number;
    total_pages: number;
  };
}

interface StatusResponse {
  status: string;
  progress?: number;
  message?: string;
  error?: string;
  result?: {
    output_path: string;
  };
}

const ConversionPanel: React.FC<ConversionPanelProps> = ({ file, onConversionStateChange, onPipelineDataChange }) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isConverting, setIsConverting] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [pipelines, setPipelines] = useState<PipelineOption[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<string>("");
  const [showPreview, setShowPreview] = useState(false);
  const [currentCredits, setCurrentCredits] = useState<number>(0);
  const [canAffordConversion, setCanAffordConversion] = useState<boolean>(true);
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Verificar si el usuario puede costear la conversión seleccionada
  const checkAffordability = () => {
    const selectedOption = pipelines.find(p => p.id === selectedPipeline);
    if (selectedOption && selectedOption.estimated_cost) {
      setCanAffordConversion(currentCredits >= selectedOption.estimated_cost);
    } else {
      setCanAffordConversion(true);
    }
  };

  // Ejecutar verificación cuando cambien los créditos o el pipeline seleccionado
  useEffect(() => {
    checkAffordability();
  }, [currentCredits, selectedPipeline, pipelines]);

  // Notificar cambios de estado de conversión al componente padre
  useEffect(() => {
    if (onConversionStateChange) {
      onConversionStateChange({
        isConverting,
        progress,
        statusMessage
      });
    }
  }, [isConverting, progress, statusMessage, onConversionStateChange]);

  // Notificar cambios de datos de pipeline al componente padre
  useEffect(() => {
    if (onPipelineDataChange) {
      onPipelineDataChange({
        pipelines,
        selectedPipeline,
        userCredits: currentCredits,
        analysisData: pipelines.length > 0 ? {
          page_count: 6,
          content_type: "document",
          complexity_score: 3,
          issues: [],
          recommended: pipelines[1]?.id
        } : null
      });
    }
  }, [pipelines, selectedPipeline, currentCredits, onPipelineDataChange]);

  const analyzeFile = async () => {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
    setPipelines([]);
    setSelectedPipeline("");
    
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const data = await apiPost("analyze", formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setPipelines(data.pipelines || []);
      
      // Auto-select the middle pipeline (intermediate) by default
      // But delay showing cards until animation finishes (2.5 seconds total)
      setTimeout(() => {
        if (data.pipelines?.length > 0) {
          // Seleccionar el del medio por defecto
          const middleIndex = Math.floor(data.pipelines.length / 2);
          setSelectedPipeline(data.pipelines[middleIndex].id);
        }
      }, 2500); // Wait 2.5 seconds to match animation duration
    } catch (err) {
      console.error("Error analyzing file:", err);
      if (err instanceof ApiError && err.code === "UNAUTHORIZED") {
        logout();
        navigate("/login");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to analyze file");
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    if (file) {
      analyzeFile();
    } else {
      setPipelines([]);
      setSelectedPipeline("");
    }
  }, [file]);

  const startConversion = async () => {
    if (!file || !selectedPipeline) return;

    // Verificar créditos antes de iniciar
    if (!canAffordConversion) {
      const selectedOption = pipelines.find(p => p.id === selectedPipeline);
      const cost = selectedOption?.estimated_cost || 0;
      setError(`Créditos insuficientes. Necesitas ${cost} créditos, pero solo tienes ${currentCredits}.`);
      return;
    }

    setError(null);
    setTaskId(null);
    setStatus(null);
    setProgress(0);
    setStatusMessage("");
    setIsConverting(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("pipeline_id", selectedPipeline);

      const data = await apiPost("convert", formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setTaskId(data.task_id);
      pollStatus(data.task_id);
    } catch (err) {
      console.error("Error starting conversion:", err);
      if (err instanceof ApiError && err.code === "UNAUTHORIZED") {
        logout();
        navigate("/login");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to start conversion");
      setIsConverting(false);
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const data = await apiGet<StatusResponse>(`status/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        setStatus(data.status);
        if (data.status === "PROGRESS") {
          if (typeof data.progress === "number") {
            setProgress(data.progress);
          }
          if (data.message) {
            setStatusMessage(data.message);
          }
        } else if (data.status === "SUCCESS") {
          clearInterval(interval);
          setIsConverting(false);
          setProgress(100);
          setStatusMessage(t("conversionPanel.completed"));
          if (data.result && data.result.output_path) {
            const downloadRes = await fetch(data.result.output_path);
            const blob = await downloadRes.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = data.result.output_path.split("/").pop() || "resultado.epub";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
          }
        } else if (data.status === "FAILURE") {
          clearInterval(interval);
          setIsConverting(false);
          setError(data.error || t("conversionPanel.conversionError"));
          setStatusMessage("");
        }
      } catch (err) {
        clearInterval(interval);
        setIsConverting(false);
        if (err instanceof ApiError && err.code === "UNAUTHORIZED") {
          logout();
          navigate("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to check conversion status");
      }
    }, 2000);
    
    // Return cleanup function
    return () => clearInterval(interval);
  };

  return (
    <div className="conversion-panel relative">
      {pipelines.length > 0 && (
        <div className="pipeline-selection">
          {/* Cards en columna vertical compacta */}
          <div className="flex flex-col space-y-3">
            {pipelines.map((p, index) => {
              // Calcular la parte del degradado para cada card (igual al botón)
              const getCardGradient = (cardIndex: number) => {
                // Degradado continuo basado en el botón: turquesa → naranja claro
                const gradientStops = [
                  '#2EAFC4', // Inicio turquesa
                  '#7DD3FC', // Medio azul claro
                  '#FFC979'  // Final naranja claro
                ];

                return `linear-gradient(135deg, ${gradientStops[cardIndex]}, ${gradientStops[cardIndex + 1] || gradientStops[cardIndex]})`;
              };

              const isSelected = selectedPipeline === p.id;

              return (
                <div
                  key={p.id}
                  onClick={() => setSelectedPipeline(p.id)}
                  className="pipeline-card cursor-pointer relative transition-all duration-300 hover:scale-105"
                  style={{
                    background: getCardGradient(index),
                    border: isSelected ? '2px solid #1E3A8A' : '2px solid #000000',
                    borderRadius: '16px',
                    padding: '32px 24px',
                    boxShadow: isSelected
                      ? '0 8px 30px rgba(30, 58, 138, 0.4), 0 0 20px rgba(30, 58, 138, 0.3)'
                      : '0 2px 6px rgba(0, 0, 0, 0.1)',
                    minHeight: '160px',
                    width: '100%',
                    transform: isSelected ? 'translateY(-2px)' : 'translateY(0)',
                  }}
                >
                  <div className="text-center h-full flex flex-col justify-between">

                    <h4 className="font-semibold text-xl mb-4" style={{
                      color: isSelected ? '#FFFFFF' : '#23436B',
                      textShadow: isSelected ? '0 1px 2px rgba(0,0,0,0.3)' : 'none'
                    }}>
                      {t(`engines.${p.quality}`)}
                    </h4>

                    <div className="text-base mb-3" style={{
                      color: isSelected ? 'rgba(255,255,255,0.95)' : '#162032',
                      fontWeight: '500'
                    }}>
                      <div className="mb-3">⏱️ {p.estimated_time}s</div>
                      {p.estimated_cost && (
                        <div className="font-semibold text-lg" style={{
                          color: isSelected ? '#FFF' : '#23436B'
                        }}>
                          💰 {p.estimated_cost} {p.estimated_cost === 1 ? 'crédito' : 'créditos'}
                        </div>
                      )}
                    </div>

                  {isSelected && (
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center" style={{
                      boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
                    }}>
                      <span className="text-sm text-blue-800">✓</span>
                    </div>
                  )}
                </div>
              </div>
              );
            })}
          </div>
        </div>
      )}


      {status && !isConverting && <p>{t("conversionPanel.status", { status })}</p>}
      {error && (
        <Toast
          title="Error"
          message={error}
          variant="error"
          onClose={() => setError(null)}
        />
      )}
      {showPreview && taskId && (
        <PreviewModal
          taskId={taskId}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
};

export default ConversionPanel;
