import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
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

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Ionicons name="car-sport" size={60} color={Colors.primary} />
          <Text style={styles.appName}>VK Drop Taxi</Text>
          <Text style={styles.tagline}>Your Reliable Ride Partner</Text>
        </View>
      </View>

      {/* Role Selection */}
      <View style={styles.content}>
        <Text style={styles.title}>Welcome!</Text>
        <Text style={styles.subtitle}>Select your role to continue</Text>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.roleCard, styles.customerCard]}
            onPress={() => handleRoleSelection('customer')}
            activeOpacity={0.8}
          >
            <View style={styles.iconCircle}>
              <Ionicons name="person" size={40} color={Colors.primary} />
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
              <Ionicons name="car" size={40} color={Colors.secondary} />
            </View>
            <Text style={styles.roleTitle}>Driver</Text>
            <Text style={styles.roleDescription}>Start earning</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>Safe • Reliable • Affordable</Text>
      </View>
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
    backgroundColor: Colors.lightGray,
  },
  logoContainer: {
    alignItems: 'center',
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
    gap: 20,
  },
  roleCard: {
    backgroundColor: Colors.white,
    borderRadius: 20,
    padding: 30,
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
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.lightGray,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  roleTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 8,
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