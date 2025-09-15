import React from 'react';

interface ModalProps {
  title: string;
  message: string;
  type: 'success' | 'error';
  isOpen: boolean;
  onClose?: () => void;
}

const Modal: React.FC<ModalProps> = ({ title, message, type, isOpen, onClose }) => {
  if (!isOpen) return null;

  const colorClass = type === 'success' ? 'text-green-600' : 'text-red-600';

  return (
    <div
      className="fixed inset-0 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      onClick={onClose}
    >
      <div
        className="rounded-lg p-6 max-w-sm w-full"
        style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', boxShadow: 'var(--shadow-md)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className={`text-lg font-semibold mb-4 ${colorClass}`}>{title}</h2>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default Modal;

