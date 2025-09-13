import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import FileUploader from './components/FileUploader';
import ConversionPanel from './components/ConversionPanel';
import MetricsDisplay from './components/MetricsDisplay';
import ConversionHistory from './components/ConversionHistory';
import './styles/App.css';

const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [currentSection, setCurrentSection] = useState<string>('inicio');
  
  // Detectar preferencia de tema del sistema
  useEffect(() => {
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDarkMode ? 'dark' : 'light');
    
    // Listener para cambios del sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      setTheme(e.matches ? 'dark' : 'light');
    });
  }, []);
  
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };
  
  return (
    <div className={`app-container ${theme}`} data-theme={theme}>
      <Header theme={theme} toggleTheme={toggleTheme} currentSection={currentSection} />
      
      <main className="main-content">
        {currentSection === 'inicio' && (
          <div className="hero-section">
            <h1>Anclora PDF2EPUB</h1>
            <p>Conversión inteligente de PDF a EPUB3</p>
            <FileUploader />
          </div>
        )}
        
        {currentSection === 'conversion' && (
          <div className="conversion-section">
            <h2>Convertir PDF a EPUB</h2>
            <FileUploader />
            <ConversionPanel />
            <MetricsDisplay />
          </div>
        )}
        
        {currentSection === 'history' && (
          <div className="history-section">
            <h2>Historial de Conversiones</h2>
            <ConversionHistory />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;