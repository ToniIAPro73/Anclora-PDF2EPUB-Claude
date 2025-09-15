import React from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  currentSection: string;
  setCurrentSection: (section: string) => void;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme, currentSection, setCurrentSection }) => {
  const { logout, user } = useAuth();
  const { t } = useTranslation();

  // User object is available for debugging if needed



  const handleLogout = () => {
    logout();
  };

  // Helper function to get user initials
  const getUserInitials = (user: any): string => {
    // Handle null/undefined user
    if (!user) return 'U';

    // Handle non-object user (shouldn't happen but defensive)
    if (typeof user !== 'object') return 'U';

    try {
      let displayName = 'U';

      // Priority: username from metadata > email prefix > 'U'
      if (user.user_metadata && typeof user.user_metadata === 'object') {
        if (user.user_metadata.username && typeof user.user_metadata.username === 'string') {
          displayName = user.user_metadata.username.trim();
        }
      }

      // Fallback to email if no username
      if (displayName === 'U' && user.email && typeof user.email === 'string') {
        displayName = user.email.split('@')[0].trim();
      }

      // Ensure we have a valid string
      if (!displayName || displayName === 'U') return 'U';

      // Get initials
      const words = displayName.split(/\s+/).filter(word => word.length > 0);
      if (words.length >= 2) {
        return (words[0][0] + words[1][0]).toUpperCase();
      } else if (words.length === 1 && words[0].length >= 2) {
        return words[0].substring(0, 2).toUpperCase();
      } else if (words.length === 1 && words[0].length === 1) {
        return words[0][0].toUpperCase();
      }

      return 'U';
    } catch (error) {
      console.error('Error in getUserInitials:', error);
      return 'U';
    }
  };

  const navigationItems = [
    { id: 'inicio', label: t('navigation.home'), icon: '🏠' },
    { id: 'history', label: t('navigation.history'), icon: '📋' },
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
              <h1 className="text-xl font-bold" style={{ lineHeight: '1.5', margin: '0', padding: '0', color: 'var(--text-header)' }}>{t('app.title')}</h1>
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
            {/* Selector de Idioma */}
            <LanguageSelector />

            {/* Toggle de Tema */}
            <button
              onClick={toggleTheme}
              aria-label={t('theme.toggle')}
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
                {theme === 'dark' ? t('theme.light') : t('theme.dark')}
              </span>
            </button>

            {/* Usuario */}
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white"
                   style={{ background: 'var(--gradient-nexus)' }}>
                {getUserInitials(user)}
              </div>
              <div className="hidden sm:block">
                <span className="text-sm font-medium px-2 py-1 rounded"
                      style={{
                        color: 'var(--text-primary)',
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        whiteSpace: 'nowrap'
                      }}>
                  {(() => {
                    if (!user) return t('auth.login');
                    if (user.user_metadata?.username) return user.user_metadata.username;
                    if (user.email) return user.email.split('@')[0];
                    return t('auth.login');
                  })()}
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
              <span className="hidden sm:inline">{t('navigation.logout')}</span>
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
