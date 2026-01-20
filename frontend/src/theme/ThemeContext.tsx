import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export type ThemeMode = 'light' | 'dark';

// Light theme colors
const lightColors = {
  // Primary colors - Calm teal/blue (trust)
  primary: '#2C7A7B',
  primaryLight: '#4FD1C5',
  primaryDark: '#234E52',

  // Accent colors
  accent: '#38A169',
  accentWarning: '#ED8936',
  accentError: '#E53E3E',

  // Text colors
  text: '#2D3748',
  textSecondary: '#718096',
  textLight: '#A0AEC0',
  textInverse: '#FFFFFF',

  // Background colors
  background: '#FFFFFF',
  backgroundSecondary: '#F7FAFC',
  backgroundTertiary: '#EDF2F7',
  backgroundDark: '#2D3748',

  // Border colors
  border: '#E2E8F0',
  borderDark: '#CBD5E0',

  // Card/Surface
  surface: '#FFFFFF',
  surfaceHover: '#F7FAFC',

  // Shadows
  shadowColor: 'rgba(0, 0, 0, 0.1)',
  shadowColorStrong: 'rgba(0, 0, 0, 0.2)',

  // Map marker colors (consistent across themes)
  food: '#FF6B6B',
  shelter: '#4ECDC4',
  medical: '#95E1D3',
  social: '#F38181',
  hygiene: '#AA96DA',
  warming: '#FF8C00',
  cooling: '#5DADE2',
};

// Dark theme colors
const darkColors = {
  // Primary colors - Slightly brighter for dark mode
  primary: '#4FD1C5',
  primaryLight: '#81E6D9',
  primaryDark: '#2C7A7B',

  // Accent colors - Adjusted for dark backgrounds
  accent: '#48BB78',
  accentWarning: '#F6AD55',
  accentError: '#FC8181',

  // Text colors - Inverted
  text: '#F7FAFC',
  textSecondary: '#A0AEC0',
  textLight: '#718096',
  textInverse: '#1A202C',

  // Background colors - Dark
  background: '#1A202C',
  backgroundSecondary: '#2D3748',
  backgroundTertiary: '#4A5568',
  backgroundDark: '#171923',

  // Border colors - Subtle on dark
  border: '#4A5568',
  borderDark: '#2D3748',

  // Card/Surface
  surface: '#2D3748',
  surfaceHover: '#4A5568',

  // Shadows - Darker for dark mode
  shadowColor: 'rgba(0, 0, 0, 0.3)',
  shadowColorStrong: 'rgba(0, 0, 0, 0.5)',

  // Map marker colors (consistent across themes)
  food: '#FF6B6B',
  shelter: '#4ECDC4',
  medical: '#95E1D3',
  social: '#F38181',
  hygiene: '#AA96DA',
  warming: '#FF8C00',
  cooling: '#5DADE2',
};

export type ThemeColors = typeof lightColors;

interface ThemeContextType {
  mode: ThemeMode;
  colors: ThemeColors;
  isDark: boolean;
  toggleTheme: () => void;
}

const THEME_STORAGE_KEY = 'hope-theme-preference';

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get initial theme: check localStorage first, then system preference
  const getInitialTheme = (): ThemeMode => {
    if (typeof window !== 'undefined') {
      // Check localStorage for user preference
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
      // Fall back to system preference
      if (window.matchMedia) {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
    }
    return 'light';
  };

  const [mode, setMode] = useState<ThemeMode>(getInitialTheme);

  // Toggle theme and persist to localStorage
  const toggleTheme = useCallback(() => {
    setMode(prevMode => {
      const newMode = prevMode === 'dark' ? 'light' : 'dark';
      localStorage.setItem(THEME_STORAGE_KEY, newMode);
      return newMode;
    });
  }, []);

  // Listen for system theme changes (only if user hasn't set a preference)
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      // Only auto-switch if user hasn't set a manual preference
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      if (!stored) {
        setMode(e.matches ? 'dark' : 'light');
      }
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    // Older browsers (Safari < 14)
    mediaQuery.addListener(handleChange);
    return () => mediaQuery.removeListener(handleChange);
  }, []);

  // Update document styles for dark mode
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', mode);
    document.body.style.backgroundColor = mode === 'dark' ? darkColors.background : lightColors.background;
    document.body.style.color = mode === 'dark' ? darkColors.text : lightColors.text;
    // Add/remove dark-mode class for CSS targeting (e.g., Leaflet popups)
    if (mode === 'dark') {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [mode]);

  const colors = mode === 'dark' ? darkColors : lightColors;
  const isDark = mode === 'dark';

  return (
    <ThemeContext.Provider value={{ mode, colors, isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Export colors for backward compatibility
export const COLORS = lightColors;
