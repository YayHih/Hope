import React from 'react';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme';
import { useLanguage } from '../i18n/LanguageContext';

const PrivacyPolicyScreen: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.header}>{t('privacyPolicy')}</h1>

        <div style={styles.lastUpdated}>Last Updated: January 9, 2026</div>

        <div style={styles.keyPointsCard}>
          <h2 style={styles.subheader}>Key Points</h2>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              We <strong>do not sell, trade, or share</strong> your personal data with third parties.
            </li>
            <li style={styles.listItem}>
              There are <strong>no advertisements</strong> and no tracking pixels.
            </li>
            <li style={styles.listItem}>
              We use your location <strong>only</strong> to show nearest services; we do not save location history.
            </li>
            <li style={styles.listItem}>
              <strong>No account required</strong> to use the app - fully anonymous access.
            </li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>1. Introduction</h2>
          <p style={styles.text}>
            Hope for NYC ("we", "our", or "us") is committed to protecting your privacy. This Privacy
            Policy explains how we collect, use, and safeguard information when you use our website
            and services (the "Service"). We recognize that individuals seeking assistance with
            homelessness, food insecurity, or related services deserve the utmost respect for their
            privacy and dignity.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>2. Information We Collect</h2>

          <h3 style={styles.subsectionHeader}>2.1 Location Information</h3>
          <p style={styles.text}>
            When you grant location permissions, we access your device's GPS coordinates to:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>Display your position on the map</li>
            <li style={styles.listItem}>Calculate distances to nearby services</li>
            <li style={styles.listItem}>Show relevant services in your area</li>
          </ul>
          <p style={styles.text}>
            <strong>We do NOT:</strong>
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>Store your location data on our servers</li>
            <li style={styles.listItem}>Track your movements or create location history</li>
            <li style={styles.listItem}>Share your location with any third parties</li>
          </ul>

          <h3 style={styles.subsectionHeader}>2.2 Usage Information</h3>
          <p style={styles.text}>
            We collect minimal technical information necessary to operate the Service:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>IP Address:</strong> Temporarily logged for security, rate limiting, and
              spam prevention. Not linked to any personal information.
            </li>
            <li style={styles.listItem}>
              <strong>Browser Type & Version:</strong> Used to ensure compatibility and optimize
              the user experience.
            </li>
            <li style={styles.listItem}>
              <strong>Device Type:</strong> Helps us provide appropriate mobile or desktop layouts.
            </li>
          </ul>

          <h3 style={styles.subsectionHeader}>2.3 Voluntary Information</h3>
          <p style={styles.text}>
            If you submit a report through our "Report an Issue" feature, we collect:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>Issue description and affected location name</li>
            <li style={styles.listItem}>
              IP address (for spam prevention and abuse detection only)
            </li>
          </ul>
          <p style={styles.text}>
            <strong>You are not required to provide any personal identifying information</strong> such
            as name, email, or phone number to submit reports.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>3. How We Use Information</h2>
          <p style={styles.text}>
            We use the collected information solely to:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>Provide the Service:</strong> Display maps, calculate distances, show nearby
              services based on your location.
            </li>
            <li style={styles.listItem}>
              <strong>Improve Service Quality:</strong> Fix bugs, optimize performance, and enhance
              user experience.
            </li>
            <li style={styles.listItem}>
              <strong>Maintain Security:</strong> Prevent abuse, detect spam, and protect against
              malicious activity.
            </li>
            <li style={styles.listItem}>
              <strong>Process Reports:</strong> Review and act on user-submitted issue reports to
              maintain data accuracy.
            </li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>4. Information Sharing and Disclosure</h2>
          <p style={styles.text}>
            <strong>We do NOT sell, rent, trade, or share your personal information with any third
            parties for marketing or commercial purposes.</strong>
          </p>
          <p style={styles.text}>
            We may disclose information only in the following limited circumstances:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>Legal Requirements:</strong> If required by law, court order, or governmental
              request.
            </li>
            <li style={styles.listItem}>
              <strong>Protection of Rights:</strong> To protect the rights, property, or safety of
              Hope for NYC, our users, or the public.
            </li>
            <li style={styles.listItem}>
              <strong>Service Providers:</strong> We use trusted infrastructure providers (hosting,
              database, email) who are contractually obligated to protect your data and use it only
              for providing services to us.
            </li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>5. Data Retention</h2>
          <p style={styles.text}>
            We retain data only as long as necessary to provide the Service:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>Location Data:</strong> Never stored. Processed in real-time and immediately
              discarded.
            </li>
            <li style={styles.listItem}>
              <strong>Server Logs:</strong> Retained for 30 days for security and debugging purposes,
              then automatically deleted.
            </li>
            <li style={styles.listItem}>
              <strong>Issue Reports:</strong> Retained until the issue is resolved, then archived or
              deleted.
            </li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>6. Your Rights and Choices</h2>
          <p style={styles.text}>You have the following rights regarding your information:</p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>Location Permissions:</strong> You can revoke location access at any time
              through your browser or device settings. The Service will still function but will
              require manual location entry.
            </li>
            <li style={styles.listItem}>
              <strong>Do Not Track:</strong> We honor browser "Do Not Track" signals and do not
              track users across websites.
            </li>
            <li style={styles.listItem}>
              <strong>Data Deletion:</strong> Since we don't store personal data beyond temporary
              logs, there is minimal data to delete. Contact us if you have specific concerns.
            </li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>7. Cookies and Tracking Technologies</h2>
          <p style={styles.text}>
            We use minimal cookies and local storage to provide core functionality:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>Essential Cookies:</strong> Required for the Service to function (e.g., session
              management, security).
            </li>
            <li style={styles.listItem}>
              <strong>Local Storage:</strong> May store user preferences (e.g., map zoom level,
              language preference) locally on your device.
            </li>
          </ul>
          <p style={styles.text}>
            <strong>We do NOT use:</strong>
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>Advertising cookies or tracking pixels</li>
            <li style={styles.listItem}>Third-party analytics services (e.g., Google Analytics)</li>
            <li style={styles.listItem}>Social media tracking or "Like" buttons</li>
            <li style={styles.listItem}>Cross-site tracking or behavioral advertising</li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>8. Security Measures</h2>
          <p style={styles.text}>
            We implement industry-standard security measures to protect your information:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>HTTPS Encryption:</strong> All data transmitted between your device and our
              servers is encrypted using SSL/TLS.
            </li>
            <li style={styles.listItem}>
              <strong>Rate Limiting:</strong> Prevents abuse and protects against attacks.
            </li>
            <li style={styles.listItem}>
              <strong>Secure Infrastructure:</strong> Hosted on trusted, security-compliant platforms.
            </li>
            <li style={styles.listItem}>
              <strong>No Plaintext Storage:</strong> Any sensitive data (e.g., email addresses in
              reports) is handled securely.
            </li>
          </ul>
          <p style={styles.text}>
            However, no method of transmission over the Internet is 100% secure. We cannot guarantee
            absolute security.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>9. Third-Party Services</h2>
          <p style={styles.text}>
            We use the following third-party services to provide the Service:
          </p>
          <ul style={styles.list}>
            <li style={styles.listItem}>
              <strong>OpenStreetMap:</strong> Map tiles and geocoding services. Subject to
              OpenStreetMap's privacy policy.
            </li>
            <li style={styles.listItem}>
              <strong>Cloud Hosting Provider:</strong> Infrastructure hosting (subject to their
              privacy policy).
            </li>
          </ul>
          <p style={styles.text}>
            These services have their own privacy policies, which we encourage you to review.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>10. Children's Privacy</h2>
          <p style={styles.text}>
            Our Service is not intended for individuals under the age of 13. We do not knowingly
            collect personal information from children. If you believe we have inadvertently collected
            information from a child, please contact us immediately.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>11. Changes to This Privacy Policy</h2>
          <p style={styles.text}>
            We may update this Privacy Policy from time to time. We will notify users of significant
            changes by updating the "Last Updated" date at the top of this page. Continued use of
            the Service after changes constitutes acceptance of the updated policy.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>12. Contact Us</h2>
          <p style={styles.text}>
            If you have questions, concerns, or requests regarding this Privacy Policy or our data
            practices, please contact us at:
          </p>
          <p style={styles.text}>
            Email:{' '}
            <a href="mailto:campuslens.help@gmail.com" style={styles.link}>
              campuslens.help@gmail.com
            </a>
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subheader}>13. Your Dignity Matters</h2>
          <p style={styles.text}>
            We built Hope for NYC with the belief that everyone deserves access to essential services
            without sacrificing their privacy or dignity. We will never monetize your data, track your
            movements, or share your information for profit. This Service exists to help, not to exploit.
          </p>
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    padding: SPACING.md,
    maxWidth: '900px',
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
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  lastUpdated: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: SPACING.xl,
  },
  subheader: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.text,
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  subsectionHeader: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.text,
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  keyPointsCard: {
    backgroundColor: COLORS.backgroundGray,
    padding: SPACING.lg,
    borderRadius: '12px',
    marginBottom: SPACING.xl,
    border: `2px solid ${COLORS.primary}`,
  },
  section: {
    marginBottom: SPACING.xl,
  },
  text: {
    fontSize: TYPOGRAPHY.fontSize.base,
    lineHeight: TYPOGRAPHY.lineHeight.relaxed,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  list: {
    margin: `${SPACING.sm} 0`,
    paddingLeft: SPACING.xl,
  },
  listItem: {
    fontSize: TYPOGRAPHY.fontSize.base,
    lineHeight: TYPOGRAPHY.lineHeight.relaxed,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  link: {
    color: COLORS.primary,
    textDecoration: 'underline',
  },
};

export default PrivacyPolicyScreen;
