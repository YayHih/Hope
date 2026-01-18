/**
 * Privacy Policy Screen - Privacy information and data practices
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../constants/theme';

export function PrivacyPolicyScreen() {
  const privacyPoints = [
    {
      icon: '🚫',
      title: 'No Data Selling',
      description: 'We do not sell, trade, or share your personal data with third parties.',
    },
    {
      icon: '📢',
      title: 'No Advertisements',
      description: 'There are no advertisements on Hope for NYC. We will never show you ads.',
    },
    {
      icon: '📍',
      title: 'Location Privacy',
      description: 'We use your location only to show nearest services. We do not save location history.',
    },
    {
      icon: '👤',
      title: 'No Account Required',
      description: 'No account is needed to use the app. You can access all services anonymously.',
    },
    {
      icon: '🔒',
      title: 'Secure Connection',
      description: 'All communication with our servers uses encrypted HTTPS connections.',
    },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🔒</Text>
        <Text style={styles.headerTitle}>Privacy Policy</Text>
        <Text style={styles.headerSubtitle}>
          Your privacy and dignity are our top priorities
        </Text>
      </View>

      <View style={styles.keyPointsSection}>
        <Text style={styles.sectionTitle}>Key Points</Text>
        {privacyPoints.map((point, index) => (
          <View key={index} style={styles.pointCard}>
            <Text style={styles.pointIcon}>{point.icon}</Text>
            <View style={styles.pointContent}>
              <Text style={styles.pointTitle}>{point.title}</Text>
              <Text style={styles.pointDescription}>{point.description}</Text>
            </View>
          </View>
        ))}
      </View>

      <View style={styles.detailsSection}>
        <Text style={styles.sectionTitle}>What We Collect</Text>
        <View style={styles.listCard}>
          <Text style={styles.listItem}>
            • <Text style={styles.bold}>Location Data:</Text> Only when you grant permission, and only to show nearby services. Never stored.
          </Text>
          <Text style={styles.listItem}>
            • <Text style={styles.bold}>Anonymous Usage:</Text> We collect basic, anonymous usage statistics (like number of searches) to improve the service.
          </Text>
          <Text style={styles.listItem}>
            • <Text style={styles.bold}>No Personal Information:</Text> We don't collect names, emails, phone numbers, or any identifying information.
          </Text>
        </View>
      </View>

      <View style={styles.detailsSection}>
        <Text style={styles.sectionTitle}>Your Rights</Text>
        <View style={styles.listCard}>
          <Text style={styles.listItem}>
            • <Text style={styles.bold}>Control Location:</Text> You can deny location access and still use the app with manual search.
          </Text>
          <Text style={styles.listItem}>
            • <Text style={styles.bold}>No Tracking:</Text> We don't use cookies or tracking pixels.
          </Text>
          <Text style={styles.listItem}>
            • <Text style={styles.bold}>Open Source:</Text> Our code is open source, so you can verify our privacy practices.
          </Text>
        </View>
      </View>

      <View style={styles.contactSection}>
        <Text style={styles.contactTitle}>Questions About Privacy?</Text>
        <Text style={styles.contactText}>
          If you have concerns about privacy or data handling, please contact us at:
        </Text>
        <Text style={styles.contactEmail}>privacy@hopefornyc.com</Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Last Updated: January 2026
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
    alignItems: 'center',
    marginBottom: SPACING.xl,
  },
  headerIcon: {
    fontSize: 48,
    marginBottom: SPACING.md,
  },
  headerTitle: {
    ...TYPOGRAPHY.h1,
    color: COLORS.primary,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  headerSubtitle: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
  keyPointsSection: {
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.primary,
    marginBottom: SPACING.md,
  },
  pointCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.surface,
    padding: SPACING.md,
    borderRadius: SPACING.md,
    marginBottom: SPACING.sm,
    ...SHADOWS.small,
  },
  pointIcon: {
    fontSize: 28,
    marginRight: SPACING.md,
  },
  pointContent: {
    flex: 1,
  },
  pointTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SPACING.xs,
  },
  pointDescription: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  detailsSection: {
    marginBottom: SPACING.xl,
  },
  listCard: {
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.md,
    borderRadius: SPACING.md,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primary,
  },
  listItem: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.md,
    lineHeight: 22,
  },
  bold: {
    fontWeight: '600',
    color: COLORS.text,
  },
  contactSection: {
    backgroundColor: COLORS.primaryLight,
    padding: SPACING.lg,
    borderRadius: SPACING.md,
    alignItems: 'center',
    marginBottom: SPACING.xl,
    ...SHADOWS.medium,
  },
  contactTitle: {
    ...TYPOGRAPHY.h3,
    color: COLORS.textInverse,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  contactText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textInverse,
    textAlign: 'center',
    marginBottom: SPACING.sm,
  },
  contactEmail: {
    ...TYPOGRAPHY.body,
    color: COLORS.textInverse,
    fontWeight: '700',
    textDecorationLine: 'underline',
  },
  footer: {
    alignItems: 'center',
    paddingTop: SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider,
  },
  footerText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
  },
});
