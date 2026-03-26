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
import { sendOTP, verifyOTP, getDriverStatusByPhone } from '../../utils/api';
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

  const isDriver = role === 'driver';

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
    } catch (error: any) {
      console.error('Send OTP Error:', error);
      Alert.alert(
        'Error', 
        error.response?.data?.detail || 'Failed to send OTP. Please try again.'
      );
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
        if (role === 'customer') {
          // Customer flow
          if (response.data.new_user) {
            router.replace(`/auth/register-customer?phone=${phone}`);
          } else {
            await setUser(response.data.user);
            router.replace('/customer/home');
          }
        } else {
          // DRIVER FLOW - Check status by phone first
          const statusResponse = await getDriverStatusByPhone(phone);
          console.log('Driver status response:', statusResponse.data);
          
          if (!statusResponse.data.found || statusResponse.data.status === 'NOT_FOUND') {
            // Driver not registered - open registration form
            router.replace(`/auth/driver-onboarding?phone=${phone}`);
          } else if (statusResponse.data.status === 'PENDING') {
            // Driver registered but pending approval
            await setUser({
              driver_id: statusResponse.data.driver_id,
              phone: phone,
              name: statusResponse.data.full_name,
              role: 'driver',
              approval_status: 'pending',
            });
            router.replace('/driver/pending-approval');
          } else if (statusResponse.data.status === 'APPROVED') {
            // Driver approved - open dashboard
            await setUser(response.data.user);
            router.replace('/driver/dashboard');
          } else if (statusResponse.data.status === 'REJECTED') {
            // Driver rejected
            await setUser({
              driver_id: statusResponse.data.driver_id,
              phone: phone,
              name: statusResponse.data.full_name,
              role: 'driver',
              approval_status: 'rejected',
            });
            Alert.alert('Account Rejected', statusResponse.data.rejection_reason || 'Your application was rejected.');
            router.replace('/driver/pending-approval');
          }
        }
      }
    } catch (error: any) {
      console.error('Verify OTP Error:', error);
      Alert.alert(
        'Error', 
        error.response?.data?.detail || 'Invalid OTP. Please try again.'
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
            <Text style={styles.title}>
              {isDriver ? 'Driver Login' : 'Customer Login'}
            </Text>
            <Text style={styles.subtitle}>
              {isDriver 
                ? 'Start earning with VK Drop Taxi' 
                : 'Book your premium ride'
              }
            </Text>

            {/* Login Card */}
            <View style={styles.card}>
              <Input
                label="Mobile Number"
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
                    title="Verify OTP"
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

            {/* Mock OTP Hint */}
            <View style={styles.hintContainer}>
              <Ionicons name="information-circle" size={18} color={Colors.gold} />
              <Text style={styles.hintText}>Mock OTP: 123456</Text>
            </View>

            {/* Benefits for Driver */}
            {isDriver && (
              <View style={styles.benefitsCard}>
                <Text style={styles.benefitsTitle}>Why Join VK Drop Taxi?</Text>
                <View style={styles.benefitRow}>
                  <Ionicons name="cash" size={20} color={Colors.greenLight} />
                  <Text style={styles.benefitText}>Earn ₹15,000 - ₹40,000/month</Text>
                </View>
                <View style={styles.benefitRow}>
                  <Ionicons name="time" size={20} color={Colors.greenLight} />
                  <Text style={styles.benefitText}>Flexible working hours</Text>
                </View>
                <View style={styles.benefitRow}>
                  <Ionicons name="flash" size={20} color={Colors.greenLight} />
                  <Text style={styles.benefitText}>Instant trip assignments</Text>
                </View>
              </View>
            )}

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
    paddingTop: 60,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  logo: {
    width: 120,
    height: 120,
    borderRadius: 60,
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
    backgroundColor: Colors.cardBackground,
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  buttonGroup: {
    gap: 12,
  },
  changeButton: {
    marginTop: 8,
  },
  hintContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    gap: 8,
  },
  hintText: {
    fontSize: 13,
    color: Colors.gold,
  },
  benefitsCard: {
    backgroundColor: 'rgba(46, 125, 50, 0.1)',
    borderRadius: 16,
    padding: 20,
    marginTop: 24,
    borderWidth: 1,
    borderColor: Colors.borderGreen,
  },
  benefitsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.greenLight,
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
  backButton: {
    marginTop: 24,
  },
});
