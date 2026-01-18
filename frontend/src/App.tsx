import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
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

function App() {
  return (
    <LanguageProvider>
      <Router>
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
      </Router>
    </LanguageProvider>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  appContainer: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    overflow: 'hidden',
  },
  mainContent: {
    flex: 1,
    overflow: 'auto',
    paddingBottom: '70px', // Space for bottom nav
  },
};

export default App;
