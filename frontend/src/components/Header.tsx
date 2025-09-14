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

  // Debug log temporal
  console.log('Header render - user value:', JSON.stringify(user));



  const handleLogout = () => {
    logout();
  };

  // Helper function to get user initials
  const getUserInitials = (username: string | null): string => {
    if (!username) return 'U';

    const words = username.trim().split(' ');
    if (words.length >= 2) {
      // If there are multiple words, take first letter of first two words
      return (words[0][0] + words[1][0]).toUpperCase();
    } else {
      // If single word, take first two letters or just first if only one character
      return username.length >= 2
        ? username.substring(0, 2).toUpperCase()
        : username[0].toUpperCase();
    }
  };

  const navigationItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
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
                    ? 'shadow-md'
                    : 'hover:bg-gray-100'
                }`}
                style={currentSection === item.id
                  ? { background: 'var(--gradient-action)', color: 'var(--text-nav-active)' }
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
              <span className="hidden sm:inline" translate="no">
                {theme === 'dark' ? 'Claro' : 'Oscuro'}
              </span>
            </button>

            {/* Usuario */}
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white"
                   translate="no"
                   style={{ background: 'var(--gradient-nexus)' }}>
                {getUserInitials(user)}
              </div>
              <div className="hidden sm:block">
                <span className="text-sm font-medium px-2 py-1 rounded"
                      translate="no"
                      style={{
                        color: 'var(--text-primary)',
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        whiteSpace: 'nowrap'
                      }}>
                  {user || 'Usuario'}
                </span>
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
                    ? ''
                    : ''
                }`}
                style={currentSection === item.id
                  ? { background: 'var(--gradient-action)', color: 'var(--text-nav-active)' }
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
