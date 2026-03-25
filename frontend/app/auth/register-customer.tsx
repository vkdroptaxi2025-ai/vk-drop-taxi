import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  Image,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Colors } from '../../utils/colors';
import { registerCustomer } from '../../utils/api';
import { useAuthStore } from '../../store/authStore';
import { Ionicons } from '@expo/vector-icons';

export default function RegisterCustomerScreen() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const { setUser } = useAuthStore();

  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter your name');
      return;
    }

    if (name.trim().length < 2) {
      Alert.alert('Error', 'Name must be at least 2 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await registerCustomer({
        phone,
        name: name.trim(),
      });

      if (response.data.success) {
        await setUser(response.data.user);
        Alert.alert('Welcome!', 'Registration successful!', [
          { text: 'OK', onPress: () => router.replace('/customer/home') },
        ]);
      }
    } catch (error: any) {
      console.error('Registration Error:', error);
      Alert.alert(
        'Error', 
        error.response?.data?.detail || 'Registration failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1A1A1A', '#0D0D0D', '#000000']}
        style={styles.gradient}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            {/* Logo */}
            <View style={styles.logoContainer}>
              <Image
                source={require('../../assets/images/vk-logo-app.png')}
                style={styles.logo}
                resizeMode="contain"
              />
            </View>

            {/* Title */}
            <Text style={styles.title}>Complete Registration</Text>
            <Text style={styles.subtitle}>Just one more step to get started</Text>

            {/* Form Card */}
            <View style={styles.card}>
              <LinearGradient
                colors={['#2C2C2E', '#1C1C1E']}
                style={styles.cardGradient}
              >
                <View style={styles.phoneDisplay}>
                  <Ionicons name="call" size={20} color={Colors.gold} />
                  <Text style={styles.phoneText}>{phone}</Text>
                  <Ionicons name="checkmark-circle" size={20} color={Colors.greenLight} />
                </View>

                <Input
                  label="Full Name"
                  value={name}
                  onChangeText={setName}
                  placeholder="Enter your full name"
                  autoCapitalize="words"
                  icon={<Ionicons name="person" size={20} color={Colors.gold} />}
                />

                <Button
                  title="Complete Registration"
                  onPress={handleRegister}
                  loading={loading}
                  variant="gold"
                  icon={<Ionicons name="checkmark" size={20} color={Colors.black} />}
                />
              </LinearGradient>
            </View>

            {/* Benefits */}
            <View style={styles.benefitsCard}>
              <Text style={styles.benefitsTitle}>Why VK Drop Taxi?</Text>
              <View style={styles.benefitRow}>
                <Ionicons name="shield-checkmark" size={18} color={Colors.gold} />
                <Text style={styles.benefitText}>Verified & safe drivers</Text>
              </View>
              <View style={styles.benefitRow}>
                <Ionicons name="cash" size={18} color={Colors.gold} />
                <Text style={styles.benefitText}>Lowest fares guaranteed</Text>
              </View>
              <View style={styles.benefitRow}>
                <Ionicons name="time" size={18} color={Colors.gold} />
                <Text style={styles.benefitText}>24/7 availability</Text>
              </View>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
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
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    paddingTop: 60,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  logo: {
    width: 100,
    height: 100,
    borderRadius: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textLight,
    textAlign: 'center',
    marginBottom: 32,
  },
  card: {
    borderRadius: 20,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  cardGradient: {
    padding: 24,
  },
  phoneDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    padding: 16,
    borderRadius: 14,
    marginBottom: 20,
    gap: 12,
  },
  phoneText: {
    flex: 1,
    fontSize: 18,
    fontWeight: '600',
    color: Colors.text,
  },
  benefitsCard: {
    backgroundColor: 'rgba(255, 215, 0, 0.08)',
    borderRadius: 16,
    padding: 20,
    marginTop: 24,
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  benefitsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.gold,
    marginBottom: 16,
    textAlign: 'center',
  },
  benefitRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  benefitText: {
    fontSize: 14,
    color: Colors.text,
  },
});
