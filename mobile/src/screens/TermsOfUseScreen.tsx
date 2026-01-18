/**
 * Terms of Use Screen - Legal terms and disclaimers
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../constants/theme';

export function TermsOfUseScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Terms of Use</Text>
        <Text style={styles.headerSubtitle}>
          Please read these terms carefully before using Hope for NYC
        </Text>
      </View>

      <View style={styles.disclaimerCard}>
        <Text style={styles.disclaimerIcon}>⚠️</Text>
        <View style={styles.disclaimerContent}>
          <Text style={styles.disclaimerTitle}>Important Disclaimer</Text>
          <Text style={styles.disclaimerText}>
            Information is provided "as-is." We cannot guarantee that every listing is 100% accurate.
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>1. Service Description</Text>
        <Text style={styles.bodyText}>
          Hope for NYC is a directory service that provides information about homeless services, food pantries, and social services in New York City. We are not a service provider ourselves.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>2. No Guarantee of Accuracy</Text>
        <Text style={styles.bodyText}>
          While we strive to maintain accurate information, service availability, hours, and requirements can change without notice. We strongly recommend calling ahead before visiting any location.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>3. Not a Service Provider</Text>
        <Text style={styles.bodyText}>
          We are a directory, not a provider. We are not responsible if:
        </Text>
        <View style={styles.bulletList}>
          <Text style={styles.bulletItem}>• A service is full or unavailable</Text>
          <Text style={styles.bulletItem}>• A facility denies entry for any reason</Text>
          <Text style={styles.bulletItem}>• Hours or requirements have changed</Text>
          <Text style={styles.bulletItem}>• A location is temporarily or permanently closed</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>4. User Responsibility</Text>
        <Text style={styles.bodyText}>
          Users are responsible for:
        </Text>
        <View style={styles.bulletList}>
          <Text style={styles.bulletItem}>• Verifying information before visiting locations</Text>
          <Text style={styles.bulletItem}>• Following facility rules and requirements</Text>
          <Text style={styles.bulletItem}>• Using the app responsibly and lawfully</Text>
          <Text style={styles.bulletItem}>• Respecting the privacy of others</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>5. No Warranty</Text>
        <Text style={styles.bodyText}>
          This app is provided "as-is" without warranty of any kind, express or implied. We do not guarantee uninterrupted access or error-free operation.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>6. Limitation of Liability</Text>
        <Text style={styles.bodyText}>
          Hope for NYC and its operators shall not be liable for any direct, indirect, incidental, or consequential damages arising from use of this service.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>7. Emergency Situations</Text>
        <Text style={styles.bodyText}>
          For life-threatening emergencies, always call 911. This app is not a substitute for emergency services.
        </Text>
      </View>

      <View style={styles.highlightCard}>
        <Text style={styles.highlightTitle}>💙 Our Commitment</Text>
        <Text style={styles.highlightText}>
          Despite these legal disclaimers, we are deeply committed to providing accurate, helpful information. We continuously work to improve our data quality and user experience.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>8. Changes to Terms</Text>
        <Text style={styles.bodyText}>
          We reserve the right to modify these terms at any time. Continued use of the app constitutes acceptance of updated terms.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>9. Contact</Text>
        <Text style={styles.bodyText}>
          For questions about these terms, please contact:{'\n'}
          <Text style={styles.emailText}>legal@hopefornyc.com</Text>
        </Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Last Updated: January 2026{'\n'}
          Hope for NYC
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.xl,
  },
  header: {
    marginBottom: SPACING.xl,
  },
  headerTitle: {
    ...TYPOGRAPHY.h1,
    color: COLORS.primary,
    marginBottom: SPACING.sm,
  },
  headerSubtitle: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    lineHeight: 22,
  },
  disclaimerCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.accentWarning,
    padding: SPACING.md,
    borderRadius: SPACING.md,
    marginBottom: SPACING.xl,
    ...SHADOWS.medium,
  },
  disclaimerIcon: {
    fontSize: 32,
    marginRight: SPACING.md,
  },
  disclaimerContent: {
    flex: 1,
  },
  disclaimerTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.textInverse,
    marginBottom: SPACING.xs,
  },
  disclaimerText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textInverse,
    lineHeight: 22,
  },
  section: {
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    ...TYPOGRAPHY.h3,
    color: COLORS.primary,
    marginBottom: SPACING.sm,
  },
  bodyText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    lineHeight: 24,
  },
  bulletList: {
    marginTop: SPACING.sm,
    paddingLeft: SPACING.md,
  },
  bulletItem: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.xs,
    lineHeight: 22,
  },
  highlightCard: {
    backgroundColor: COLORS.primaryLight,
    padding: SPACING.lg,
    borderRadius: SPACING.md,
    marginBottom: SPACING.xl,
    ...SHADOWS.small,
  },
  highlightTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 18,
    color: COLORS.textInverse,
    marginBottom: SPACING.sm,
  },
  highlightText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textInverse,
    lineHeight: 24,
  },
  emailText: {
    ...TYPOGRAPHY.body,
    color: COLORS.primary,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  footer: {
    marginTop: SPACING.xl,
    paddingTop: SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider,
    alignItems: 'center',
  },
  footerText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textLight,
    textAlign: 'center',
    lineHeight: 20,
  },
});
