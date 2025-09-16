import React from 'react';

interface CircularProgressProps {
  progress: number;
  size?: number;
  strokeWidth?: number;
  showPercentage?: boolean;
  className?: string;
}

const CircularProgress: React.FC<CircularProgressProps> = ({
  progress,
  size = 80,
  strokeWidth = 8,
  showPercentage = true,
  className = ''
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  // Gradiente de colores basado en el progreso (Anclora Nexus + Press)
  const getProgressColor = (progress: number) => {
    if (progress < 25) return '#38BDF8'; // Azul Nexus
    if (progress < 50) return '#2EAFC4'; // Turquesa
    if (progress < 75) return '#FFC979'; // Amarillo Press
    return '#23436B'; // Azul oscuro (completado)
  };

  const getGradientStops = (progress: number) => {
    const startColor = '#38BDF8';
    const midColor = '#2EAFC4';
    const endColor = '#FFC979';
    const completeColor = '#23436B';

    if (progress < 50) {
      return [startColor, midColor];
    } else if (progress < 100) {
      return [midColor, endColor];
    } else {
      return [endColor, completeColor];
    }
  };

  const gradientStops = getGradientStops(progress);
  const currentColor = getProgressColor(progress);

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
        style={{
          filter: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))'
        }}
      >
        <defs>
          <linearGradient id={`progress-gradient-${progress}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={gradientStops[0]} />
            <stop offset="100%" stopColor={gradientStops[1]} />
          </linearGradient>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="rgba(0,0,0,0.3)"/>
          </filter>
        </defs>

        {/* Círculo de fondo */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#F6F7F9"
          strokeWidth={strokeWidth}
          fill="none"
          className="opacity-30"
        />

        {/* Círculo de progreso */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={`url(#progress-gradient-${progress})`}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          filter="url(#shadow)"
          style={{
            transition: 'stroke-dashoffset 0.3s ease, stroke 0.3s ease',
          }}
        />
      </svg>

      {/* Porcentaje en el centro */}
      {showPercentage && (
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            fontSize: `${size * 0.2}px`,
            fontWeight: '600',
            color: currentColor,
            textShadow: '0 1px 2px rgba(0,0,0,0.1)'
          }}
        >
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
};

export default CircularProgress;