import React from 'react';

interface HeaderProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  currentSection: string;
}

const Header: React.FC<HeaderProps> = ({ theme, toggleTheme }) => {
  return (
    <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
      <h1 className="text-xl sm:text-2xl font-semibold">Anclora PDF2EPUB</h1>
      <button
        onClick={toggleTheme}
        aria-label="Cambiar tema"
        className="self-start sm:self-auto rounded-md px-3 py-2 bg-gray-200 text-gray-900 dark:bg-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-gray-900"
      >
        {theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro'}
      </button>
    </header>
  );
};

export default Header;
