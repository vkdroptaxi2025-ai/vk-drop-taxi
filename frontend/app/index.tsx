import React, { useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  Image, 
  ScrollView,
  Animated,
  Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Colors } from '../utils/colors';
import { useAuthStore } from '../store/authStore';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

export default function WelcomeScreen() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const glowAnim = new Animated.Value(0.5);

  useEffect(() => {
    // Logo glow animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(glowAnim, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: false,
        }),
        Animated.timing(glowAnim, {
          toValue: 0.5,
          duration: 1500,
          useNativeDriver: false,
        }),
      ])
    ).start();

    // Redirect if already logged in
    if (isAuthenticated && user) {
      if (user.role === 'customer') {
        router.replace('/customer/home');
      } else if (user.role === 'driver') {
        router.replace('/driver/dashboard');
      } else if (user.role === 'admin') {
        router.replace('/admin/dashboard');
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
      <LinearGradient
        colors={['#1A1A1A', '#0D0D0D', '#000000']}
        style={styles.gradient}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Logo Section with Glow */}
          <View style={styles.logoSection}>
            <Animated.View 
              style={[
                styles.logoGlow,
                {
                  opacity: glowAnim,
                  transform: [{ scale: glowAnim.interpolate({
                    inputRange: [0.5, 1],
                    outputRange: [1, 1.1],
                  })}],
                }
              ]}
            />
            <Image
              source={require('../assets/images/vk-logo-app.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>

          {/* Brand Text */}
          <Text style={styles.brandName}>VK DROP TAXI</Text>
          <Text style={styles.tagline}>Premium Ride Experience</Text>

          {/* Benefits Banner */}
          <View style={styles.benefitsBanner}>
            <View style={styles.benefitItem}>
              <Ionicons name="shield-checkmark" size={24} color={Colors.gold} />
              <Text style={styles.benefitText}>Safe</Text>
            </View>
            <View style={styles.benefitDivider} />
            <View style={styles.benefitItem}>
              <Ionicons name="wallet" size={24} color={Colors.gold} />
              <Text style={styles.benefitText}>Affordable</Text>
            </View>
            <View style={styles.benefitDivider} />
            <View style={styles.benefitItem}>
              <Ionicons name="time" size={24} color={Colors.gold} />
              <Text style={styles.benefitText}>Reliable</Text>
            </View>
          </View>

          {/* Role Selection */}
          <Text style={styles.selectTitle}>Select Your Role</Text>

          {/* Customer Card */}
          <TouchableOpacity
            style={styles.roleCard}
            onPress={() => handleRoleSelection('customer')}
            activeOpacity={0.9}
          >
            <LinearGradient
              colors={['#2C2C2E', '#1C1C1E']}
              style={styles.roleCardGradient}
            >
              <View style={styles.roleCardContent}>
                <View style={styles.roleIconContainer}>
                  <Ionicons name="person" size={36} color={Colors.gold} />
                </View>
                <View style={styles.roleTextContainer}>
                  <Text style={styles.roleTitle}>Customer</Text>
                  <Text style={styles.roleSubtitle}>Book a premium ride</Text>
                </View>
                <Ionicons name="chevron-forward" size={24} color={Colors.gold} />
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Driver Card */}
          <TouchableOpacity
            style={styles.roleCard}
            onPress={() => handleRoleSelection('driver')}
            activeOpacity={0.9}
          >
            <LinearGradient
              colors={['#1B4D3E', '#0D2818']}
              style={styles.roleCardGradient}
            >
              <View style={styles.roleCardContent}>
                <View style={[styles.roleIconContainer, styles.driverIconContainer]}>
                  <Ionicons name="car-sport" size={36} color={Colors.greenLight} />
                </View>
                <View style={styles.roleTextContainer}>
                  <Text style={styles.roleTitle}>Driver</Text>
                  <Text style={styles.roleSubtitle}>Start earning today</Text>
                </View>
                <Ionicons name="chevron-forward" size={24} color={Colors.greenLight} />
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Driver Benefits Banner */}
          <View style={styles.driverBanner}>
            <LinearGradient
              colors={['rgba(46, 125, 50, 0.2)', 'rgba(46, 125, 50, 0.05)']}
              style={styles.driverBannerGradient}
            >
              <Text style={styles.driverBannerTitle}>Earn Daily Income</Text>
              <View style={styles.driverBenefitsRow}>
                <View style={styles.driverBenefitItem}>
                  <Ionicons name="cash" size={20} color={Colors.greenLight} />
                  <Text style={styles.driverBenefitText}>Daily Pay</Text>
                </View>
                <View style={styles.driverBenefitItem}>
                  <Ionicons name="time" size={20} color={Colors.greenLight} />
                  <Text style={styles.driverBenefitText}>Flexible Hours</Text>
                </View>
                <View style={styles.driverBenefitItem}>
                  <Ionicons name="flash" size={20} color={Colors.greenLight} />
                  <Text style={styles.driverBenefitText}>Instant Trips</Text>
                </View>
              </View>
            </LinearGradient>
          </View>

          {/* Admin Access */}
          <TouchableOpacity
            style={styles.adminButton}
            onPress={handleAdminAccess}
          >
            <Ionicons name="shield" size={18} color={Colors.textLight} />
            <Text style={styles.adminButtonText}>Admin Access</Text>
          </TouchableOpacity>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>© 2024 VK Drop Taxi</Text>
            <Text style={styles.footerSubtext}>Premium Taxi Service</Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  gradient: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  logoSection: {
    alignItems: 'center',
    marginBottom: 16,
  },
  logoGlow: {
    position: 'absolute',
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: Colors.glowGold,
  },
  logo: {
    width: 160,
    height: 160,
    borderRadius: 80,
  },
  brandName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.gold,
    textAlign: 'center',
    letterSpacing: 3,
  },
  tagline: {
    fontSize: 14,
    color: Colors.textLight,
    textAlign: 'center',
    marginTop: 4,
    letterSpacing: 1,
  },
  benefitsBanner: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 32,
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: 'rgba(255, 215, 0, 0.08)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  benefitItem: {
    alignItems: 'center',
    flex: 1,
  },
  benefitText: {
    fontSize: 12,
    color: Colors.text,
    marginTop: 6,
    fontWeight: '600',
  },
  benefitDivider: {
    width: 1,
    height: 30,
    backgroundColor: Colors.borderGold,
  },
  selectTitle: {
    fontSize: 16,
    color: Colors.textLight,
    textAlign: 'center',
    marginBottom: 16,
    letterSpacing: 1,
  },
  roleCard: {
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  roleCardGradient: {
    padding: 20,
  },
  roleCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  roleIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(255, 215, 0, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: Colors.borderGold,
  },
  driverIconContainer: {
    backgroundColor: 'rgba(76, 175, 80, 0.15)',
    borderColor: Colors.borderGreen,
  },
  roleTextContainer: {
    flex: 1,
    marginLeft: 16,
  },
  roleTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  roleSubtitle: {
    fontSize: 13,
    color: Colors.textLight,
    marginTop: 4,
  },
  driverBanner: {
    marginTop: 8,
    marginBottom: 24,
    borderRadius: 12,
    overflow: 'hidden',
  },
  driverBannerGradient: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.borderGreen,
  },
  driverBannerTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.greenLight,
    textAlign: 'center',
    marginBottom: 12,
  },
  driverBenefitsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  driverBenefitItem: {
    alignItems: 'center',
  },
  driverBenefitText: {
    fontSize: 11,
    color: Colors.text,
    marginTop: 4,
  },
  adminButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    gap: 8,
  },
  adminButtonText: {
    fontSize: 14,
    color: Colors.textLight,
  },
  footer: {
    alignItems: 'center',
    marginTop: 24,
  },
  footerText: {
    fontSize: 12,
    color: Colors.textLight,
  },
  footerSubtext: {
    fontSize: 10,
    color: Colors.gray,
    marginTop: 2,
  },
});
