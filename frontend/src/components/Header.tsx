import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import Container from './Container';
import CreditBalance from './CreditBalance';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  currentSection: string;
  setCurrentSection: (section: string) => void;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme, currentSection, setCurrentSection }) => {
  const { logout, user } = useAuth();
  const { t } = useTranslation();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [currentCredits, setCurrentCredits] = useState(0);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
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
      <Container>
        <div className="flex items-center justify-between h-16">
          {/* Logo y Marca */}
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg p-1"
                 style={{ background: 'var(--gradient-hero)' }}>
              <img
                src="/images/iconos/anclora-logo.png"
                alt={t('app.title')}
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
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 ${
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
          <div className="flex items-center gap-4">
            {/* Balance de Créditos y Usuario */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 p-2 rounded-lg transition-all duration-200 hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
                style={{ color: 'var(--text-primary)' }}
              >
                {/* Balance de Créditos */}
                <CreditBalance onCreditsUpdate={setCurrentCredits} />

                {/* Avatar del Usuario */}
                <div className="flex items-center justify-center w-9 h-9 rounded-full text-sm font-bold text-white"
                     style={{ background: 'var(--gradient-nexus)' }}>
                  {getUserInitials(user)}
                </div>

                {/* Icono de dropdown */}
                <svg
                  className={`w-4 h-4 transition-transform duration-200 ${showUserMenu ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Menú Dropdown */}
              {showUserMenu && (
                <>
                  {/* Overlay para cerrar el menú */}
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />

                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border z-20"
                       style={{
                         backgroundColor: 'var(--bg-card)',
                         borderColor: 'var(--border-color)',
                         boxShadow: 'var(--shadow-lg)'
                       }}>

                    {/* Header del menú con info del usuario */}
                    <div className="p-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-12 h-12 rounded-full text-lg font-bold text-white"
                             style={{ background: 'var(--gradient-nexus)' }}>
                          {getUserInitials(user)}
                        </div>
                        <div>
                          <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                            {(() => {
                              if (!user) return t('auth.login');
                              if (user.user_metadata?.username) return user.user_metadata.username;
                              if (user.email) return user.email.split('@')[0];
                              return t('auth.login');
                            })()}
                          </p>
                          {user?.email && (
                            <p className="text-xs text-gray-500">{user.email}</p>
                          )}
                        </div>
                      </div>

                      {/* Balance de créditos detallado */}
                      <div className="mt-3">
                        <CreditBalance showDetails={true} />
                      </div>
                    </div>

                    {/* Opciones del menú */}
                    <div className="py-2">
                      {/* Invitar amigos */}
                      <button
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                        style={{ color: 'var(--text-primary)' }}
                        onClick={() => {
                          setShowUserMenu(false);
                          // TODO: Abrir modal de invitaciones
                        }}
                      >
                        <span>👥</span>
                        <span>{t('menu.inviteFriends')}</span>
                      </button>

                      {/* Suscripción */}
                      <button
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-gray-50 transition-colors opacity-50 cursor-not-allowed"
                        style={{ color: 'var(--text-primary)' }}
                        disabled
                      >
                        <span>💎</span>
                        <span>{t('menu.subscription')}</span>
                        <span className="ml-auto text-xs bg-gray-200 px-2 py-1 rounded-full">
                          {t('menu.comingSoon')}
                        </span>
                      </button>

                      <div className="border-t my-2" style={{ borderColor: 'var(--border-color)' }} />

                      {/* Selector de idioma */}
                      <div className="px-4 py-2">
                        <div className="flex items-center gap-3 mb-2">
                          <span>🌍</span>
                          <span className="text-sm" style={{ color: 'var(--text-primary)' }}>
                            {t('menu.language')}
                          </span>
                        </div>
                        <div className="ml-6">
                          <LanguageSelector />
                        </div>
                      </div>

                      {/* Toggle de tema */}
                      <button
                        onClick={() => {
                          toggleTheme();
                          setShowUserMenu(false);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        <span>{theme === 'dark' ? '☀️' : '🌙'}</span>
                        <span>
                          {theme === 'dark' ? t('theme.light') : t('theme.dark')}
                        </span>
                      </button>

                      <div className="border-t my-2" style={{ borderColor: 'var(--border-color)' }} />

                      {/* Cerrar sesión */}
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-red-50 hover:text-red-600 transition-colors"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        <span>🚪</span>
                        <span>{t('navigation.logout')}</span>
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Navegación Móvil */}
        <div className="md:hidden border-t" style={{ borderColor: 'var(--border-color)' }}>
          <nav className="flex justify-around py-2">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentSection(item.id)}
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 ${
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
      </Container>
    </header>
  );
};

export default Header;
