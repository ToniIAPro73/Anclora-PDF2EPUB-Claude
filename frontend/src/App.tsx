import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ConversionPanel from './components/ConversionPanel';
import ConversionHistory from './components/ConversionHistory';

const App: React.FC = () => {

  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [currentSection, setCurrentSection] = useState<string>('inicio');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Detectar preferencia de tema del sistema
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (

    <div className={`app-container ${theme}`} data-theme={theme}>
      <Header theme={theme} toggleTheme={toggleTheme} currentSection={currentSection} />
      
      <main className="main-content">
        {currentSection === 'inicio' && (
          <div className="hero-section">
            <h1>Anclora PDF2EPUB</h1>
            <p>Conversión inteligente de PDF a EPUB3</p>
            <FileUploader onFileSelected={setSelectedFile} />
          </div>
        )}
        
        {currentSection === 'conversion' && (
          <div className="conversion-section">
            <h2>Convertir PDF a EPUB</h2>
            <FileUploader onFileSelected={setSelectedFile} />
            <ConversionPanel file={selectedFile} />
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
