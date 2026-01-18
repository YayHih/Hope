/**
 * Provider Portal Screen - Login and information for service providers
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS, BORDER_RADIUS } from '../constants/theme';

export function ProviderPortalScreen() {
  const [email, setEmail] = useState('');

  const handleRequestAccess = async () => {
    const subject = encodeURIComponent('Provider Portal Access Request');
    const body = encodeURIComponent(
      `Hello,\n\nI would like to request access to the Hope for NYC Provider Portal.\n\nOrganization: \nContact Name: \nEmail: ${email}\nPhone: \n\nThank you!`
    );

    const mailtoUrl = `mailto:providers@hopefornyc.com?subject=${subject}&body=${body}`;

    try {
      const supported = await Linking.canOpenURL(mailtoUrl);
      if (supported) {
        await Linking.openURL(mailtoUrl);
      }
    } catch (error) {
      console.error('Error opening email:', error);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🏢</Text>
        <Text style={styles.headerTitle}>Provider Portal</Text>
        <Text style={styles.headerSubtitle}>
          For administrators at shelters, food pantries, and service organizations
        </Text>
      </View>

      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Who This Is For</Text>
        <Text style={styles.infoText}>
          The Provider Portal is designed for administrators at shelters, food pantries, and service organizations who want to keep their listing information current.
        </Text>
      </View>

      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>What You Can Do</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⏰</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Update Hours</Text>
              <Text style={styles.featureText}>
                Keep your operating hours current, including special holiday schedules
              </Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📊</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Mark Capacity</Text>
              <Text style={styles.featureText}>
                Update bed availability or food supply status in real-time
              </Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔒</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Close Facilities</Text>
              <Text style={styles.featureText}>
                Temporarily close your listing for maintenance or emergencies
              </Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📝</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Edit Information</Text>
              <Text style={styles.featureText}>
                Update contact details, services offered, and requirements
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.accessSection}>
        <Text style={styles.sectionTitle}>Request Access</Text>
        <Text style={styles.accessDescription}>
          To request access to the Provider Portal, please provide your email address and we'll send you login instructions.
        </Text>

        <TextInput
          style={styles.input}
          placeholder="your.email@organization.org"
          placeholderTextColor={COLORS.textLight}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <TouchableOpacity
          style={styles.requestButton}
          onPress={handleRequestAccess}
        >
          <Text style={styles.requestButtonText}>Request Access</Text>
        </TouchableOpacity>

        <Text style={styles.helperText}>
          You will receive an email with setup instructions within 1-2 business days.
        </Text>
      </View>

      <View style={styles.divider} />

      <View style={styles.existingUserSection}>
        <Text style={styles.sectionTitle}>Existing Users</Text>
        <Text style={styles.existingUserText}>
          If you already have access, please log in through the web portal:
        </Text>
        <TouchableOpacity
          style={styles.linkButton}
          onPress={() => Linking.openURL('https://hopefornyc.com/providers')}
        >
          <Text style={styles.linkButtonText}>Open Web Portal →</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.supportCard}>
        <Text style={styles.supportIcon}>💬</Text>
        <View style={styles.supportContent}>
          <Text style={styles.supportTitle}>Need Help?</Text>
          <Text style={styles.supportText}>
            Contact our provider support team:{'\n'}
            <Text style={styles.emailLink}>providers@hopefornyc.com</Text>
          </Text>
        </View>
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
    lineHeight: 22,
  },
  infoCard: {
    backgroundColor: COLORS.primaryLight,
    padding: SPACING.lg,
    borderRadius: BORDER_RADIUS.md,
    marginBottom: SPACING.xl,
    ...SHADOWS.medium,
  },
  infoTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 18,
    color: COLORS.textInverse,
    marginBottom: SPACING.sm,
  },
  infoText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textInverse,
    lineHeight: 22,
  },
  featuresSection: {
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.primary,
    marginBottom: SPACING.md,
  },
  featuresList: {
    gap: SPACING.md,
  },
  featureItem: {
    flexDirection: 'row',
    backgroundColor: COLORS.surface,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    ...SHADOWS.small,
  },
  featureIcon: {
    fontSize: 28,
    marginRight: SPACING.md,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SPACING.xs,
  },
  featureText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  accessSection: {
    marginBottom: SPACING.xl,
  },
  accessDescription: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.md,
    lineHeight: 22,
  },
  input: {
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  requestButton: {
    backgroundColor: COLORS.accent,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    ...SHADOWS.medium,
  },
  requestButtonText: {
    ...TYPOGRAPHY.button,
    color: COLORS.textInverse,
  },
  helperText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    textAlign: 'center',
    marginTop: SPACING.sm,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.divider,
    marginVertical: SPACING.xl,
  },
  existingUserSection: {
    marginBottom: SPACING.xl,
  },
  existingUserText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.md,
    lineHeight: 22,
  },
  linkButton: {
    backgroundColor: COLORS.primary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    ...SHADOWS.small,
  },
  linkButtonText: {
    ...TYPOGRAPHY.button,
    color: COLORS.textInverse,
  },
  supportCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primary,
  },
  supportIcon: {
    fontSize: 28,
    marginRight: SPACING.md,
  },
  supportContent: {
    flex: 1,
  },
  supportTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SPACING.xs,
  },
  supportText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  emailLink: {
    color: COLORS.primary,
    fontWeight: '600',
  },
});
