import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import { ThemeProvider, useTheme } from './theme/ThemeContext';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import MapScreen from './screens/MapScreen';
import AboutScreen from './screens/AboutScreen';
import HowItWorksScreen from './screens/HowItWorksScreen';
import PrivacyPolicyScreen from './screens/PrivacyPolicyScreen';
import TermsOfUseScreen from './screens/TermsOfUseScreen';
import ReportIssueScreen from './screens/ReportIssueScreen';
import ProviderPortalScreen from './screens/ProviderPortalScreen';
import 'leaflet/dist/leaflet.css';
import './App.css';

const AppContent: React.FC = () => {
  const { colors } = useTheme();

  const styles: { [key: string]: React.CSSProperties } = {
    appContainer: {
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      overflow: 'hidden',
      backgroundColor: colors.background,
      color: colors.text,
    },
    mainContent: {
      flex: 1,
      overflow: 'auto',
      paddingBottom: '70px',
      backgroundColor: colors.background,
    },
  };

  return (
    <div className="App" style={styles.appContainer}>
      <Header />
      <main style={styles.mainContent}>
        <Routes>
          <Route path="/" element={<MapScreen />} />
          <Route path="/about" element={<AboutScreen />} />
          <Route path="/how-it-works" element={<HowItWorksScreen />} />
          <Route path="/privacy" element={<PrivacyPolicyScreen />} />
          <Route path="/terms" element={<TermsOfUseScreen />} />
          <Route path="/report" element={<ReportIssueScreen />} />
          <Route path="/providers" element={<ProviderPortalScreen />} />
        </Routes>
      </main>
      <BottomNav />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <Router>
          <AppContent />
        </Router>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
