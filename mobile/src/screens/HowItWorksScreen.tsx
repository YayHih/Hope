/**
 * How It Works Screen - Instructions for using the app
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../constants/theme';

export function HowItWorksScreen() {
  const steps = [
    {
      number: '1',
      title: 'Open the Map',
      description: 'As soon as you open the app, you will see services near your current location.',
      icon: '🗺️',
    },
    {
      number: '2',
      title: 'Tap a Location',
      description: 'Click on any pin to see what services they offer, their operating hours, and if there are specific requirements.',
      icon: '📍',
    },
    {
      number: '3',
      title: 'Use Filters',
      description: 'Need food right now? Use the "Open Now" or "Tonight" filters.',
      icon: '🔍',
    },
    {
      number: '4',
      title: 'Call Before You Go',
      description: 'If a phone number is listed, try to call to ensure they have space.',
      icon: '📞',
    },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>How This Works</Text>
        <Text style={styles.headerSubtitle}>
          Four simple steps to find help quickly
        </Text>
      </View>

      {steps.map((step) => (
        <View key={step.number} style={styles.stepCard}>
          <View style={styles.stepIconContainer}>
            <Text style={styles.stepIcon}>{step.icon}</Text>
          </View>
          <View style={styles.stepContent}>
            <View style={styles.stepHeader}>
              <View style={styles.stepNumberBadge}>
                <Text style={styles.stepNumber}>Step {step.number}</Text>
              </View>
              <Text style={styles.stepTitle}>{step.title}</Text>
            </View>
            <Text style={styles.stepDescription}>{step.description}</Text>
          </View>
        </View>
      ))}

      <View style={styles.tipCard}>
        <Text style={styles.tipIcon}>💡</Text>
        <View style={styles.tipContent}>
          <Text style={styles.tipTitle}>Quick Tip</Text>
          <Text style={styles.tipText}>
            Save time by using the category filters (Food, Shelter, Medical, etc.) to see only what you need right now.
          </Text>
        </View>
      </View>

      <View style={styles.helpCard}>
        <Text style={styles.helpTitle}>Need More Help?</Text>
        <Text style={styles.helpText}>
          For emergency assistance or if you're in immediate danger, always call 911.
        </Text>
        <Text style={styles.helpText}>
          For general assistance and service referrals, call 311 from any phone in NYC.
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
    alignItems: 'center',
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
  stepCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.surface,
    padding: SPACING.md,
    borderRadius: SPACING.md,
    marginBottom: SPACING.md,
    ...SHADOWS.small,
  },
  stepIconContainer: {
    width: 60,
    height: 60,
    backgroundColor: COLORS.primary,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  stepIcon: {
    fontSize: 28,
  },
  stepContent: {
    flex: 1,
  },
  stepHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.xs,
  },
  stepNumberBadge: {
    backgroundColor: COLORS.primaryLight,
    paddingHorizontal: SPACING.sm,
    paddingVertical: 2,
    borderRadius: 12,
    marginRight: SPACING.sm,
  },
  stepNumber: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textInverse,
    fontWeight: '700',
    fontSize: 11,
  },
  stepTitle: {
    ...TYPOGRAPHY.h3,
    color: COLORS.text,
    fontSize: 18,
  },
  stepDescription: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    lineHeight: 22,
  },
  tipCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.accent,
    padding: SPACING.md,
    borderRadius: SPACING.md,
    marginTop: SPACING.lg,
    marginBottom: SPACING.md,
    ...SHADOWS.medium,
  },
  tipIcon: {
    fontSize: 32,
    marginRight: SPACING.md,
  },
  tipContent: {
    flex: 1,
  },
  tipTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.textInverse,
    marginBottom: SPACING.xs,
  },
  tipText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textInverse,
    lineHeight: 20,
  },
  helpCard: {
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.lg,
    borderRadius: SPACING.md,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginTop: SPACING.lg,
  },
  helpTitle: {
    ...TYPOGRAPHY.h3,
    color: COLORS.primary,
    marginBottom: SPACING.md,
  },
  helpText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.sm,
    lineHeight: 22,
  },
});
