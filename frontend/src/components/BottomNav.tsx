import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { COLORS, SPACING, TYPOGRAPHY, Z_INDEX } from '../theme';
import { useLanguage } from '../i18n/LanguageContext';

const BottomNav: React.FC = () => {
  const location = useLocation();
  const { t } = useLanguage();

  const navItems = [
    { path: '/', labelKey: 'map' as const, icon: '🗺️' },
    { path: '/privacy', labelKey: 'privacy' as const, icon: '🔒' },
    { path: '/terms', labelKey: 'terms' as const, icon: '📄' },
    { path: '/report', labelKey: 'report' as const, icon: '📝' },
    { path: '/providers', labelKey: 'providers' as const, icon: '🏛️' },
  ];

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

const styles: { [key: string]: React.CSSProperties } = {
  bottomNav: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    borderTop: `1px solid ${COLORS.border}`,
    boxShadow: '0 -2px 8px rgba(0,0,0,0.1)',
    zIndex: Z_INDEX.sticky,
    padding: `${SPACING.sm} 0`,
  },
  navItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textDecoration: 'none',
    color: COLORS.textSecondary,
    padding: `${SPACING.xs} ${SPACING.sm}`,
    minWidth: '60px',
    transition: 'color 0.2s',
  },
  navItemActive: {
    color: COLORS.primary,
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

export default BottomNav;
