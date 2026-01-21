import React from 'react';
import { SPACING, TYPOGRAPHY } from '../../theme';

interface DHSInfoCardProps {
  t: (key: any) => string;
  colors: any;
  isDark: boolean;
  onClose: () => void;
  onCall311: () => void;
}

export const DHSInfoCard: React.FC<DHSInfoCardProps> = ({ t, colors, isDark, onClose, onCall311 }) => {
  const styles = getStyles(colors, isDark);

  return (
    <div style={styles.dhsContainer}>
      <div style={styles.dhsCard}>
        <div style={styles.dhsIcon}>🏛️</div>
        <h2 style={styles.dhsTitle}>Safe Options & Intake</h2>
        <h3 style={styles.dhsSubtitle}>{t('officialDHSEntryPoints')}</h3>

        {/* Warning Block */}
        <div style={styles.dhsWarningBlock}>
          <p style={styles.dhsWarningText}>
            ℹ️ {t('dhsWarning')}
          </p>
        </div>

        {/* Action Buttons Row */}
        <div style={styles.dhsActionRow}>
          <button onClick={onCall311} style={styles.dhsActionButton}>
            📞 {t('call311')}<br />
            <span style={styles.dhsActionSubtext}>{t('cityServices')}</span>
          </button>
          <a
            href="tel:988"
            style={styles.dhsActionButton}
            onClick={(e) => {
              e.preventDefault();
              window.location.href = 'tel:988';
            }}
          >
            🧠 {t('call988')}<br />
            <span style={styles.dhsActionSubtext}>{t('mentalHealth')}</span>
          </a>
        </div>

        {/* Intake Centers Section */}
        <div style={styles.dhsSection}>
          <h4 style={styles.dhsSectionTitle}>🛑 {t('intakeCentersTitle')}</h4>
          <p style={styles.dhsSectionSubtext}>{t('intakeCentersSubtext')}</p>

          <div style={styles.dhsLocationList}>
            <div style={styles.dhsLocationItem}>
              <strong>{t('familiesWithKids')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=151+East+151st+St+Bronx+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                151 East 151st St, Bronx (PATH)
              </a>
            </div>

            <div style={styles.dhsLocationItem}>
              <strong>{t('singleMen')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=400+East+30th+St+Manhattan+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                400-430 East 30th St, Manhattan
              </a>
            </div>

            <div style={styles.dhsLocationItem}>
              <strong>{t('singleWomen')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=116+Williams+Ave+Brooklyn+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                116 Williams Ave, Brooklyn (HELP Center)
              </a>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=1122+Franklin+Ave+Bronx+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                1122 Franklin Ave, Bronx (Franklin Shelter)
              </a>
            </div>

            <div style={styles.dhsLocationItem}>
              <strong>{t('adultFamilies')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=400+East+30th+St+Manhattan+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                400-430 East 30th St, Manhattan (AFIC)
              </a>
            </div>
          </div>
        </div>

        {/* Drop-In Centers Section */}
        <div style={styles.dhsSection}>
          <h4 style={styles.dhsSectionTitle}>🛋️ {t('dropInCentersTitle')}</h4>
          <p style={styles.dhsSectionSubtext}>{t('dropInCentersSubtext')}</p>

          <div style={styles.dhsLocationList}>
            <div style={styles.dhsLocationItem}>
              <strong>{t('manhattan')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=120+E+32nd+St+Manhattan+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                Mainchance (120 E 32nd St)
              </a>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=257+W+30th+St+Manhattan+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                Olivieri Center (257 W 30th St)
              </a>
            </div>

            <div style={styles.dhsLocationItem}>
              <strong>{t('bronx')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=800+Barretto+St+Bronx+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                The Living Room (800 Barretto St)
              </a>
            </div>

            <div style={styles.dhsLocationItem}>
              <strong>{t('brooklyn')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=2402+Atlantic+Ave+Brooklyn+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                The Gathering Place (2402 Atlantic Ave)
              </a>
            </div>

            <div style={styles.dhsLocationItem}>
              <strong>{t('statenIsland')}</strong>
              <a
                href="https://www.google.com/maps/dir/?api=1&destination=25+Central+Ave+Staten+Island+NY&travelmode=transit"
                target="_blank"
                rel="noopener noreferrer"
                style={styles.dhsAddressLink}
              >
                Project Hospitality (25 Central Ave)
              </a>
            </div>
          </div>
        </div>

        <button onClick={onClose} style={styles.dhsBackButton}>
          ← Back to Map
        </button>
      </div>
    </div>
  );
};

const getStyles = (colors: any, isDark: boolean): { [key: string]: React.CSSProperties } => ({
  dhsContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: SPACING.xl,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    backdropFilter: 'blur(4px)',
    zIndex: 2000,
  },
  dhsCard: {
    maxWidth: '700px',
    maxHeight: '75vh',
    overflowY: 'auto',
    padding: SPACING.xl,
    backgroundColor: colors.background,
    borderRadius: '16px',
    boxShadow: isDark ? '0 12px 40px rgba(0,0,0,0.5)' : '0 12px 40px rgba(0,0,0,0.2)',
    textAlign: 'left',
  },
  dhsIcon: {
    fontSize: '48px',
    marginBottom: SPACING.sm,
    textAlign: 'center' as const,
  },
  dhsTitle: {
    fontSize: TYPOGRAPHY.fontSize['2xl'],
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: colors.primary,
    marginBottom: SPACING.xs,
    textAlign: 'center' as const,
  },
  dhsSubtitle: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: colors.textSecondary,
    marginBottom: SPACING.lg,
    textAlign: 'center' as const,
  },
  dhsWarningBlock: {
    backgroundColor: isDark ? '#78350F' : '#FFF4E6',
    border: `2px solid ${isDark ? '#F59E0B' : '#FFB84D'}`,
    borderRadius: '8px',
    padding: SPACING.md,
    marginBottom: SPACING.lg,
  },
  dhsWarningText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    lineHeight: TYPOGRAPHY.lineHeight.relaxed,
    color: isDark ? '#FEF3C7' : '#744210',
    margin: 0,
  },
  dhsActionRow: {
    display: 'flex',
    gap: SPACING.sm,
    marginBottom: SPACING.xl,
  },
  dhsActionButton: {
    flex: 1,
    padding: SPACING.md,
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: colors.textInverse,
    backgroundColor: colors.accent,
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    textAlign: 'center' as const,
    textDecoration: 'none',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dhsActionSubtext: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    fontWeight: TYPOGRAPHY.fontWeight.normal,
    marginTop: '4px',
    opacity: 0.9,
  },
  dhsSection: {
    marginBottom: SPACING.xl,
    paddingBottom: SPACING.lg,
    borderBottom: `1px solid ${colors.border}`,
  },
  dhsSectionTitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: colors.text,
    marginBottom: SPACING.xs,
    marginTop: 0,
  },
  dhsSectionSubtext: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: SPACING.md,
    fontStyle: 'italic',
  },
  dhsLocationList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.md,
  },
  dhsLocationItem: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.xs,
    color: colors.text,
  },
  dhsAddressLink: {
    color: colors.primary,
    textDecoration: 'none',
    fontSize: TYPOGRAPHY.fontSize.sm,
    paddingLeft: SPACING.md,
    display: 'block',
    transition: 'color 0.2s',
  },
  dhsBackButton: {
    padding: `${SPACING.sm} ${SPACING.lg}`,
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: colors.primary,
    backgroundColor: 'transparent',
    border: `2px solid ${colors.primary}`,
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: SPACING.md,
    width: '100%',
  },
});
