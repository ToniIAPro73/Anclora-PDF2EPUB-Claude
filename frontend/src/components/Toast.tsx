import React from 'react';

interface ToastProps {
  message: string;
  variant?: 'info' | 'success' | 'error';
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ message, variant = 'info', onClose }) => {
  // Define styles based on toast type
  const getToastStyles = () => {
    switch (variant) {
      case 'success':
        return 'bg-green-600 text-white';
      case 'error':
        return 'bg-red-600 text-white';
      case 'info':
      default:
        return 'bg-gray-800 text-white';
    }
  };

  const baseClasses =
    'fixed bottom-4 right-4 px-4 py-2 rounded shadow-md transition animate-fade-in';

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`${baseClasses} ${getToastStyles()}`}
    >
      <span>{message}</span>
      <button
        onClick={onClose}
        aria-label="Close"
        className="ml-2 text-white hover:text-gray-200"
      >
        &times;
      </button>
    </div>
  );
};

export default Toast;
