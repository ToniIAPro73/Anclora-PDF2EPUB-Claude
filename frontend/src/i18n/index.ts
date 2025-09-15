import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Importar las traducciones
import es from './locales/es.json';
import en from './locales/en.json';

const resources = {
  es: {
    translation: es
  },
  en: {
    translation: en
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'es', // Español como idioma por defecto
    // Removido lng: 'es' para permitir detección automática
    debug: true, // Habilitado para debugging

    interpolation: {
      escapeValue: false, // React ya escapa por defecto
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    }
  });

// Debug logging
i18n.on('languageChanged', (lng) => {
  console.log('i18n: Language changed to:', lng);
});

console.log('i18n: Initialized with language:', i18n.language);

export default i18n;
