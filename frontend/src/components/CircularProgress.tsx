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

  // Degradado del azul oscuro al verde agua claro
  const getProgressColor = (progress: number) => {
    // Interpolación entre azul oscuro (#23436B) y verde agua claro (#7DD3FC)
    const darkBlue = { r: 35, g: 67, b: 107 };
    const lightAqua = { r: 125, g: 211, b: 252 };

    const ratio = progress / 100;
    const r = Math.round(darkBlue.r + (lightAqua.r - darkBlue.r) * ratio);
    const g = Math.round(darkBlue.g + (lightAqua.g - darkBlue.g) * ratio);
    const b = Math.round(darkBlue.b + (lightAqua.b - darkBlue.b) * ratio);

    return `rgb(${r}, ${g}, ${b})`;
  };

  const getGradientStops = () => {
    return ['#23436B', '#2EAFC4', '#7DD3FC']; // Azul oscuro -> Turquesa -> Verde agua claro
  };

  const gradientStops = getGradientStops();
  const currentColor = getProgressColor(progress);

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
        style={{
          filter: 'drop-shadow(0 6px 12px rgba(35, 67, 107, 0.25))'
        }}
      >
        <defs>
          <linearGradient
            id={`progress-gradient-${progress}`}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
            gradientUnits="objectBoundingBox"
          >
            <stop offset="0%" stopColor={gradientStops[0]} />
            <stop offset="50%" stopColor={gradientStops[1]} />
            <stop offset="100%" stopColor={gradientStops[2]} />
          </linearGradient>

          <filter id={`shadow-${progress}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="0" dy="3" result="offset"/>
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.4"/>
            </feComponentTransfer>
            <feMerge>
              <feMergeNode/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>

          <filter id={`inner-shadow-${progress}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2"/>
            <feOffset dx="0" dy="-1" result="offset"/>
            <feComposite in2="SourceGraphic" operator="subtract"/>
          </filter>
        </defs>

        {/* Círculo de fondo con relieve */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E2E8F0"
          strokeWidth={strokeWidth}
          fill="none"
          className="opacity-40"
          style={{
            filter: 'inset 0 2px 4px rgba(0,0,0,0.1)'
          }}
        />

        {/* Círculo de progreso con degradado y relieve */}
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
          filter={`url(#shadow-${progress})`}
          style={{
            transition: 'stroke-dashoffset 0.5s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease',
            strokeShadow: 'inset 0 1px 2px rgba(255,255,255,0.3), 0 2px 4px rgba(35,67,107,0.2)'
          }}
        />

        {/* Círculo interior para efecto de relieve */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius - strokeWidth / 4}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="1"
          fill="none"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{
            transition: 'stroke-dashoffset 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </svg>

      {/* Porcentaje en el centro con relieve */}
      {showPercentage && (
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            fontSize: `${size * 0.22}px`,
            fontWeight: '700',
            color: currentColor,
            textShadow: `
              0 1px 0 rgba(255,255,255,0.4),
              0 2px 4px rgba(35,67,107,0.3),
              0 0 8px rgba(125,211,252,0.2)
            `,
            background: `linear-gradient(135deg,
              rgba(255,255,255,0.1) 0%,
              rgba(255,255,255,0.05) 50%,
              transparent 100%)`,
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            filter: 'drop-shadow(0 1px 2px rgba(35,67,107,0.2))'
          }}
        >
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
};

export default CircularProgress;