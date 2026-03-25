import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Colors } from '../../utils/colors';
import { sendOTP, verifyOTP } from '../../utils/api';
import { useAuthStore } from '../../store/authStore';
import { Ionicons } from '@expo/vector-icons';

export default function LoginScreen() {
  const router = useRouter();
  const { role } = useLocalSearchParams();
  const { setUser } = useAuthStore();

  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSendOTP = async () => {
    if (phone.length !== 10) {
      Alert.alert('Error', 'Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    try {
      const response = await sendOTP(phone, role as string);
      if (response.data.success) {
        setOtpSent(true);
        Alert.alert('Success', `OTP sent to ${phone}\nUse: 123456 (Mock OTP)`);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (otp.length !== 6) {
      Alert.alert('Error', 'Please enter a valid 6-digit OTP');
      return;
    }

    setLoading(true);
    try {
      const response = await verifyOTP(phone, otp, role as string);
      if (response.data.success) {
        if (response.data.new_user) {
          // Navigate to registration
          if (role === 'customer') {
            router.replace(`/auth/register-customer?phone=${phone}`);
          } else {
            router.replace(`/auth/register-driver?phone=${phone}`);
          }
        } else {
          // User exists, login
          await setUser(response.data.user);
          if (role === 'customer') {
            router.replace('/customer/home');
          } else {
            router.replace('/driver/dashboard');
          }
        }
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Ionicons
            name={role === 'customer' ? 'person-circle' : 'car'}
            size={80}
            color={role === 'customer' ? Colors.primary : Colors.secondary}
          />
          <Text style={styles.title}>
            {role === 'customer' ? 'Customer' : 'Driver'} Login
          </Text>
          <Text style={styles.subtitle}>Enter your phone number to continue</Text>
        </View>

        <View style={styles.form}>
          <Input
            label="Phone Number"
            placeholder="Enter 10-digit phone number"
            keyboardType="phone-pad"
            maxLength={10}
            value={phone}
            onChangeText={setPhone}
            editable={!otpSent}
          />

          {otpSent && (
            <Input
              label="OTP"
              placeholder="Enter 6-digit OTP"
              keyboardType="number-pad"
              maxLength={6}
              value={otp}
              onChangeText={setOtp}
            />
          )}

          {!otpSent ? (
            <Button
              title="Send OTP"
              onPress={handleSendOTP}
              loading={loading}
              variant={role === 'customer' ? 'primary' : 'secondary'}
            />
          ) : (
            <View style={styles.buttonGroup}>
              <Button
                title="Verify OTP"
                onPress={handleVerifyOTP}
                loading={loading}
                variant={role === 'customer' ? 'primary' : 'secondary'}
              />
              <Button
                title="Resend OTP"
                onPress={handleSendOTP}
                variant="outline"
                style={styles.resendButton}
              />
            </View>
          )}

          <Button
            title="Back"
            onPress={() => router.back()}
            variant="outline"
            style={styles.backButton}
          />
        </View>

        <View style={styles.infoBox}>
          <Ionicons name="information-circle" size={20} color={Colors.primary} />
          <Text style={styles.infoText}>Mock OTP: 123456</Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.white,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    paddingTop: 60,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 16,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 8,
    textAlign: 'center',
  },
  form: {
    marginBottom: 24,
  },
  buttonGroup: {
    gap: 12,
  },
  resendButton: {
    marginTop: 8,
  },
  backButton: {
    marginTop: 16,
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.lightGray,
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  infoText: {
    fontSize: 14,
    color: Colors.textLight,
  },
});