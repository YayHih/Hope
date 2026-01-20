/**
 * Language Context - Manages app-wide language state
 * Provides translations throughout the app
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { translations, Language, Translations } from './translations';

const LANGUAGE_STORAGE_KEY = 'hope_app_language';

interface LanguageContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextValue>({
  language: 'EN',
  setLanguage: () => {},
  t: translations.EN,
});

export const useLanguage = () => useContext(LanguageContext);

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<Language>('EN');
  const [isLoaded, setIsLoaded] = useState(false);

  // Load saved language on mount
  useEffect(() => {
    loadSavedLanguage();
  }, []);

  const loadSavedLanguage = async () => {
    try {
      const savedLanguage = await AsyncStorage.getItem(LANGUAGE_STORAGE_KEY);
      if (savedLanguage && (savedLanguage === 'EN' || savedLanguage === 'ES' || savedLanguage === 'ZH')) {
        setLanguageState(savedLanguage as Language);
      }
    } catch (error) {
      console.error('[LanguageContext] Failed to load saved language:', error);
    } finally {
      setIsLoaded(true);
    }
  };

  const setLanguage = async (lang: Language) => {
    try {
      await AsyncStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
      setLanguageState(lang);
    } catch (error) {
      console.error('[LanguageContext] Failed to save language:', error);
      // Still update state even if storage fails
      setLanguageState(lang);
    }
  };

  const value: LanguageContextValue = {
    language,
    setLanguage,
    t: translations[language],
  };

  // Don't render until language is loaded to prevent flash
  if (!isLoaded) {
    return null;
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}
