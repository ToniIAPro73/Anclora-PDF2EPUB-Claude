import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../AuthContext';
import renderMathInElement from 'katex/contrib/auto-render';
import { createSafeHTML, SanitizationMetrics } from '../utils/sanitize';

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

const PreviewModal: React.FC<PreviewModalProps> = ({ taskId, onClose }) => {
  const { token } = useAuth();
  const [pages, setPages] = useState<string[]>([]);
  const [index, setIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`/api/preview/${taskId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (res.ok) {
        
        setPages(data.pages || []);
      }
    };
    load();
  }, [taskId, token]);

  useEffect(() => {
    document.querySelectorAll('.preview-body').forEach((el) => {
      renderMathInElement(el as HTMLElement, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\\(', right: '\\)', display: false },
        ],
      });
    });
  }, [pages, index]);

  const next = () => setIndex((i) => Math.min(i + 1, pages.length - 1));
  const prev = () => setIndex((i) => Math.max(i - 1, 0));

  return (
    <div
      className="modal-overlay transition animate-fade-in"
      role="dialog"
      aria-modal="true"
    >
      <div className="modal-content transition animate-fade-in" aria-live="assertive">
        <button onClick={onClose}>Cerrar</button>
        {pages.length > 0 ? (
          <div>
            <div
              ref={containerRef}
              className="preview-body"
              dangerouslySetInnerHTML={SanitizationMetrics.measureSanitization(
                () => createSafeHTML(pages[index]),
                pages[index]?.length || 0
              )}
            />
            <div className="preview-nav">
              <button onClick={prev} disabled={index === 0}>
                Anterior
              </button>
              <span>
                {index + 1} / {pages.length}
              </span>
              <button onClick={next} disabled={index === pages.length - 1}>
                Siguiente
              </button>
            </div>
          </div>
        ) : (
          <p>Cargando...</p>
        )}
      </div>
    </div>
  );
};

export default PreviewModal;

