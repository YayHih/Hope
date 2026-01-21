import React from 'react';
import { SPACING, TYPOGRAPHY } from '../theme';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

const AboutScreen: React.FC = () => {
  const { t } = useLanguage();
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
      marginBottom: SPACING.lg,
      textAlign: 'center',
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
    note: {
      fontSize: TYPOGRAPHY.fontSize.base,
      lineHeight: TYPOGRAPHY.lineHeight.relaxed,
      color: colors.textSecondary,
      backgroundColor: colors.backgroundSecondary,
      padding: SPACING.md,
      borderRadius: '8px',
      marginTop: SPACING.md,
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.header}>{t('aboutHeader')}</h1>

        <div style={styles.section}>
          <p style={styles.text}>
            {t('aboutIntro')}
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>{t('whoItsFor')}</h2>
          <p style={styles.text}>
            {t('whoItsForText')}
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>{t('whatItIsNot')}</h2>
          <p style={styles.text}>
            {t('whatItIsNotText')}
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>{t('dataSources')}</h2>
          <p style={styles.text}>
            {t('dataSourcesText')}
          </p>
          <p style={styles.note}>
            <strong>{t('pleaseNote')}</strong> {t('availabilityNote')}
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>{t('privacyNote')}</h2>
          <p style={styles.text}>
            <strong>{t('privacyNoteText')}</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AboutScreen;
