import React from 'react';

interface ToastProps {
  message: string;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ message, onClose }) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded shadow-md transition animate-fade-in"
    >
      <span>{message}</span>
      <button
        onClick={onClose}
        aria-label="Close"
        className="ml-2 text-white"
      >
        &times;
      </button>
    </div>
  );
};

export default Toast;
