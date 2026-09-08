import React, { createContext, useContext, useState, useCallback } from 'react';
import en from './translations/en.json';
import te from './translations/te.json';
import hi from './translations/hi.json';
import ta from './translations/ta.json';
import ka from './translations/ka.json';

const translations = { en, te, hi, ta, ka };

export const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'ka', name: 'Kannada', native: 'ಕನ್ನಡ' },
];

const I18nContext = createContext();

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem('aide-language') || 'en';
  });

  const setLanguage = useCallback((code) => {
    setLanguageState(code);
    localStorage.setItem('aide-language', code);
  }, []);

  // t('NAV.nav_home') -> translations[lang].NAV.nav_home
  const t = useCallback((key) => {
    if (!key) return '';
    const parts = key.split('.');
    let result = translations[language];
    // Fallback to English if key missing in current lang
    let fallback = translations.en;
    
    for (const part of parts) {
      if (result && typeof result === 'object') result = result[part];
      else result = undefined;
      if (fallback && typeof fallback === 'object') fallback = fallback[part];
      else fallback = undefined;
    }
    
    return result || fallback || key;
  }, [language]);

  return (
    <I18nContext.Provider value={{ t, language, setLanguage, languages: LANGUAGES }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within LanguageProvider');
  return ctx;
}

export default translations;
