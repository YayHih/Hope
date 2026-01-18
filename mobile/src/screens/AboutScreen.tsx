/**
 * About Screen - Information about Hope for NYC
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../constants/theme';

export function AboutScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About Hope for NYC</Text>
        <Text style={styles.bodyText}>
          Hope for NYC is a free tool that helps people find shelters, food pantries, and essential social services across New York City. We exist to make finding help faster and easier.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Who It's For</Text>
        <Text style={styles.bodyText}>
          This site is for anyone currently in need, as well as the social workers, volunteers, and organizations providing help.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>What It Is NOT</Text>
        <Text style={styles.bodyText}>
          We are a directory. We are not a shelter, a government agency, or a donation platform. We do not manage the facilities listed here.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data Sources</Text>
        <Text style={styles.bodyText}>
          Our information comes from NYC Open Data and verified service providers.
        </Text>
        <View style={styles.noteCard}>
          <Text style={styles.noteTitle}>⚠️ Please Note</Text>
          <Text style={styles.noteText}>
            Availability and hours can change quickly. We strongly recommend calling a location ahead of time if you can.
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Privacy Note</Text>
        <View style={styles.highlightCard}>
          <Text style={styles.highlightTitle}>💙 Your Dignity Matters</Text>
          <Text style={styles.highlightText}>
            • No Ads{'\n'}
            • No Selling Data{'\n'}
            • No Tracking beyond what is needed to make the site work
          </Text>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Hope for NYC is an open-source, community-driven project.
        </Text>
        <Text style={styles.footerTextSmall}>
          Made with care for our neighbors.
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
  section: {
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.primary,
    marginBottom: SPACING.md,
  },
  bodyText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    lineHeight: 24,
  },
  noteCard: {
    backgroundColor: COLORS.surfaceDark,
    padding: SPACING.md,
    borderRadius: SPACING.sm,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.accentWarning,
    marginTop: SPACING.md,
  },
  noteTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SPACING.xs,
  },
  noteText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
  },
  highlightCard: {
    backgroundColor: COLORS.primaryLight,
    padding: SPACING.md,
    borderRadius: SPACING.md,
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
  footer: {
    marginTop: SPACING.xl,
    paddingTop: SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider,
    alignItems: 'center',
  },
  footerText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: SPACING.xs,
  },
  footerTextSmall: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    textAlign: 'center',
  },
});
