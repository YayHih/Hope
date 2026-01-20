import React from 'react';
import { SPACING, TYPOGRAPHY } from '../theme';
import { useTheme } from '../theme/ThemeContext';

const ProviderPortalScreen: React.FC = () => {
  const { colors } = useTheme();

  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      padding: SPACING.md,
      maxWidth: '800px',
      margin: '0 auto',
      backgroundColor: colors.background,
    },
    content: {
      padding: SPACING.lg,
    },
    header: {
      fontSize: TYPOGRAPHY.fontSize['3xl'],
      fontWeight: TYPOGRAPHY.fontWeight.bold,
      color: colors.primary,
      marginBottom: SPACING.xl,
      textAlign: 'center',
    },
    infoCard: {
      backgroundColor: colors.surface,
      padding: SPACING.xl,
      borderRadius: '12px',
      border: `2px solid ${colors.primary}`,
    },
    iconContainer: {
      textAlign: 'center',
      marginBottom: SPACING.lg,
    },
    icon: {
      fontSize: '64px',
    },
    subheader: {
      fontSize: TYPOGRAPHY.fontSize.xl,
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
      color: colors.text,
      marginBottom: SPACING.sm,
    },
    section: {
      marginBottom: SPACING.lg,
    },
    text: {
      fontSize: TYPOGRAPHY.fontSize.base,
      lineHeight: TYPOGRAPHY.lineHeight.relaxed,
      color: colors.text,
      marginBottom: SPACING.sm,
    },
    list: {
      margin: 0,
      paddingLeft: SPACING.lg,
    },
    listItem: {
      fontSize: TYPOGRAPHY.fontSize.base,
      lineHeight: TYPOGRAPHY.lineHeight.relaxed,
      color: colors.text,
      marginBottom: SPACING.sm,
    },
    emailButton: {
      display: 'inline-block',
      padding: `${SPACING.md} ${SPACING.xl}`,
      fontSize: TYPOGRAPHY.fontSize.base,
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
      color: colors.textInverse,
      backgroundColor: colors.primary,
      textDecoration: 'none',
      borderRadius: '8px',
      marginTop: SPACING.md,
      transition: 'background-color 0.2s',
    },
    note: {
      marginTop: SPACING.xl,
      padding: SPACING.md,
      backgroundColor: colors.backgroundSecondary,
      borderRadius: '8px',
    },
    noteText: {
      fontSize: TYPOGRAPHY.fontSize.sm,
      color: colors.textSecondary,
      margin: 0,
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.header}>Provider Portal</h1>

        <div style={styles.infoCard}>
          <div style={styles.iconContainer}>
            <span style={styles.icon}>🏛️</span>
          </div>

          <div style={styles.section}>
            <h2 style={styles.subheader}>Who This Is For</h2>
            <p style={styles.text}>
              Administrators at shelters and food pantries.
            </p>
          </div>

          <div style={styles.section}>
            <h2 style={styles.subheader}>What You Can Do</h2>
            <ul style={styles.list}>
              <li style={styles.listItem}>Update hours of operation</li>
              <li style={styles.listItem}>Mark capacity and availability</li>
              <li style={styles.listItem}>Close facilities or update service information</li>
              <li style={styles.listItem}>Ensure accurate information for those in need</li>
            </ul>
          </div>

          <div style={styles.section}>
            <h2 style={styles.subheader}>Request Access</h2>
            <p style={styles.text}>
              To request access to the provider portal, please contact us:
            </p>
            <a
              href="mailto:providers@hopefornyc.com"
              style={styles.emailButton}
            >
              providers@hopefornyc.com
            </a>
          </div>
        </div>

        <div style={styles.note}>
          <p style={styles.noteText}>
            <strong>Note:</strong> The provider portal is currently under development.
            We will be reaching out to service providers to offer this functionality soon.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProviderPortalScreen;
