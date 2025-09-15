import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../AuthContext';

const LanguageSelector: React.FC = () => {
  const { language, setLanguage } = useAuth();
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const languages = [
    { code: 'es', label: t('language.spanish'), flag: '🇪🇸' },
    { code: 'en', label: t('language.english'), flag: '🇬🇧' }
  ];

  const currentLanguage = languages.find(lang => lang.code === language) || languages[0];

  const changeLanguage = (languageCode: string) => {
    setLanguage(languageCode);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1 px-2 py-1 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 transition-colors duration-200"
        title={t('language.selectLanguage')}
      >
        <span className="text-base">{currentLanguage.flag}</span>
        <span>{currentLanguage.label}</span>
        <svg
          className={`w-3 h-3 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Overlay para cerrar el dropdown */}
          <div
            className="fixed inset-0 z-10"
            role="button"
            tabIndex={0}
            aria-label="Close language menu"
            onClick={() => setIsOpen(false)}
            onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && setIsOpen(false)}
          />

          {/* Dropdown menu */}
          <div className="absolute right-0 mt-1 w-20 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 z-20">
            <div className="py-1">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => changeLanguage(lang.code)}
                  className={`w-full px-3 py-1 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 ${
                    language === lang.code
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSelector;
