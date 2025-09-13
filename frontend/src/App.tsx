import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ConversionPanel from './components/ConversionPanel';
import ConversionHistory from './components/ConversionHistory';
import FileUploader from './components/FileUploader';
import MetricsDisplay from './components/MetricsDisplay';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import ProtectedRoute from './ProtectedRoute';

const getInitialTheme = (): 'light' | 'dark' => {
  const stored = localStorage.getItem('theme') as 'light' | 'dark' | null;
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const MainApp: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme);
  const [currentSection, setCurrentSection] = useState<string>('inicio');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => setTheme(e.matches ? 'dark' : 'light');
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 dark:bg-gray-900 dark:text-gray-100" data-theme={theme}>
      <Header theme={theme} toggleTheme={toggleTheme} currentSection={currentSection} />

      <main className="container mx-auto p-4 sm:p-6 space-y-8">
        {currentSection === 'inicio' && (
          <div className="flex flex-col items-center text-center gap-4">
            <h1 className="text-2xl sm:text-3xl font-bold">Anclora PDF2EPUB</h1>
            <p className="text-lg">Conversión inteligente de PDF a EPUB3</p>
            <FileUploader onFileSelected={setSelectedFile} />
          </div>
        )}

        {currentSection === 'conversion' && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Convertir PDF a EPUB</h2>
            <FileUploader onFileSelected={setSelectedFile} />
            <ConversionPanel file={selectedFile} />
            <MetricsDisplay />
          </div>
        )}

        {currentSection === 'history' && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Historial de Conversiones</h2>
            <ConversionHistory />
          </div>
        )}
      </main>
    </div>
  );
};

const App: React.FC = () => (
  <Routes>
    <Route path="/login" element={<LoginForm />} />
    <Route path="/register" element={<RegisterForm />} />
    <Route
      path="/*"
      element={
        <ProtectedRoute>
          <MainApp />
        </ProtectedRoute>
      }
    />
  </Routes>
);

export default App;
