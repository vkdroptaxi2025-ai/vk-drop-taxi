import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { Colors } from '../utils/colors';
import { Ionicons } from '@expo/vector-icons';

export default function Index() {
  const router = useRouter();
  const { isAuthenticated, user, loadUser } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, []);

  useEffect(() => {
    if (isAuthenticated && user) {
      // Navigate based on role
      if (user.role === 'customer') {
        router.replace('/customer/home');
      } else if (user.role === 'driver') {
        router.replace('/driver/dashboard');
      }
    }
  }, [isAuthenticated, user]);

  const handleRoleSelection = (role: 'customer' | 'driver') => {
    router.push(`/auth/login?role=${role}`);
  };

  const handleAdminAccess = () => {
    router.push('/admin/dashboard');
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Image
            source={require('../assets/images/vk-logo-app.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>
      </View>

      {/* Role Selection */}
      <ScrollView 
        style={styles.scrollContainer}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title}>Welcome!</Text>
        <Text style={styles.subtitle}>Select your role to continue</Text>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.roleCard, styles.customerCard]}
            onPress={() => handleRoleSelection('customer')}
            activeOpacity={0.8}
          >
            <View style={styles.iconCircle}>
              <Ionicons name="person" size={32} color={Colors.primary} />
            </View>
            <Text style={styles.roleTitle}>Customer</Text>
            <Text style={styles.roleDescription}>Book a ride</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.roleCard, styles.driverCard]}
            onPress={() => handleRoleSelection('driver')}
            activeOpacity={0.8}
          >
            <View style={styles.iconCircle}>
              <Ionicons name="car" size={32} color={Colors.secondary} />
            </View>
            <Text style={styles.roleTitle}>Driver</Text>
            <Text style={styles.roleDescription}>Start earning</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.roleCard, styles.adminCard]}
            onPress={handleAdminAccess}
            activeOpacity={0.8}
          >
            <View style={[styles.iconCircle, styles.adminIconCircle]}>
              <Ionicons name="shield-checkmark" size={32} color={Colors.text} />
            </View>
            <Text style={styles.roleTitle}>Admin</Text>
            <Text style={styles.roleDescription}>Manage fleet</Text>
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Safe • Reliable • Affordable</Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.white,
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    alignItems: 'center',
    backgroundColor: Colors.primary,
  },
  logoContainer: {
    alignItems: 'center',
    width: '100%',
  },
  logo: {
    width: 280,
    height: 180,
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 16,
  },
  tagline: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 8,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
    paddingBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: Colors.textLight,
    textAlign: 'center',
    marginBottom: 40,
  },
  buttonContainer: {
    gap: 12,
  },
  roleCard: {
    backgroundColor: Colors.white,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    borderWidth: 2,
  },
  customerCard: {
    borderColor: Colors.primary,
  },
  driverCard: {
    borderColor: Colors.secondary,
  },
  adminCard: {
    borderColor: Colors.gray,
  },
  adminIconCircle: {
    backgroundColor: Colors.lightGray,
  },
  iconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.lightGray,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  roleTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 4,
  },
  roleDescription: {
    fontSize: 14,
    color: Colors.textLight,
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: Colors.textLight,
  },
});