import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ConversionHistory from './components/ConversionHistory';
import ConversionPanel from './components/ConversionPanel';
import FileUploader from './components/FileUploader';
import CircularProgress from './components/CircularProgress';
import AIChatBox from './components/AIChatBox';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import ProtectedRoute from './ProtectedRoute';

import { useTranslation } from 'react-i18next';

const getInitialTheme = (): 'light' | 'dark' => {
  const stored = localStorage.getItem('theme') as 'light' | 'dark' | null;
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const MainApp: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme);
  const [currentSection, setCurrentSection] = useState<string>('inicio');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [conversionState, setConversionState] = useState({
    isConverting: false,
    progress: 0,
    statusMessage: ''
  });
  const [pipelineData, setPipelineData] = useState({
    pipelines: [],
    selectedPipeline: '',
    userCredits: 0,
    analysisData: null
  });
  const { t } = useTranslation();


  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => setTheme(e.matches ? 'dark' : 'light');
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  // Función para manejar el reinicio/nueva conversión
  const handleNewConversion = () => {
    setSelectedFile(null); // Resetear archivo seleccionado
    setConversionState({    // Resetear estado de conversión
      isConverting: false,
      progress: 0,
      statusMessage: ''
    });
    setPipelineData({       // Resetear datos de pipeline
      pipelines: [],
      selectedPipeline: '',
      userCredits: 0,
      analysisData: null
    });
    setCurrentSection('inicio'); // Ir a la sección inicio
  };

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }} data-theme={theme}>
      <Header theme={theme} toggleTheme={toggleTheme} currentSection={currentSection} setCurrentSection={setCurrentSection} onNewConversion={handleNewConversion} />

      <main className="min-h-[calc(100vh-4rem)]">
        {currentSection === 'inicio' && (
          <div className="animate-fade-in">
            {/* Hero Section */}
            <section className="relative overflow-hidden py-16" style={{ background: 'var(--gradient-hero)' }}>
              <div className="w-full text-center text-white">
                <div className="mb-8">
                  <h1 className="text-5xl md:text-6xl font-bold mb-6 gradient-text-hero" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t('home.hero.title')}
                  </h1>
                  <p className="text-xl md:text-2xl mb-8 opacity-90">
                    {t('home.hero.subtitle')}
                  </p>
                </div>

                {/* Layout de borde a borde cuando hay archivo seleccionado */}
                {selectedFile ? (
                  <div className="w-full">
                    <div className="grid grid-cols-12 items-start max-w-6xl mx-auto px-8">
                      {/* Columna izquierda - Cards (3 columnas) */}
                      <div className="col-span-3 pr-6 py-6" style={{ marginTop: '-50px' }}>
                        <ConversionPanel
                          file={selectedFile}
                          onConversionStateChange={setConversionState}
                          onPipelineDataChange={setPipelineData}
                        />
                      </div>

                      {/* Columna central - File Uploader (6 columnas) */}
                      <div className="col-span-6 flex flex-col items-center px-6">
                        <FileUploader
                          onFileSelected={setSelectedFile}
                          selectedFile={selectedFile}
                        />

                        {/* Barra de progreso circular centrada debajo del área de importación */}
                        {conversionState.isConverting && (
                          <div className="flex flex-col items-center mt-6">
                            <CircularProgress
                              progress={conversionState.progress}
                              size={120}
                              strokeWidth={10}
                              showPercentage={true}
                              className="mb-4"
                            />
                            <p className="text-sm text-center max-w-xs" style={{color: '#23436B'}}>
                              {conversionState.statusMessage || t("conversionPanel.progress", { progress: conversionState.progress })}
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Columna derecha - AI ChatBox (3 columnas) */}
                      <div className="col-span-3 flex items-start justify-center pl-6 py-6" style={{ marginTop: '-50px' }}>
                        <AIChatBox
                          userCredits={pipelineData.userCredits}
                          selectedPipeline={pipelineData.selectedPipeline}
                          pipelines={pipelineData.pipelines}
                          analysisData={pipelineData.analysisData}
                          onSequenceRecommended={(sequence) => {
                            // Handle sequence recommendation
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  /* File Uploader centrado cuando no hay archivo */
                  <div className="max-w-2xl mx-auto">
                    <FileUploader
                      onFileSelected={setSelectedFile}
                      selectedFile={selectedFile}
                    />
                  </div>
                )}
              </div>

              {/* Decorative elements */}
              <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full opacity-10"
                     style={{ background: 'var(--anclora-amber)' }}></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full opacity-10"
                     style={{ background: 'var(--anclora-blue-sky)' }}></div>
              </div>
            </section>

            {/* Features Section */}
            <section className="py-16 px-4" style={{ background: 'var(--bg-secondary)' }}>
              <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12">
                  <h2 className="text-3xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                    {t('home.features.title')}
                  </h2>
                  <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
                    {t('home.features.subtitle')}
                  </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                  <div className="card text-center animate-slide-in">
                    <div className="w-16 h-16 rounded-xl mx-auto mb-4 flex items-center justify-center text-2xl"
                         style={{ background: 'var(--gradient-nexus)' }}>
                      <span className="text-white">🤖</span>
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{t('home.features.ai.title')}</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                      {t('home.features.ai.description')}
                    </p>
                  </div>

                  <div className="card text-center animate-slide-in" style={{ animationDelay: '0.1s' }}>
                    <div className="w-16 h-16 rounded-xl mx-auto mb-4 flex items-center justify-center text-2xl"
                         style={{ background: 'var(--gradient-action)' }}>
                      <span style={{ color: 'var(--anclora-dark)' }}>⚡</span>
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{t('home.features.speed.title')}</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                      {t('home.features.speed.description')}
                    </p>
                  </div>

                  <div className="card text-center animate-slide-in" style={{ animationDelay: '0.2s' }}>
                    <div className="w-16 h-16 rounded-xl mx-auto mb-4 flex items-center justify-center text-2xl"
                         style={{ background: 'var(--gradient-press)' }}>
                      <span style={{ color: 'var(--anclora-dark)', fontWeight: 'bold' }}>💎</span>
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{t('home.features.quality.title')}</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                      {t('home.features.quality.description')}
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}



        {currentSection === 'history' && (
          <div className="max-w-6xl mx-auto p-6 space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4 gradient-text">{t('history.title')}</h2>
              <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
                {t('history.subtitle')}
              </p>
            </div>
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
