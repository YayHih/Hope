import React, { useState, useRef } from 'react';
import axios from 'axios';
import ReCAPTCHA from 'react-google-recaptcha';
import { SPACING, TYPOGRAPHY } from '../theme';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://hopefornyc.com/api/v1';
const RECAPTCHA_SITE_KEY = process.env.REACT_APP_RECAPTCHA_SITE_KEY || '';

const ReportIssueScreen: React.FC = () => {
  const { t } = useLanguage();
  const { colors, isDark } = useTheme();
  const [selectedIssue, setSelectedIssue] = useState<string>('');
  const [locationName, setLocationName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const recaptchaRef = useRef<ReCAPTCHA>(null);

  const issueTypes = [
    { value: 'closed', label: t('issueTypeClosed') },
    { value: 'hours', label: t('issueTypeHours') },
    { value: 'full', label: t('issueTypeFull') },
    { value: 'referral', label: t('issueTypeReferral') },
    { value: 'other', label: t('issueTypeOther') },
  ];

  const handleCaptchaChange = (token: string | null) => {
    setCaptchaToken(token);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedIssue) {
      alert(t('pleaseSelectIssue'));
      return;
    }

    if (!locationName.trim()) {
      alert(t('pleaseEnterLocation'));
      return;
    }

    if (!description.trim()) {
      alert(t('pleaseProvideExplanation'));
      return;
    }

    if (!captchaToken) {
      alert(t('pleaseCompleteCaptcha'));
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await axios.post(`${API_BASE_URL}/public/issues/report`, {
        issue_type: selectedIssue,
        location_name: locationName,
        description: description,
        captcha_token: captchaToken,
      });

      if (response.data.status === 'success') {
        setSubmitStatus('success');
        setSelectedIssue('');
        setLocationName('');
        setDescription('');
        setCaptchaToken(null);
        if (recaptchaRef.current) {
          recaptchaRef.current.reset();
        }

        setTimeout(() => setSubmitStatus('idle'), 5000);
      } else {
        setSubmitStatus('error');
        setTimeout(() => setSubmitStatus('idle'), 5000);
      }
    } catch (error) {
      console.error('Error submitting report:', error);
      setSubmitStatus('error');
      setTimeout(() => setSubmitStatus('idle'), 5000);
    } finally {
      setIsSubmitting(false);
    }
  };

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
      marginBottom: SPACING.md,
      textAlign: 'center',
    },
    description: {
      fontSize: TYPOGRAPHY.fontSize.base,
      lineHeight: TYPOGRAPHY.lineHeight.relaxed,
      color: colors.textSecondary,
      textAlign: 'center',
      marginBottom: SPACING.xl,
    },
    form: {
      display: 'flex',
      flexDirection: 'column',
      gap: SPACING.lg,
    },
    formGroup: {
      display: 'flex',
      flexDirection: 'column',
      gap: SPACING.sm,
    },
    label: {
      fontSize: TYPOGRAPHY.fontSize.base,
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
      color: colors.text,
    },
    required: {
      color: colors.accentError,
    },
    select: {
      padding: SPACING.md,
      fontSize: TYPOGRAPHY.fontSize.base,
      border: `1px solid ${colors.border}`,
      borderRadius: '8px',
      backgroundColor: colors.surface,
      color: colors.text,
      cursor: 'pointer',
    },
    input: {
      padding: SPACING.md,
      fontSize: TYPOGRAPHY.fontSize.base,
      border: `1px solid ${colors.border}`,
      borderRadius: '8px',
      backgroundColor: colors.surface,
      color: colors.text,
    },
    textarea: {
      padding: SPACING.md,
      fontSize: TYPOGRAPHY.fontSize.base,
      border: `1px solid ${colors.border}`,
      borderRadius: '8px',
      backgroundColor: colors.surface,
      color: colors.text,
      fontFamily: TYPOGRAPHY.fontFamily,
      resize: 'vertical' as const,
    },
    charCount: {
      fontSize: TYPOGRAPHY.fontSize.sm,
      color: colors.textLight,
      textAlign: 'right',
    },
    recaptchaContainer: {
      display: 'flex',
      justifyContent: 'center',
      marginTop: SPACING.md,
    },
    submitButton: {
      padding: `${SPACING.md} ${SPACING.xl}`,
      fontSize: TYPOGRAPHY.fontSize.base,
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
      color: colors.textInverse,
      backgroundColor: colors.primary,
      border: 'none',
      borderRadius: '8px',
      cursor: 'pointer',
      marginTop: SPACING.md,
      transition: 'background-color 0.2s',
    },
    submitButtonDisabled: {
      backgroundColor: colors.textLight,
      cursor: 'not-allowed',
    },
    successMessage: {
      padding: SPACING.md,
      backgroundColor: isDark ? 'rgba(72, 187, 120, 0.15)' : '#F0FFF4',
      border: `2px solid ${colors.accent}`,
      borderRadius: '8px',
      color: colors.accent,
      textAlign: 'center',
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
    },
    errorMessage: {
      padding: SPACING.md,
      backgroundColor: isDark ? 'rgba(252, 129, 129, 0.15)' : '#FFF5F5',
      border: `2px solid ${colors.accentError}`,
      borderRadius: '8px',
      color: colors.accentError,
      textAlign: 'center',
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
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
        <h1 style={styles.header}>{t('reportIssueHeader')}</h1>

        <p style={styles.description}>
          {t('reportIssueDesc')}
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label htmlFor="issueType" style={styles.label}>
              {t('selectIssueType')} <span style={styles.required}>{t('required')}</span>
            </label>
            <select
              id="issueType"
              value={selectedIssue}
              onChange={(e) => setSelectedIssue(e.target.value)}
              style={styles.select}
            >
              <option value="">{t('selectAnIssue')}</option>
              {issueTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label htmlFor="locationName" style={styles.label}>
              {t('locationNameLabel')} <span style={styles.required}>{t('required')}</span>
            </label>
            <input
              type="text"
              id="locationName"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
              placeholder={t('locationPlaceholder')}
              style={styles.input}
              maxLength={200}
            />
          </div>

          <div style={styles.formGroup}>
            <label htmlFor="description" style={styles.label}>
              {t('briefExplanation')} <span style={styles.required}>{t('required')}</span>
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={t('explanationPlaceholder')}
              style={styles.textarea}
              rows={5}
              maxLength={1000}
            />
            <div style={styles.charCount}>
              {description.length}/1000 {t('charactersCount')}
            </div>
          </div>

          <div style={styles.recaptchaContainer}>
            <ReCAPTCHA
              ref={recaptchaRef}
              sitekey={RECAPTCHA_SITE_KEY}
              onChange={handleCaptchaChange}
              theme={isDark ? 'dark' : 'light'}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !captchaToken}
            style={{
              ...styles.submitButton,
              ...(isSubmitting || !captchaToken ? styles.submitButtonDisabled : {}),
            }}
          >
            {isSubmitting ? t('submitting') : t('submitReport')}
          </button>

          {submitStatus === 'success' && (
            <div style={styles.successMessage}>
              {t('reportSuccess')}
            </div>
          )}

          {submitStatus === 'error' && (
            <div style={styles.errorMessage}>
              {t('reportError')}
            </div>
          )}
        </form>

        <div style={styles.note}>
          <p style={styles.noteText}>
            <strong>{t('noteLabel')}</strong> {t('reportNote')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ReportIssueScreen;
