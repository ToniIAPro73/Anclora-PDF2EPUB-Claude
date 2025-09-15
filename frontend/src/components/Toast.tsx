import React from 'react';

interface ToastProps {
  title: string;
  message: string;
  variant: 'success' | 'error';
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ title, message, variant = 'success', onClose }) => {
  // Styles based on variant
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
      className={`${baseClasses} ${getToastStyles()}`}
    >
      <div>
        <span className={titleClasses}>{title}</span>
        <span className={messageClasses}>{message}</span>
      </div>
      <button
        onClick={onClose}
        aria-label="Close"
        className="ml-3 text-white hover:text-gray-200"
      >
        &times;
      </button>
    </div>
  );
};

export default Toast;
