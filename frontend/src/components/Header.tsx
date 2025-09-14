import React from 'react';
import { useAuth } from '../AuthContext';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  currentSection: string;
  setCurrentSection: (section: string) => void;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme, currentSection, setCurrentSection }) => {
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const navigationItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
    { id: 'conversion', label: 'Convertir', icon: '🔄' },
    { id: 'history', label: 'Historial', icon: '📋' },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-sm border-b"
            style={{
              background: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
              boxShadow: 'var(--shadow-sm)'
            }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo y Marca */}
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg p-1"
                 style={{ background: 'var(--gradient-hero)' }}>
              <img
                src="/images/iconos/Anclora PDF2EPUB fodo transparente.png"
                alt="Anclora PDF2EPUB"
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex items-center h-16">
              <h1 className="text-xl font-bold" style={{ lineHeight: '1', margin: '0', padding: '0', color: 'var(--text-header)' }}>Anclora PDF2EPUB</h1>
            </div>
          </div>

          {/* Navegación Central */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentSection(item.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  currentSection === item.id
                    ? 'text-white shadow-md'
                    : 'hover:bg-gray-100'
                }`}
                style={currentSection === item.id
                  ? { background: 'var(--gradient-action)' }
                  : { color: 'var(--text-nav)' }
                }
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Controles de Usuario */}
          <div className="flex items-center gap-3">
            {/* Toggle de Tema */}
            <button
              onClick={toggleTheme}
              aria-label="Cambiar tema"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105"
              style={{
                background: theme === 'dark'
                  ? 'linear-gradient(90deg, #FFC979 70%, #2EAFC4 100%)'
                  : 'linear-gradient(120deg, #2EAFC4 70%, #FFC979 100%)',
                color: 'var(--anclora-dark)'
              }}
            >
              <span>{theme === 'dark' ? '☀️' : '🌙'}</span>
              <span className="hidden sm:inline">
                {theme === 'dark' ? 'Claro' : 'Oscuro'}
              </span>
            </button>

            {/* Usuario */}
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white"
                   style={{ background: 'var(--gradient-nexus)' }}>
                {user?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {user || 'Usuario'}
                </p>
              </div>
            </div>

            {/* Botón de Logout */}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:bg-red-50 hover:text-red-600"
              style={{ color: 'var(--text-secondary)' }}
            >
              <span>🚪</span>
              <span className="hidden sm:inline">Salir</span>
            </button>
          </div>
        </div>

        {/* Navegación Móvil */}
        <div className="md:hidden border-t" style={{ borderColor: 'var(--border-color)' }}>
          <nav className="flex justify-around py-2">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentSection(item.id)}
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 ${
                  currentSection === item.id
                    ? 'text-white'
                    : ''
                }`}
                style={currentSection === item.id
                  ? { background: 'var(--gradient-action)' }
                  : { color: 'var(--text-nav)' }
                }
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
