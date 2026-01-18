/**
 * App Navigation - Mobile-first with header, hamburger menu, and bottom tabs
 * Bottom tabs: Map (Home), Privacy, Terms, Report, Providers
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, ScrollView, Platform } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { COLORS, SPACING, TYPOGRAPHY } from '../constants/theme';

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

// Language selector component (placeholder for future implementation)
const LanguageSelector = () => {
  const [language, setLanguage] = useState('EN');

  return (
    <View style={styles.languageContainer}>
      <TouchableOpacity
        style={[styles.langButton, language === 'EN' && styles.langButtonActive]}
        onPress={() => setLanguage('EN')}
      >
        <Text style={[styles.langText, language === 'EN' && styles.langTextActive]}>EN</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.langButton, language === 'ES' && styles.langButtonActive]}
        onPress={() => setLanguage('ES')}
      >
        <Text style={[styles.langText, language === 'ES' && styles.langTextActive]}>ES</Text>
      </TouchableOpacity>
    </View>
  );
};

// Hamburger menu component
interface HamburgerMenuProps {
  navigation: any;
}

const HamburgerMenu = ({ navigation }: HamburgerMenuProps) => {
  const [menuVisible, setMenuVisible] = useState(false);

  const menuItems = [
    { label: 'About', screen: 'About', icon: 'ℹ️' },
    { label: 'How This Works', screen: 'HowItWorks', icon: '❓' },
    { label: 'Report an Issue', screen: 'Report', icon: '🚩' },
    { label: 'Provider Portal', screen: 'Providers', icon: '🏢' },
  ];

  return (
    <>
      <TouchableOpacity
        style={styles.hamburgerButton}
        onPress={() => setMenuVisible(true)}
      >
        <Text style={styles.hamburgerIcon}>☰</Text>
      </TouchableOpacity>

      <Modal
        visible={menuVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setMenuVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.menuContainer}>
            <View style={styles.menuHeader}>
              <Text style={styles.menuTitle}>Menu</Text>
              <TouchableOpacity onPress={() => setMenuVisible(false)}>
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
                >
                  <Text style={styles.menuItemIcon}>{item.icon}</Text>
                  <Text style={styles.menuItemText}>{item.label}</Text>
                </TouchableOpacity>
              ))}

              <View style={styles.menuDivider} />

              <View style={styles.menuLanguageSection}>
                <Text style={styles.menuSectionTitle}>Language</Text>
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
  return (
    <View style={styles.header}>
      <HamburgerMenu navigation={navigation} />
      <Text style={styles.headerTitle}>Hope for NYC</Text>
      <LanguageSelector />
    </View>
  );
};

// Tab icon component
const TabIcon = ({ icon, focused }: { icon: string; focused: boolean }) => (
  <Text style={{ fontSize: 24, opacity: focused ? 1 : 0.6 }}>{icon}</Text>
);

// Main tab navigator
function MainTabs() {
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
          title: 'Map',
          tabBarIcon: ({ focused }) => <TabIcon icon="🗺️" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Privacy"
        component={PrivacyPolicyScreen}
        options={{
          title: 'Privacy',
          tabBarIcon: ({ focused }) => <TabIcon icon="🔒" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Terms"
        component={TermsOfUseScreen}
        options={{
          title: 'Terms',
          tabBarIcon: ({ focused }) => <TabIcon icon="📄" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Report"
        component={ReportIssueScreen}
        options={{
          title: 'Report',
          tabBarIcon: ({ focused }) => <TabIcon icon="🚩" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Providers"
        component={ProviderPortalScreen}
        options={{
          title: 'Providers',
          tabBarIcon: ({ focused }) => <TabIcon icon="🏢" focused={focused} />,
        }}
      />
    </Tab.Navigator>
  );
}

// Root navigator with stack for modal screens
export function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Main" component={MainTabs} />
        <Stack.Screen
          name="About"
          component={AboutScreen}
          options={{
            headerShown: true,
            title: 'About',
            headerStyle: { backgroundColor: COLORS.primary },
            headerTintColor: COLORS.textInverse,
          }}
        />
        <Stack.Screen
          name="HowItWorks"
          component={HowItWorksScreen}
          options={{
            headerShown: true,
            title: 'How This Works',
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
  closeButton: {
    fontSize: 28,
    color: COLORS.textSecondary,
    padding: SPACING.sm,
  },
  menuItems: {
    paddingVertical: SPACING.md,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
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
