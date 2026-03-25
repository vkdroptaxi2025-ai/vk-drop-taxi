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
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Colors } from '../../utils/colors';
import { sendOTP, verifyOTP } from '../../utils/api';
import { useAuthStore } from '../../store/authStore';
import { Ionicons } from '@expo/vector-icons';

export default function AdminLoginScreen() {
  const router = useRouter();
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
      const response = await sendOTP(phone, 'admin');
      if (response.data.success) {
        setOtpSent(true);
        Alert.alert('OTP Sent', `OTP sent to ${phone}\nUse: 123456 (Mock)`);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to send OTP');
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
      const response = await verifyOTP(phone, otp, 'admin');
      if (response.data.success) {
        await setUser({ ...response.data.user, role: 'admin' });
        router.replace('/admin/dashboard');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Verification failed';
      if (errorMessage === 'Access Denied') {
        Alert.alert('Access Denied', 'You are not authorized to access the admin panel.');
      } else {
        Alert.alert('Error', errorMessage);
      }
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
          >
            {/* Header */}
            <View style={styles.header}>
              <View style={styles.iconContainer}>
                <Ionicons name="shield-checkmark" size={48} color={Colors.gold} />
              </View>
              <Text style={styles.title}>Admin Access</Text>
              <Text style={styles.subtitle}>Restricted Area - Authorized Personnel Only</Text>
            </View>

            {/* Login Card */}
            <View style={styles.card}>
              <Input
                label="Admin Mobile Number"
                value={phone}
                onChangeText={setPhone}
                placeholder="Enter 10-digit mobile number"
                keyboardType="phone-pad"
                maxLength={10}
                editable={!otpSent}
                icon={<Ionicons name="call" size={20} color={Colors.gold} />}
              />

              {otpSent && (
                <Input
                  label="OTP"
                  value={otp}
                  onChangeText={setOtp}
                  placeholder="Enter 6-digit OTP"
                  keyboardType="number-pad"
                  maxLength={6}
                  icon={<Ionicons name="key" size={20} color={Colors.gold} />}
                />
              )}

              {!otpSent ? (
                <Button
                  title="Send OTP"
                  onPress={handleSendOTP}
                  loading={loading}
                  variant="gold"
                />
              ) : (
                <View style={styles.buttonGroup}>
                  <Button
                    title="Verify & Login"
                    onPress={handleVerifyOTP}
                    loading={loading}
                    variant="gold"
                  />
                  <Button
                    title="Change Number"
                    onPress={() => {
                      setOtpSent(false);
                      setOtp('');
                    }}
                    variant="outline"
                    style={styles.changeButton}
                  />
                </View>
              )}
            </View>

            {/* Warning */}
            <View style={styles.warningContainer}>
              <Ionicons name="warning" size={20} color={Colors.warning} />
              <Text style={styles.warningText}>
                Unauthorized access attempts are logged and monitored.
              </Text>
            </View>

            {/* Back Button */}
            <Button
              title="Back to Home"
              onPress={() => router.back()}
              variant="outline"
              style={styles.backButton}
            />
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
    paddingTop: 80,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  iconContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: Colors.borderGold,
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.gold,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.error,
    textAlign: 'center',
  },
  card: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  buttonGroup: {
    gap: 12,
  },
  changeButton: {
    marginTop: 8,
  },
  warningContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
    gap: 8,
    padding: 16,
    backgroundColor: 'rgba(255, 179, 0, 0.1)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.warning,
  },
  warningText: {
    fontSize: 12,
    color: Colors.warning,
    flex: 1,
  },
  backButton: {
    marginTop: 24,
  },
});
