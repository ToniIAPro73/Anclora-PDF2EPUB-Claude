import React from 'react';

export interface ToastProps {
  title: string;
  message: string;
  variant: 'success' | 'error';
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ title, message, variant, onClose }) => {
  // Define styles based on toast variant
  const getToastStyles = () => {
    switch (variant) {
      case 'success':
        return 'bg-green-600 text-white';
      case 'error':
      default:
        return 'bg-red-600 text-white';
    }
  };

  const baseClasses =
    'fixed bottom-4 right-4 px-4 py-3 rounded shadow-md transition animate-fade-in max-w-sm';

  const titleClasses = 'block font-semibold mb-1';
  const messageClasses = 'block text-sm opacity-95';

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`fixed bottom-4 right-4 px-4 py-3 rounded shadow-md transition animate-fade-in ${getToastStyles()}`}
    >
      <strong className="block font-semibold">{title}</strong>
      <span className="block mt-1">{message}</span>
      <button
        onClick={onClose}
        aria-label="Close"
        className="absolute top-1 right-2 text-white hover:text-gray-200"
      >
        &times;
      </button>
    </div>
  );
};

export default Toast;
