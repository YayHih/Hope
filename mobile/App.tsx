/**
 * Hope Platform - Mobile App Entry Point
 * Privacy-first homeless services finder for NYC
 */

import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AppNavigator } from './src/navigation/AppNavigator';
import { ErrorBoundary } from './src/components/ErrorBoundary';
import { NetworkProvider } from './src/contexts/NetworkContext';
import { LanguageProvider } from './src/i18n';

export default function App() {
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <SafeAreaProvider>
          <NetworkProvider>
            <AppNavigator />
            <StatusBar style="light" />
          </NetworkProvider>
        </SafeAreaProvider>
      </LanguageProvider>
    </ErrorBoundary>
  );
}
