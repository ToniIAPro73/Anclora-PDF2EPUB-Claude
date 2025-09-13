import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ConversionPanel from './components/ConversionPanel';
import ConversionHistory from './components/ConversionHistory';

const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(
    localStorage.getItem('theme') === 'dark' ? 'dark' : 'light'
  );

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      <Header theme={theme} toggleTheme={toggleTheme} />
      <main className="p-4">
        <Routes>
          <Route path="/" element={<ConversionPanel />} />
          <Route path="/history" element={<ConversionHistory />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
