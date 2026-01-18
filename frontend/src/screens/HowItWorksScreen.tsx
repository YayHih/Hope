import React from 'react';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme';
import { useLanguage } from '../i18n/LanguageContext';

const HowItWorksScreen: React.FC = () => {
  const { t } = useLanguage();

  const steps = [
    {
      number: 1,
      icon: '🗺️',
      title: t('step1Title'),
      description: t('step1Desc'),
    },
    {
      number: 2,
      icon: '📍',
      title: t('step2Title'),
      description: t('step2Desc'),
    },
    {
      number: 3,
      icon: '🔍',
      title: t('step3Title'),
      description: t('step3Desc'),
    },
    {
      number: 4,
      icon: '📞',
      title: t('step4Title'),
      description: t('step4Desc'),
    },
  ];

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.header}>{t('howItWorksHeader')}</h1>

        <div style={styles.stepsContainer}>
          {steps.map((step) => (
            <div key={step.number} style={styles.stepCard}>
              <div style={styles.stepIcon}>{step.icon}</div>
              <div style={styles.stepContent}>
                <h2 style={styles.stepTitle}>
                  {t('step')} {step.number}: {step.title}
                </h2>
                <p style={styles.stepDescription}>{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    padding: SPACING.md,
    maxWidth: '800px',
    margin: '0 auto',
    backgroundColor: COLORS.background,
  },
  content: {
    padding: SPACING.lg,
  },
  header: {
    fontSize: TYPOGRAPHY.fontSize['3xl'],
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.primary,
    marginBottom: SPACING.xl,
    textAlign: 'center',
  },
  stepsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: SPACING.lg,
  },
  stepCard: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: SPACING.md,
    backgroundColor: COLORS.backgroundGray,
    padding: SPACING.lg,
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  },
  stepIcon: {
    fontSize: '48px',
    flexShrink: 0,
  },
  stepContent: {
    flex: 1,
  },
  stepTitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  stepDescription: {
    fontSize: TYPOGRAPHY.fontSize.base,
    lineHeight: TYPOGRAPHY.lineHeight.relaxed,
    color: COLORS.textSecondary,
  },
};

export default HowItWorksScreen;
