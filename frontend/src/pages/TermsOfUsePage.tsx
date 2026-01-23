import React from 'react';
import { SPACING, TYPOGRAPHY } from '../theme';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

const TermsOfUseScreen: React.FC = () => {
  const { t } = useLanguage();
  const { colors, isDark } = useTheme();

  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      padding: SPACING.md,
      maxWidth: '900px',
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
      marginBottom: SPACING.sm,
      textAlign: 'center',
    },
    lastUpdated: {
      fontSize: TYPOGRAPHY.fontSize.sm,
      color: colors.textSecondary,
      textAlign: 'center',
      marginBottom: SPACING.xl,
    },
    subheader: {
      fontSize: TYPOGRAPHY.fontSize.xl,
      fontWeight: TYPOGRAPHY.fontWeight.semibold,
      color: colors.text,
      marginBottom: SPACING.sm,
      marginTop: SPACING.md,
    },
    disclaimerCard: {
      backgroundColor: isDark ? 'rgba(237, 137, 54, 0.15)' : '#FFF5F5',
      padding: SPACING.lg,
      borderRadius: '12px',
      marginBottom: SPACING.xl,
      border: `2px solid ${colors.accentWarning}`,
    },
    section: {
      marginBottom: SPACING.xl,
    },
    text: {
      fontSize: TYPOGRAPHY.fontSize.base,
      lineHeight: TYPOGRAPHY.lineHeight.relaxed,
      color: colors.text,
      marginBottom: SPACING.sm,
    },
    list: {
      margin: `${SPACING.sm} 0`,
      paddingLeft: SPACING.xl,
    },
    listItem: {
      fontSize: TYPOGRAPHY.fontSize.base,
      lineHeight: TYPOGRAPHY.lineHeight.relaxed,
      color: colors.text,
      marginBottom: SPACING.sm,
    },
    link: {
      color: colors.primary,
      textDecoration: 'underline',
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.header}>{t('termsOfService')}</h1>

        <div style={styles.lastUpdated}>Last Updated: January 9, 2026</div>

        <div style={styles.disclaimerCard}>
          <h2 style={styles.subheader}>Important Disclaimer</h2>
          <p style={styles.text}>
            Information is provided "as-is" without warranties of any kind. We cannot guarantee
            that every listing is 100% accurate. We are a directory service, not a service provider;
            we are not responsible if a service is full, denies entry, or is unavailable.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>1. Acceptance of Terms</h2>
          <p style={styles.text}>
            By accessing or using the Hope for NYC website and services (the "Service"), you agree
            to be bound by these Terms of Use and all applicable laws and regulations. If you do not
            agree with any of these terms, you are prohibited from using or accessing this site.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>2. Description of Service</h2>
          <p style={styles.text}>
            Hope for NYC provides a free, public directory of essential services including shelters,
            food pantries, medical facilities, and social services in New York City. We aggregate
            information from public sources and verified service providers.
          </p>
          <p style={styles.text}>
            <strong>We are NOT:</strong>
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>A shelter or service provider</li>
            <li style={styles.listItem}>A government agency</li>
            <li style={styles.listItem}>A donation platform or fundraising organization</li>
            <li style={styles.listItem}>An emergency services coordinator</li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>3. No Warranty of Accuracy</h2>
          <p style={styles.text}>
            While we strive to maintain accurate and up-to-date information, service availability,
            hours of operation, requirements, and other details can change without notice. We make
            no representations or warranties regarding:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>The accuracy, completeness, or reliability of any information</li>
            <li style={styles.listItem}>The availability of services or space at any location</li>
            <li style={styles.listItem}>The quality of services provided by third parties</li>
            <li style={styles.listItem}>The hours of operation or service requirements</li>
          </ul>
          <p style={styles.text}>
            <strong>YOU ARE STRONGLY ENCOURAGED</strong> to call ahead to any location to verify
            availability, hours, and requirements before visiting.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>4. Limitation of Liability</h2>
          <p style={styles.text}>
            To the maximum extent permitted by applicable law, Hope for NYC and its operators,
            contributors, and affiliates shall not be liable for any direct, indirect, incidental,
            special, consequential, or punitive damages arising from:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>Use or inability to use the Service</li>
            <li style={styles.listItem}>Inaccurate or outdated information</li>
            <li style={styles.listItem}>Service unavailability or denial of services</li>
            <li style={styles.listItem}>Reliance on information provided through the Service</li>
            <li style={styles.listItem}>Any interactions with third-party service providers</li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>5. User Responsibilities</h2>
          <p style={styles.text}>When using this Service, you agree to:</p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              Use the Service only for lawful purposes and in accordance with these Terms
            </li>
            <li style={styles.listItem}>
              Not attempt to gain unauthorized access to any portion of the Service
            </li>
            <li style={styles.listItem}>
              Not use the Service in any manner that could disable, overburden, or impair it
            </li>
            <li style={styles.listItem}>
              Not submit false, misleading, or abusive reports through the reporting feature
            </li>
            <li style={styles.listItem}>
              Verify information independently before relying on it for critical decisions
            </li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>6. Third-Party Services</h2>
          <p style={styles.text}>
            All service locations listed on Hope for NYC are independently operated third-party
            entities. We do not control, endorse, or assume responsibility for the actions, policies,
            or practices of any service provider. Your interactions with service providers are solely
            between you and such providers.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>7. Intellectual Property</h2>
          <p style={styles.text}>
            The Service and its original content, features, and functionality are owned by Hope for NYC
            and are protected by international copyright, trademark, patent, trade secret, and other
            intellectual property laws. The data aggregated from public sources remains subject to its
            original licensing terms.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>8. Modifications to Service and Terms</h2>
          <p style={styles.text}>
            We reserve the right to modify or discontinue the Service at any time without notice.
            We may also revise these Terms at any time by updating this page. Continued use of the
            Service after any modifications constitutes acceptance of the new Terms.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>9. Emergency Situations</h2>
          <p style={styles.text}>
            <strong>IN CASE OF EMERGENCY, CALL 911 IMMEDIATELY.</strong>
          </p>
          <p style={styles.text}>
            This Service is not intended for emergency situations. For immediate assistance with
            homelessness or housing crisis, contact:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>NYC 311 for general city services and information</li>
            <li style={styles.listItem}>NYC Department of Homeless Services (DHS) for shelter placement</li>
            <li style={styles.listItem}>911 for life-threatening emergencies</li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>10. Governing Law</h2>
          <p style={styles.text}>
            These Terms shall be governed and construed in accordance with the laws of the State of
            New York, United States, without regard to its conflict of law provisions.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>11. Contact Information</h2>
          <p style={styles.text}>
            For questions about these Terms of Use, please contact us at{' '}
            <a href="mailto:campuslens.help@gmail.com" style={styles.link}>
              campuslens.help@gmail.com
            </a>
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>12. Severability</h2>
          <p style={styles.text}>
            If any provision of these Terms is held to be invalid or unenforceable by a court,
            the remaining provisions will remain in effect. These Terms constitute the entire
            agreement between us regarding our Service and supersede any prior agreements.
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsOfUseScreen;
