import React from 'react';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  currentSection: string;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme }) => {
  return (
    <header>
      <button onClick={toggleTheme}>
        {theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro'}
      </button>
    </header>
  );
};

export default Header;
