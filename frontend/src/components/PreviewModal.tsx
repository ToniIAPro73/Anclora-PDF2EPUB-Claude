import React, { useEffect, useRef, useState } from "react";
import { useAuth } from "../AuthContext";
import { ApiError } from "../lib/errors";
import { apiGet } from "../lib/apiClient";
import renderMathInElement from "katex/contrib/auto-render";
import { createSafeHTML, SanitizationMetrics } from "../utils/sanitize";

declare global {
  interface Window {
    MathJax?: {
      typesetPromise?: (elements?: Element[]) => Promise<void>;
    };
  }
}

interface PreviewModalProps {
  taskId: string;
  onClose: () => void;
}

interface PreviewResponse {
  pages: string[];
  metadata?: {
    title?: string;
    author?: string;
    totalPages?: number;
  };
}

const PreviewModal: React.FC<PreviewModalProps> = ({ taskId, onClose }) => {
  const { token } = useAuth();
  const [pages, setPages] = useState<string[]>([]);
  const [index, setIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        console.log("Loading preview with token:", token ? "Present" : "Missing");
        const data = await apiGet<PreviewResponse>(`preview/${taskId}`, token);
        setPages(data.pages || []);
        setError(null);
      } catch (err) {
        console.error("Error loading preview:", err);
        if (err instanceof ApiError && err.code === "UNAUTHORIZED") {
          setError("Session expired. Please log in again.");
        } else {
          setError(err instanceof Error ? err.message : "Failed to load preview");
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [taskId, token]);

  useEffect(() => {
    // Render math equations when pages or index changes
    if (containerRef.current) {
      try {
        renderMathInElement(containerRef.current, {
          delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "\\(", right: "\\)", display: false },
          ],
        });
      } catch (err) {
        console.error("Error rendering math:", err);
      }
    }
  }, [pages, index]);

  const next = () => setIndex((i) => Math.min(i + 1, pages.length - 1));
  const prev = () => setIndex((i) => Math.max(i - 1, 0));

  return (
    <div
      className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition animate-fade-in"
      role="dialog"
      aria-modal="true"
    >
      <div className="modal-content bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col transition animate-fade-in" aria-live="assertive">
        <div className="modal-header flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Vista previa</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="modal-body flex-grow overflow-auto p-6">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
            </div>
          ) : error ? (
            <div className="text-red-500 p-4 text-center">
              <p>{error}</p>
            </div>
          ) : pages.length > 0 ? (
            <div>
              <div
                ref={containerRef}
                className="preview-body prose max-w-none"
                dangerouslySetInnerHTML={SanitizationMetrics.measureSanitization(
                  () => createSafeHTML(pages[index]),
                  pages[index]?.length || 0
                )}
              />
            </div>
          ) : (
            <p className="text-center text-gray-500">No hay contenido disponible para previsualizar</p>
          )}
        </div>
        
        {pages.length > 0 && (
          <div className="modal-footer border-t p-4 flex justify-between items-center">
            <button 
              onClick={prev} 
              disabled={index === 0}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              ← Anterior
            </button>
            <span className="text-sm">
              Página {index + 1} de {pages.length}
            </span>
            <button 
              onClick={next} 
              disabled={index === pages.length - 1}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              Siguiente →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PreviewModal;
