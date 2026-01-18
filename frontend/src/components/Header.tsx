import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { COLORS, SPACING, TYPOGRAPHY, Z_INDEX } from '../theme';
import { useLanguage } from '../i18n/LanguageContext';

const Header: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const { language, setLanguage } = useLanguage();

  const toggleMenu = () => setMenuOpen(!menuOpen);
  const closeMenu = () => setMenuOpen(false);

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'es' : 'en');
  };

  return (
    <>
      <header style={styles.header}>
        <button onClick={toggleMenu} style={styles.hamburgerButton}>
          ☰
        </button>

        <h1 style={styles.brandName}>Hope for NYC</h1>

        <button onClick={toggleLanguage} style={styles.languageButton}>
          {language.toUpperCase()}
        </button>
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

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: SPACING.md,
    backgroundColor: COLORS.primary,
    color: COLORS.textInverse,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    position: 'sticky',
    top: 0,
    zIndex: Z_INDEX.sticky,
  },
  hamburgerButton: {
    fontSize: '24px',
    color: COLORS.textInverse,
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    padding: SPACING.sm,
  },
  brandName: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    margin: 0,
  },
  languageButton: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textInverse,
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
    backgroundColor: COLORS.background,
    boxShadow: '2px 0 8px rgba(0,0,0,0.2)',
    zIndex: Z_INDEX.modal,
    display: 'flex',
    flexDirection: 'column',
  },
  menuHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: SPACING.lg,
    borderBottom: `1px solid ${COLORS.border}`,
  },
  menuTitle: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.text,
    margin: 0,
  },
  closeButton: {
    fontSize: '24px',
    color: COLORS.text,
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
    color: COLORS.text,
    textDecoration: 'none',
    padding: SPACING.md,
    borderRadius: '8px',
    marginBottom: SPACING.sm,
    transition: 'background-color 0.2s',
  },
  menuItemButton: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.text,
    backgroundColor: 'transparent',
    border: 'none',
    padding: SPACING.md,
    borderRadius: '8px',
    marginBottom: SPACING.sm,
    cursor: 'pointer',
    textAlign: 'left',
  },
};

export default Header;
