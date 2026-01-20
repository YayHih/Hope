/**
 * App Navigation - Mobile-first with header, hamburger menu, and bottom tabs
 * Bottom tabs: Map (Home), Privacy, Terms, Report, Providers
 * Includes full accessibility support and i18n
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, ScrollView, Platform } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { COLORS, SPACING, TYPOGRAPHY } from '../constants/theme';
import { useLanguage, Language } from '../i18n';

// Import screens
import { MapScreen } from '../screens/MapScreen';
import { AboutScreen } from '../screens/AboutScreen';
import { HowItWorksScreen } from '../screens/HowItWorksScreen';
import { PrivacyPolicyScreen } from '../screens/PrivacyPolicyScreen';
import { TermsOfUseScreen } from '../screens/TermsOfUseScreen';
import { ReportIssueScreen } from '../screens/ReportIssueScreen';
import { ProviderPortalScreen } from '../screens/ProviderPortalScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Language order for cycling
const LANGUAGE_ORDER: Language[] = ['EN', 'ES', 'ZH'];
const LANGUAGE_LABELS: Record<Language, string> = {
  EN: 'EN',
  ES: 'ES',
  ZH: '中文',
};

// Language selector component - single button that cycles through languages
const LanguageSelector = () => {
  const { language, setLanguage, t } = useLanguage();

  const cycleLanguage = () => {
    const currentIndex = LANGUAGE_ORDER.indexOf(language);
    const nextIndex = (currentIndex + 1) % LANGUAGE_ORDER.length;
    setLanguage(LANGUAGE_ORDER[nextIndex]);
  };

  const getNextLanguageLabel = () => {
    const currentIndex = LANGUAGE_ORDER.indexOf(language);
    const nextIndex = (currentIndex + 1) % LANGUAGE_ORDER.length;
    return LANGUAGE_LABELS[LANGUAGE_ORDER[nextIndex]];
  };

  return (
    <TouchableOpacity
      style={[styles.langButton, styles.langButtonActive]}
      onPress={cycleLanguage}
      accessibilityRole="button"
      accessibilityLabel={`${t.language}: ${LANGUAGE_LABELS[language]}`}
      accessibilityHint={`Tap to switch to ${getNextLanguageLabel()}`}
    >
      <Text style={[styles.langText, styles.langTextActive]}>{LANGUAGE_LABELS[language]}</Text>
    </TouchableOpacity>
  );
};

// Hamburger menu component
interface HamburgerMenuProps {
  navigation: any;
}

const HamburgerMenu = ({ navigation }: HamburgerMenuProps) => {
  const [menuVisible, setMenuVisible] = useState(false);
  const { t } = useLanguage();

  const menuItems = [
    { label: t.about, screen: 'About', icon: 'ℹ️' },
    { label: t.howItWorks, screen: 'HowItWorks', icon: '❓' },
    { label: t.reportAnIssue, screen: 'Report', icon: '🚩' },
    { label: t.providerPortal, screen: 'Providers', icon: '🏢' },
  ];

  return (
    <>
      <TouchableOpacity
        style={styles.hamburgerButton}
        onPress={() => setMenuVisible(true)}
        accessibilityRole="button"
        accessibilityLabel={t.openMenu}
        accessibilityHint={t.opensNavigationMenu}
      >
        <Text style={styles.hamburgerIcon} accessibilityLabel="">☰</Text>
      </TouchableOpacity>

      <Modal
        visible={menuVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setMenuVisible(false)}
        accessibilityViewIsModal={true}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.menuContainer}>
            <View style={styles.menuHeader}>
              <Text style={styles.menuTitle} accessibilityRole="header">{t.menu}</Text>
              <TouchableOpacity
                onPress={() => setMenuVisible(false)}
                accessibilityRole="button"
                accessibilityLabel={t.closeMenu}
                style={styles.closeButtonTouchable}
              >
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.menuItems}>
              {menuItems.map((item) => (
                <TouchableOpacity
                  key={item.screen}
                  style={styles.menuItem}
                  onPress={() => {
                    setMenuVisible(false);
                    navigation.navigate(item.screen);
                  }}
                  accessibilityRole="button"
                  accessibilityLabel={item.label}
                >
                  <Text style={styles.menuItemIcon} accessibilityLabel="">{item.icon}</Text>
                  <Text style={styles.menuItemText}>{item.label}</Text>
                </TouchableOpacity>
              ))}

              <View style={styles.menuDivider} />

              <View style={styles.menuLanguageSection}>
                <Text style={styles.menuSectionTitle}>{t.language}</Text>
                <LanguageSelector />
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </>
  );
};

// Custom header component
const CustomHeader = ({ navigation }: { navigation: any }) => {
  const { t } = useLanguage();

  return (
    <View style={styles.header} accessibilityRole="header">
      <HamburgerMenu navigation={navigation} />
      <Text style={styles.headerTitle} accessibilityRole="header" accessibilityLabel={t.appTitle}>{t.appTitle}</Text>
      <LanguageSelector />
    </View>
  );
};

// Tab icon component with accessibility
const TabIcon = ({ icon, focused }: { icon: string; focused: boolean }) => (
  <Text style={{ fontSize: 24, opacity: focused ? 1 : 0.6 }} accessibilityLabel="">{icon}</Text>
);

// Main tab navigator
function MainTabs() {
  const { t } = useLanguage();

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textSecondary,
        tabBarStyle: styles.tabBar,
        tabBarLabelStyle: styles.tabBarLabel,
        header: ({ navigation }) => <CustomHeader navigation={navigation} />,
      }}
    >
      <Tab.Screen
        name="MapTab"
        component={MapScreen}
        options={{
          title: t.map,
          tabBarIcon: ({ focused }) => <TabIcon icon="🗺️" focused={focused} />,
          tabBarAccessibilityLabel: `${t.mapTab} - ${t.findNearbyServices}`,
        }}
      />
      <Tab.Screen
        name="Privacy"
        component={PrivacyPolicyScreen}
        options={{
          title: t.privacy,
          tabBarIcon: ({ focused }) => <TabIcon icon="🔒" focused={focused} />,
          tabBarAccessibilityLabel: t.privacyPolicyTab,
        }}
      />
      <Tab.Screen
        name="Terms"
        component={TermsOfUseScreen}
        options={{
          title: t.terms,
          tabBarIcon: ({ focused }) => <TabIcon icon="📄" focused={focused} />,
          tabBarAccessibilityLabel: t.termsOfUseTab,
        }}
      />
      <Tab.Screen
        name="Report"
        component={ReportIssueScreen}
        options={{
          title: t.report,
          tabBarIcon: ({ focused }) => <TabIcon icon="🚩" focused={focused} />,
          tabBarAccessibilityLabel: t.reportAnIssueTab,
        }}
      />
      <Tab.Screen
        name="Providers"
        component={ProviderPortalScreen}
        options={{
          title: t.providers,
          tabBarIcon: ({ focused }) => <TabIcon icon="🏢" focused={focused} />,
          tabBarAccessibilityLabel: t.providerPortalTab,
        }}
      />
    </Tab.Navigator>
  );
}

// Root navigator with stack for modal screens
export function AppNavigator() {
  const { t } = useLanguage();

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Main" component={MainTabs} />
        <Stack.Screen
          name="About"
          component={AboutScreen}
          options={{
            headerShown: true,
            title: t.about,
            headerStyle: { backgroundColor: COLORS.primary },
            headerTintColor: COLORS.textInverse,
          }}
        />
        <Stack.Screen
          name="HowItWorks"
          component={HowItWorksScreen}
          options={{
            headerShown: true,
            title: t.howItWorks,
            headerStyle: { backgroundColor: COLORS.primary },
            headerTintColor: COLORS.textInverse,
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: COLORS.primary,
    paddingHorizontal: SPACING.md,
    paddingTop: Platform.OS === 'ios' ? 50 : 10,
    paddingBottom: SPACING.sm,
    ...Platform.select({
      ios: {
        shadowColor: COLORS.shadow,
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  headerTitle: {
    ...TYPOGRAPHY.h3,
    color: COLORS.textInverse,
    flex: 1,
    textAlign: 'center',
  },
  hamburgerButton: {
    padding: SPACING.sm,
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  hamburgerIcon: {
    fontSize: 24,
    color: COLORS.textInverse,
  },
  languageContainer: {
    flexDirection: 'row',
    gap: SPACING.xs,
  },
  langButton: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: 4,
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: COLORS.textInverse,
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  langButtonActive: {
    backgroundColor: COLORS.textInverse,
  },
  langText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textInverse,
    fontWeight: '600',
  },
  langTextActive: {
    color: COLORS.primary,
  },
  tabBar: {
    backgroundColor: COLORS.background,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    paddingBottom: Platform.OS === 'ios' ? 20 : SPACING.sm,
    paddingTop: SPACING.sm,
    height: Platform.OS === 'ios' ? 85 : 65,
  },
  tabBarLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-start',
  },
  menuContainer: {
    backgroundColor: COLORS.background,
    borderBottomLeftRadius: SPACING.lg,
    borderBottomRightRadius: SPACING.lg,
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    maxHeight: '70%',
    ...Platform.select({
      ios: {
        shadowColor: COLORS.shadow,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
      },
      android: {
        elevation: 16,
      },
    }),
  },
  menuHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg,
    paddingBottom: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider,
  },
  menuTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.text,
  },
  closeButtonTouchable: {
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButton: {
    fontSize: 28,
    color: COLORS.textSecondary,
  },
  menuItems: {
    paddingVertical: SPACING.md,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    minHeight: 48,
  },
  menuItemIcon: {
    fontSize: 24,
    marginRight: SPACING.md,
  },
  menuItemText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
  },
  menuDivider: {
    height: 1,
    backgroundColor: COLORS.divider,
    marginVertical: SPACING.md,
    marginHorizontal: SPACING.lg,
  },
  menuLanguageSection: {
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
  },
  menuSectionTitle: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
    marginBottom: SPACING.sm,
    textTransform: 'uppercase',
    fontWeight: '600',
  },
});
