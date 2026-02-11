import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { SPACING, TYPOGRAPHY, Z_INDEX } from '../theme';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

const Header: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const { language, setLanguage } = useLanguage();
  const { colors, isDark, toggleTheme } = useTheme();

  const toggleMenu = () => setMenuOpen(!menuOpen);
  const closeMenu = () => setMenuOpen(false);

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'es' : 'en');
  };

  const styles: { [key: string]: React.CSSProperties } = {
    header: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: SPACING.md,
      backgroundColor: colors.primary,
      color: colors.textInverse,
      boxShadow: `0 2px 4px ${colors.shadowColor}`,
      position: 'sticky',
      top: 0,
      zIndex: Z_INDEX.sticky,
    },
    hamburgerButton: {
      fontSize: '24px',
      color: colors.textInverse,
      backgroundColor: 'transparent',
      border: 'none',
      cursor: 'pointer',
      padding: SPACING.sm,
    },
    brandName: {
      fontSize: TYPOGRAPHY.fontSize.xl,
      fontWeight: TYPOGRAPHY.fontWeight.bold,
      margin: 0,
      color: colors.textInverse,
      textDecoration: 'none',
      cursor: 'pointer',
    },
    rightControls: {
      display: 'flex',
      alignItems: 'center',
      gap: SPACING.sm,
    },
    themeToggle: {
      fontSize: '20px',
      color: colors.textInverse,
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '4px',
      padding: SPACING.sm,
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '36px',
      height: '36px',
    },
    languageButton: {
      fontSize: TYPOGRAPHY.fontSize.base,
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
      color: colors.textInverse,
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '4px',
      padding: `${SPACING.sm} ${SPACING.md}`,
      cursor: 'pointer',
    },
    overlay: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      zIndex: Z_INDEX.modalBackdrop,
    },
    menu: {
      position: 'fixed',
      top: 0,
      left: 0,
      bottom: 0,
      width: '280px',
      backgroundColor: colors.surface,
      boxShadow: `2px 0 8px ${colors.shadowColorStrong}`,
      zIndex: Z_INDEX.modal,
      display: 'flex',
      flexDirection: 'column',
    },
    menuHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: SPACING.lg,
      borderBottom: `1px solid ${colors.border}`,
    },
    menuTitle: {
      fontSize: TYPOGRAPHY.fontSize.xl,
      fontWeight: TYPOGRAPHY.fontWeight.bold,
      color: colors.text,
      margin: 0,
    },
    closeButton: {
      fontSize: '24px',
      color: colors.text,
      backgroundColor: 'transparent',
      border: 'none',
      cursor: 'pointer',
      padding: SPACING.sm,
    },
    menuItems: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      padding: SPACING.md,
    },
    menuItem: {
      fontSize: TYPOGRAPHY.fontSize.base,
      fontWeight: TYPOGRAPHY.fontWeight.medium,
      color: colors.text,
      textDecoration: 'none',
      padding: SPACING.md,
      borderRadius: '8px',
      marginBottom: SPACING.sm,
      transition: 'background-color 0.2s',
    },
    menuItemButton: {
      fontSize: TYPOGRAPHY.fontSize.base,
      fontWeight: TYPOGRAPHY.fontWeight.medium,
      color: colors.text,
      backgroundColor: 'transparent',
      border: 'none',
      padding: SPACING.md,
      borderRadius: '8px',
      marginBottom: SPACING.sm,
      cursor: 'pointer',
      textAlign: 'left',
    },
  };

  return (
    <>
      <header style={styles.header}>
        <button onClick={toggleMenu} style={styles.hamburgerButton}>
          ☰
        </button>

        <Link to="/" style={styles.brandName}>
          Hope for NYC
        </Link>

        <div style={styles.rightControls}>
          <button
            onClick={toggleTheme}
            style={styles.themeToggle}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
          <button onClick={toggleLanguage} style={styles.languageButton}>
            {language.toUpperCase()}
          </button>
        </div>
      </header>

      {/* Hamburger Menu Overlay */}
      {menuOpen && (
        <>
          <div style={styles.overlay} onClick={closeMenu} />
          <nav style={styles.menu}>
            <div style={styles.menuHeader}>
              <h2 style={styles.menuTitle}>Menu</h2>
              <button onClick={closeMenu} style={styles.closeButton}>
                ✕
              </button>
            </div>

            <div style={styles.menuItems}>
              <Link to="/about" style={styles.menuItem} onClick={closeMenu}>
                About
              </Link>
              <Link to="/how-it-works" style={styles.menuItem} onClick={closeMenu}>
                How This Works
              </Link>
              <button onClick={() => { toggleTheme(); }} style={styles.menuItemButton}>
                Theme: {isDark ? 'Dark' : 'Light'}
              </button>
              <button onClick={() => { toggleLanguage(); closeMenu(); }} style={styles.menuItemButton}>
                Language: {language.toUpperCase()}
              </button>
            </div>
          </nav>
        </>
      )}
    </>
  );
};

export default Header;
