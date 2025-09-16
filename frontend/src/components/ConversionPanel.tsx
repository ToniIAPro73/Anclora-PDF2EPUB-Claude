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

interface ConversionPanelProps {
  file: File | null;
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

const ConversionPanel: React.FC<ConversionPanelProps> = ({ file }) => {
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

  const analyzeFile = async () => {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
    setPipelines([]);
    setSelectedPipeline("");
    
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      console.log("Analyzing file with token:", token ? "Present" : "Missing");
      const data = await apiPost("analyze", formData, token);
      setPipelines(data.pipelines || []);
      
      // Auto-select the recommended pipeline if available
      if (data.recommended && data.pipelines?.length > 0) {
        setSelectedPipeline(data.recommended);
      } else if (data.pipelines?.length > 0) {
        setSelectedPipeline(data.pipelines[0].id);
      }
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

      console.log("Starting conversion with token:", token ? "Present" : "Missing");
      const data = await apiPost("convert", formData, token);
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
        console.log("Checking status with token:", token ? "Present" : "Missing");
        const data = await apiGet<StatusResponse>(`status/${id}`, token);
        
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
    <div className="conversion-panel">
      {isAnalyzing && <p>{t("conversionPanel.analyzing")}</p>}
      {pipelines.length > 0 && (
        <div className="pipeline-selection">
          <h3 className="text-lg font-semibold mb-6 text-center" style={{color: '#23436B'}}>{t("conversionPanel.options")}</h3>
          <div className="grid grid-cols-3 gap-3 max-w-md mx-auto">
            {pipelines.map((p) => (
              <div
                key={p.id}
                onClick={() => setSelectedPipeline(p.id)}
                className="pipeline-card cursor-pointer relative transition-all duration-300 hover:scale-105"
                style={{
                  background: selectedPipeline === p.id
                    ? `linear-gradient(135deg, ${
                        p.quality === 'low' ? '#38BDF8, #2EAFC4' :
                        p.quality === 'medium' ? '#2EAFC4, #FFC979' :
                        '#FFC979, #23436B'
                      })`
                    : 'linear-gradient(135deg, #F6F7F9, #FFFFFF)',
                  border: selectedPipeline === p.id ? '2px solid #23436B' : '2px solid #E1E8ED',
                  borderRadius: '12px',
                  padding: '16px 12px',
                  boxShadow: selectedPipeline === p.id
                    ? '0 8px 25px rgba(46, 175, 196, 0.3)'
                    : '0 2px 8px rgba(0, 0, 0, 0.08)',
                  minHeight: '120px'
                }}
              >
                <div className="text-center h-full flex flex-col justify-between">
                  <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${
                    selectedPipeline === p.id ? 'bg-white shadow-sm' :
                    p.quality === 'low' ? 'bg-gradient-to-r from-green-400 to-green-500' :
                    p.quality === 'medium' ? 'bg-gradient-to-r from-yellow-400 to-orange-400' :
                    'bg-gradient-to-r from-orange-400 to-red-500'
                  }`} style={{
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}></div>

                  <h4 className="font-semibold text-sm mb-1" style={{
                    color: selectedPipeline === p.id ? '#FFFFFF' : '#23436B',
                    textShadow: selectedPipeline === p.id ? '0 1px 2px rgba(0,0,0,0.2)' : 'none'
                  }}>
                    {t(`engines.${p.quality}`)}
                  </h4>

                  <div className="text-xs mb-1" style={{
                    color: selectedPipeline === p.id ? 'rgba(255,255,255,0.9)' : '#162032',
                    opacity: 0.8
                  }}>
                    <div>{p.estimated_time}s</div>
                    {p.estimated_cost && (
                      <div className="font-semibold mt-1" style={{
                        color: selectedPipeline === p.id ? '#FFF' : '#23436B'
                      }}>
                        💰 {p.estimated_cost} {p.estimated_cost === 1 ? 'crédito' : 'créditos'}
                      </div>
                    )}
                  </div>

                  <div className="text-xs" style={{
                    color: selectedPipeline === p.id ? 'rgba(255,255,255,0.8)' : '#162032',
                    opacity: 0.7
                  }}>
                    {p.quality === 'low' && '⚡'}
                    {p.quality === 'medium' && '⚖️'}
                    {p.quality === 'high' && '✨'}
                  </div>

                  {selectedPipeline === p.id && (
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center" style={{
                      boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
                    }}>
                      <span className="text-xs text-blue-600">✓</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {isConverting && (
        <div className="flex flex-col items-center mt-6 mb-4">
          <CircularProgress
            progress={progress}
            size={120}
            strokeWidth={10}
            showPercentage={true}
            className="mb-4"
          />
          <p className="text-sm text-center max-w-xs" style={{color: '#23436B'}}>
            {statusMessage || t("conversionPanel.progress", { progress })}
          </p>
        </div>
      )}

      {/* Sección de créditos y advertencias */}
      {pipelines.length > 0 && selectedPipeline && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-2">
                Balance de Créditos
              </h4>
              <CreditBalance onCreditsUpdate={setCurrentCredits} />
            </div>

            {/* Botón de conversión con verificación de créditos */}
            <div className="text-right">
              <button
                onClick={startConversion}
                disabled={isConverting || isAnalyzing || !canAffordConversion}
                className={`px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 ${
                  canAffordConversion && !isConverting && !isAnalyzing
                    ? 'bg-blue-600 hover:bg-blue-700 hover:scale-105 shadow-md'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
                style={{
                  background: canAffordConversion && !isConverting && !isAnalyzing
                    ? 'linear-gradient(135deg, #2EAFC4 0%, #23436B 100%)'
                    : undefined
                }}
              >
                {isConverting ? 'Convirtiendo...' : 'Analizar y convertir'}
              </button>

              {/* Advertencia de créditos insuficientes */}
              {!canAffordConversion && (
                <div className="mt-2 text-xs text-red-600">
                  ⚠️ Créditos insuficientes para esta conversión
                </div>
              )}
            </div>
          </div>

          {/* Detalles del costo */}
          {(() => {
            const selectedOption = pipelines.find(p => p.id === selectedPipeline);
            if (selectedOption?.estimated_cost) {
              return (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">
                      Costo de conversión ({selectedOption.quality}):
                    </span>
                    <span className="font-semibold">
                      {selectedOption.estimated_cost} créditos
                    </span>
                  </div>
                  {selectedOption.cost_breakdown && (
                    <div className="mt-1 text-xs text-gray-500">
                      Base: {selectedOption.cost_breakdown.base_cost} +
                      {selectedOption.cost_breakdown.cost_per_page} ×
                      ({selectedOption.cost_breakdown.total_pages - 1} páginas adicionales)
                    </div>
                  )}
                </div>
              );
            }
            return null;
          })()}
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
