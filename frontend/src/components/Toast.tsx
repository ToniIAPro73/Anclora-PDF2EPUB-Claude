import React, { useEffect } from 'react';

interface ToastProps {
  message: string;
  type?: 'info' | 'success' | 'error';
  onClose: () => void;
}

const bgColors = {
  info: 'bg-blue-500',
  success: 'bg-green-500',
  error: 'bg-red-500'
};

const Toast: React.FC<ToastProps> = ({ message, type = 'info', onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`fixed bottom-4 right-4 px-4 py-2 text-white rounded shadow-lg ${bgColors[type]}`}>
      {message}
    </div>
  );
};

export default Toast;
