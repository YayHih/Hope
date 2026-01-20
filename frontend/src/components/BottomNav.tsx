import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { SPACING, TYPOGRAPHY, Z_INDEX } from '../theme';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

const BottomNav: React.FC = () => {
  const location = useLocation();
  const { t } = useLanguage();
  const { colors } = useTheme();

  const navItems = [
    { path: '/', labelKey: 'map' as const, icon: '🗺️' },
    { path: '/privacy', labelKey: 'privacy' as const, icon: '🔒' },
    { path: '/terms', labelKey: 'terms' as const, icon: '📄' },
    { path: '/report', labelKey: 'report' as const, icon: '📝' },
    { path: '/providers', labelKey: 'providers' as const, icon: '🏛️' },
  ];

  const styles: { [key: string]: React.CSSProperties } = {
    bottomNav: {
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      display: 'flex',
      justifyContent: 'space-around',
      alignItems: 'center',
      backgroundColor: colors.surface,
      borderTop: `1px solid ${colors.border}`,
      boxShadow: `0 -2px 8px ${colors.shadowColor}`,
      zIndex: Z_INDEX.sticky,
      padding: `${SPACING.sm} 0`,
    },
    navItem: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      textDecoration: 'none',
      color: colors.textSecondary,
      padding: `${SPACING.xs} ${SPACING.sm}`,
      minWidth: '60px',
      transition: 'color 0.2s',
    },
    navItemActive: {
      color: colors.primary,
    },
    navIcon: {
      fontSize: '24px',
      marginBottom: '2px',
    },
    navLabel: {
      fontSize: TYPOGRAPHY.fontSize.xs,
      fontWeight: TYPOGRAPHY.fontWeight.medium,
    },
    navLabelActive: {
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
    },
  };

  return (
    <nav style={styles.bottomNav}>
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;

        return (
          <NavLink
            key={item.path}
            to={item.path}
            style={{
              ...styles.navItem,
              ...(isActive ? styles.navItemActive : {}),
            }}
          >
            <span style={styles.navIcon}>{item.icon}</span>
            <span style={{
              ...styles.navLabel,
              ...(isActive ? styles.navLabelActive : {}),
            }}>
              {t(item.labelKey)}
            </span>
          </NavLink>
        );
      })}
    </nav>
  );
};

export default BottomNav;
