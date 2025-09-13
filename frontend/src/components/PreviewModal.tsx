import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../AuthContext';

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
        const data = await res.json();
        setPages(data.pages || []);
      }
    };
    load();
  }, [taskId, token]);

  useEffect(() => {
    const typeset = async () => {
      if (import.meta.env.MODE === 'test') return;
      if (!containerRef.current) return;
      if (!window.MathJax) {
        // @ts-ignore - MathJax no provee declaraciones de tipo para este import
        await import('mathjax/es5/tex-mml-chtml.js');
      }
      containerRef.current
        .querySelectorAll('span.math-inline')
        .forEach((el) => {
          const tex = el.textContent || '';
          // @ts-ignore - MathJax proporciona esta utilidad en tiempo de ejecución
          const node = window.MathJax.tex2chtml(tex, { display: false });
          el.replaceWith(node);
        });
      window.MathJax?.typesetPromise?.([containerRef.current]);
    };
    typeset();
  }, [pages, index]);

  const next = () => setIndex((i) => Math.min(i + 1, pages.length - 1));
  const prev = () => setIndex((i) => Math.max(i - 1, 0));

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button onClick={onClose}>Cerrar</button>
        {pages.length > 0 ? (
          <div>
            <div
              ref={containerRef}
              className="preview-body"
              dangerouslySetInnerHTML={{ __html: pages[index] }}
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
