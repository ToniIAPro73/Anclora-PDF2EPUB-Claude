import React, { useState, useEffect } from 'react';
import CircularProgress from './CircularProgress';

const CircularProgressTest: React.FC = () => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 0 : prev + 10));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 bg-gray-100 min-h-screen flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h2 className="text-xl font-bold mb-4 text-center">Test de Barra Circular</h2>
        <CircularProgress
          progress={progress}
          size={120}
          strokeWidth={10}
          showPercentage={true}
          className="mb-4"
        />
        <p className="text-center text-gray-600">
          Progreso actual: {progress}%
        </p>
        <div className="mt-4 text-center">
          <button
            onClick={() => setProgress(25)}
            className="mx-2 px-4 py-2 bg-blue-500 text-white rounded"
          >
            25%
          </button>
          <button
            onClick={() => setProgress(50)}
            className="mx-2 px-4 py-2 bg-blue-500 text-white rounded"
          >
            50%
          </button>
          <button
            onClick={() => setProgress(75)}
            className="mx-2 px-4 py-2 bg-blue-500 text-white rounded"
          >
            75%
          </button>
          <button
            onClick={() => setProgress(100)}
            className="mx-2 px-4 py-2 bg-blue-500 text-white rounded"
          >
            100%
          </button>
        </div>
      </div>
    </div>
  );
};

export default CircularProgressTest;