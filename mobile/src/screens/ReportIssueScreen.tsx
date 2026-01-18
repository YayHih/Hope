/**
 * Report Issue Screen - Form to report problems with service listings
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS, BORDER_RADIUS } from '../constants/theme';

interface IssueType {
  id: string;
  label: string;
  icon: string;
}

const ISSUE_TYPES: IssueType[] = [
  { id: 'closed', label: 'Location permanently closed', icon: '🚫' },
  { id: 'hours', label: 'Hours incorrect', icon: '⏰' },
  { id: 'full', label: 'Facility full/unavailable', icon: '🔒' },
  { id: 'referral', label: 'Referral required', icon: '📋' },
  { id: 'other', label: 'Other', icon: '❓' },
];

export function ReportIssueScreen() {
  const [selectedIssue, setSelectedIssue] = useState<string>('');
  const [locationName, setLocationName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    // Validation
    if (!selectedIssue) {
      Alert.alert('Required Field', 'Please select an issue type.');
      return;
    }

    if (!locationName.trim()) {
      Alert.alert('Required Field', 'Please enter the location name.');
      return;
    }

    if (!description.trim()) {
      Alert.alert('Required Field', 'Please provide a brief explanation.');
      return;
    }

    setIsSubmitting(true);

    try {
      // TODO: Replace with actual API endpoint
      // const response = await apiService.reportIssue({
      //   issue_type: selectedIssue,
      //   location_name: locationName,
      //   description: description,
      // });

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      Alert.alert(
        'Thank You!',
        'Your report has been submitted. We will review it as soon as possible.',
        [
          {
            text: 'OK',
            onPress: () => {
              // Reset form
              setSelectedIssue('');
              setLocationName('');
              setDescription('');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert(
        'Error',
        'Unable to submit report. Please try again later.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🚩</Text>
        <Text style={styles.headerTitle}>Report an Issue</Text>
        <Text style={styles.headerSubtitle}>
          Help us keep our information accurate and up-to-date
        </Text>
      </View>

      <View style={styles.formSection}>
        <Text style={styles.label}>
          Select Issue <Text style={styles.required}>*</Text>
        </Text>
        <View style={styles.optionsGrid}>
          {ISSUE_TYPES.map((issue) => (
            <TouchableOpacity
              key={issue.id}
              style={[
                styles.optionCard,
                selectedIssue === issue.id && styles.optionCardSelected,
              ]}
              onPress={() => setSelectedIssue(issue.id)}
            >
              <Text style={styles.optionIcon}>{issue.icon}</Text>
              <Text
                style={[
                  styles.optionLabel,
                  selectedIssue === issue.id && styles.optionLabelSelected,
                ]}
              >
                {issue.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.formSection}>
        <Text style={styles.label}>
          Location Name <Text style={styles.required}>*</Text>
        </Text>
        <TextInput
          style={styles.input}
          placeholder="E.g., St. John's Bread & Life"
          placeholderTextColor={COLORS.textLight}
          value={locationName}
          onChangeText={setLocationName}
        />
      </View>

      <View style={styles.formSection}>
        <Text style={styles.label}>
          Brief Explanation <Text style={styles.required}>*</Text>
        </Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Please describe the issue..."
          placeholderTextColor={COLORS.textLight}
          value={description}
          onChangeText={setDescription}
          multiline
          numberOfLines={6}
          textAlignVertical="top"
        />
        <Text style={styles.helperText}>
          Include any relevant details that would help us verify and update the information.
        </Text>
      </View>

      <TouchableOpacity
        style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
        onPress={handleSubmit}
        disabled={isSubmitting}
      >
        <Text style={styles.submitButtonText}>
          {isSubmitting ? 'Submitting...' : 'Submit Report'}
        </Text>
      </TouchableOpacity>

      <View style={styles.infoCard}>
        <Text style={styles.infoIcon}>ℹ️</Text>
        <View style={styles.infoContent}>
          <Text style={styles.infoTitle}>What Happens Next?</Text>
          <Text style={styles.infoText}>
            Our team will review your report and update the listing if necessary. This typically takes 1-3 business days.
          </Text>
        </View>
      </View>

      <View style={styles.emergencyCard}>
        <Text style={styles.emergencyTitle}>🚨 For Emergencies</Text>
        <Text style={styles.emergencyText}>
          If you need immediate assistance or are in danger, please call 911 or contact NYC's 311 for service referrals.
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
  formSection: {
    marginBottom: SPACING.xl,
  },
  label: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  required: {
    color: COLORS.accentError,
  },
  optionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  optionCard: {
    backgroundColor: COLORS.surface,
    borderWidth: 2,
    borderColor: COLORS.border,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    alignItems: 'center',
    width: '48%',
    ...SHADOWS.small,
  },
  optionCardSelected: {
    backgroundColor: COLORS.primaryLight,
    borderColor: COLORS.primary,
  },
  optionIcon: {
    fontSize: 32,
    marginBottom: SPACING.xs,
  },
  optionLabel: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.text,
    textAlign: 'center',
  },
  optionLabelSelected: {
    color: COLORS.textInverse,
    fontWeight: '600',
  },
  input: {
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    ...TYPOGRAPHY.body,
    color: COLORS.text,
  },
  textArea: {
    minHeight: 120,
    paddingTop: SPACING.md,
  },
  helperText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: SPACING.xs,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    marginBottom: SPACING.xl,
    ...SHADOWS.medium,
  },
  submitButtonDisabled: {
    backgroundColor: COLORS.textLight,
  },
  submitButtonText: {
    ...TYPOGRAPHY.button,
    color: COLORS.textInverse,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primary,
    marginBottom: SPACING.md,
  },
  infoIcon: {
    fontSize: 24,
    marginRight: SPACING.md,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 14,
    color: COLORS.text,
    marginBottom: SPACING.xs,
  },
  infoText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  emergencyCard: {
    backgroundColor: COLORS.accentError,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    ...SHADOWS.small,
  },
  emergencyTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.textInverse,
    marginBottom: SPACING.xs,
  },
  emergencyText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textInverse,
    lineHeight: 20,
  },
});
