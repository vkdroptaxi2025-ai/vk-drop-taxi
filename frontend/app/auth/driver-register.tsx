import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Image,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { registerDriver } from '../../utils/api';
import { useAuthStore } from '../../store/authStore';

// Yellow + Green theme colors
const COLORS = {
  primary: '#FFD700',      // Yellow
  secondary: '#2E7D32',    // Green
  background: '#FFFFFF',
  card: '#F8F9FA',
  text: '#1A1A1A',
  textLight: '#666666',
  border: '#E0E0E0',
  error: '#DC3545',
  success: '#28A745',
};

export default function DriverRegistrationForm() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const { setUser } = useAuthStore();
  
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [driverId, setDriverId] = useState<string | null>(null);

  // Form fields
  const [fullName, setFullName] = useState('');
  const [address, setAddress] = useState('');
  const [licenseNumber, setLicenseNumber] = useState('');
  const [licenseImage, setLicenseImage] = useState<string | null>(null);
  const [vehicleType, setVehicleType] = useState<string>('sedan');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [rcBookImage, setRcBookImage] = useState<string | null>(null);
  const [insuranceDetails, setInsuranceDetails] = useState('');
  const [insuranceImage, setInsuranceImage] = useState<string | null>(null);

  // Image picker function
  const pickImage = async (setter: (uri: string) => void, label: string) => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Please allow access to your photo library');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const base64 = result.assets[0].base64;
        if (base64) {
          setter(`data:image/jpeg;base64,${base64}`);
          Alert.alert('Success', `${label} uploaded successfully`);
        }
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    }
  };

  // Form validation
  const validateForm = () => {
    if (!fullName.trim()) {
      Alert.alert('Required', 'Please enter your full name');
      return false;
    }
    if (!address.trim()) {
      Alert.alert('Required', 'Please enter your address');
      return false;
    }
    if (!licenseNumber.trim()) {
      Alert.alert('Required', 'Please enter your driving license number');
      return false;
    }
    if (!licenseImage) {
      Alert.alert('Required', 'Please upload your driving license image');
      return false;
    }
    if (!vehicleNumber.trim()) {
      Alert.alert('Required', 'Please enter your vehicle number');
      return false;
    }
    if (!rcBookImage) {
      Alert.alert('Required', 'Please upload your RC book image');
      return false;
    }
    if (!insuranceDetails.trim()) {
      Alert.alert('Required', 'Please enter your insurance details');
      return false;
    }
    return true;
  };

  // Submit form
  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const data = {
        phone: phone as string,
        full_name: fullName.trim(),
        address: address.trim(),
        driving_license_number: licenseNumber.trim().toUpperCase(),
        driving_license_image: licenseImage,
        vehicle_type: vehicleType,
        vehicle_number: vehicleNumber.trim().toUpperCase(),
        rc_book_image: rcBookImage,
        insurance_details: insuranceDetails.trim(),
        insurance_image: insuranceImage,
      };

      const response = await registerDriver(data);
      
      if (response.data.success) {
        setDriverId(response.data.driver_id);
        setSubmitted(true);
        
        // Save driver info to store
        await setUser({
          driver_id: response.data.driver_id,
          phone: phone as string,
          full_name: fullName,
          role: 'driver',
          approval_status: 'pending',
        });
      }
    } catch (error: any) {
      console.error('Registration error:', error);
      Alert.alert(
        'Registration Failed',
        error.response?.data?.detail || 'Something went wrong. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Success screen after submission
  if (submitted) {
    return (
      <View style={styles.container}>
        <View style={styles.successContainer}>
          <View style={styles.successIcon}>
            <Ionicons name="checkmark-circle" size={80} color={COLORS.success} />
          </View>
          <Text style={styles.successTitle}>Registration Submitted!</Text>
          <Text style={styles.successMessage}>
            Your application has been submitted successfully.
          </Text>
          <View style={styles.statusCard}>
            <Ionicons name="time-outline" size={24} color={COLORS.primary} />
            <View style={styles.statusTextContainer}>
              <Text style={styles.statusLabel}>Current Status</Text>
              <Text style={styles.statusValue}>PENDING APPROVAL</Text>
            </View>
          </View>
          <Text style={styles.infoText}>
            Admin will review your documents and approve your account.
            You will be notified once approved.
          </Text>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => router.replace('/driver/pending-approval')}
          >
            <Text style={styles.primaryButtonText}>Check Status</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => router.replace('/')}
          >
            <Text style={styles.secondaryButtonText}>Back to Home</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Upload button component
  const UploadButton = ({ 
    label, 
    value, 
    onPress 
  }: { 
    label: string; 
    value: string | null; 
    onPress: () => void;
  }) => (
    <TouchableOpacity 
      style={[styles.uploadButton, value && styles.uploadButtonDone]}
      onPress={onPress}
    >
      {value ? (
        <View style={styles.uploadDoneContent}>
          <Image source={{ uri: value }} style={styles.uploadPreview} />
          <View style={styles.uploadCheckmark}>
            <Ionicons name="checkmark-circle" size={24} color={COLORS.success} />
          </View>
          <Text style={styles.uploadDoneText}>Uploaded</Text>
        </View>
      ) : (
        <View style={styles.uploadContent}>
          <Ionicons name="cloud-upload-outline" size={32} color={COLORS.secondary} />
          <Text style={styles.uploadLabel}>{label}</Text>
          <Text style={styles.uploadHint}>Tap to upload from gallery</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color={COLORS.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Driver Registration</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Personal Information */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Personal Information</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Full Name *</Text>
              <TextInput
                style={styles.input}
                value={fullName}
                onChangeText={setFullName}
                placeholder="Enter your full name"
                placeholderTextColor={COLORS.textLight}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Mobile Number</Text>
              <View style={[styles.input, styles.inputDisabled]}>
                <Text style={styles.inputText}>{phone}</Text>
                <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Address *</Text>
              <TextInput
                style={[styles.input, styles.inputMultiline]}
                value={address}
                onChangeText={setAddress}
                placeholder="Enter your complete address"
                placeholderTextColor={COLORS.textLight}
                multiline
                numberOfLines={2}
              />
            </View>
          </View>

          {/* Driving License */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Driving License</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>License Number *</Text>
              <TextInput
                style={styles.input}
                value={licenseNumber}
                onChangeText={setLicenseNumber}
                placeholder="e.g. TN01 2020 0012345"
                placeholderTextColor={COLORS.textLight}
                autoCapitalize="characters"
              />
            </View>

            <Text style={styles.inputLabel}>Upload License *</Text>
            <UploadButton
              label="Upload Driving License"
              value={licenseImage}
              onPress={() => pickImage(setLicenseImage, 'Driving License')}
            />
          </View>

          {/* Vehicle Details */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Vehicle Details</Text>
            
            <Text style={styles.inputLabel}>Vehicle Type *</Text>
            <View style={styles.vehicleTypeContainer}>
              {['sedan', 'suv', 'crysta'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.vehicleTypeButton,
                    vehicleType === type && styles.vehicleTypeButtonActive
                  ]}
                  onPress={() => setVehicleType(type)}
                >
                  <Ionicons 
                    name={type === 'sedan' ? 'car-sport' : 'car'} 
                    size={24} 
                    color={vehicleType === type ? COLORS.background : COLORS.secondary}
                  />
                  <Text style={[
                    styles.vehicleTypeText,
                    vehicleType === type && styles.vehicleTypeTextActive
                  ]}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Vehicle Number *</Text>
              <TextInput
                style={styles.input}
                value={vehicleNumber}
                onChangeText={setVehicleNumber}
                placeholder="e.g. TN01AB1234"
                placeholderTextColor={COLORS.textLight}
                autoCapitalize="characters"
              />
            </View>

            <Text style={styles.inputLabel}>Upload RC Book *</Text>
            <UploadButton
              label="Upload RC Book"
              value={rcBookImage}
              onPress={() => pickImage(setRcBookImage, 'RC Book')}
            />
          </View>

          {/* Insurance */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Insurance</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Insurance Details *</Text>
              <TextInput
                style={[styles.input, styles.inputMultiline]}
                value={insuranceDetails}
                onChangeText={setInsuranceDetails}
                placeholder="Enter policy number and validity"
                placeholderTextColor={COLORS.textLight}
                multiline
                numberOfLines={2}
              />
            </View>

            <Text style={styles.inputLabel}>Upload Insurance (Optional)</Text>
            <UploadButton
              label="Upload Insurance Document"
              value={insuranceImage}
              onPress={() => pickImage(setInsuranceImage, 'Insurance')}
            />
          </View>

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, loading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={COLORS.text} />
            ) : (
              <>
                <Text style={styles.submitButtonText}>Submit Registration</Text>
                <Ionicons name="arrow-forward" size={20} color={COLORS.text} />
              </>
            )}
          </TouchableOpacity>

          <Text style={styles.disclaimer}>
            By submitting, you agree to our terms and conditions.
            Your documents will be verified by our team.
          </Text>

          <View style={{ height: 40 }} />
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: COLORS.primary,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  section: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 16,
    paddingBottom: 8,
    borderBottomWidth: 2,
    borderBottomColor: COLORS.primary,
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  input: {
    backgroundColor: COLORS.background,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: COLORS.text,
  },
  inputMultiline: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  inputDisabled: {
    backgroundColor: '#F0F0F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  inputText: {
    fontSize: 16,
    color: COLORS.textLight,
  },
  vehicleTypeContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  vehicleTypeButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: COLORS.border,
    backgroundColor: COLORS.background,
  },
  vehicleTypeButtonActive: {
    backgroundColor: COLORS.secondary,
    borderColor: COLORS.secondary,
  },
  vehicleTypeText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.secondary,
    marginTop: 4,
  },
  vehicleTypeTextActive: {
    color: COLORS.background,
  },
  uploadButton: {
    backgroundColor: COLORS.background,
    borderWidth: 2,
    borderColor: COLORS.border,
    borderStyle: 'dashed',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 140,
  },
  uploadButtonDone: {
    borderColor: COLORS.success,
    borderStyle: 'solid',
  },
  uploadContent: {
    alignItems: 'center',
  },
  uploadLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginTop: 12,
  },
  uploadHint: {
    fontSize: 12,
    color: COLORS.textLight,
    marginTop: 4,
  },
  uploadDoneContent: {
    alignItems: 'center',
    position: 'relative',
  },
  uploadPreview: {
    width: 100,
    height: 75,
    borderRadius: 8,
  },
  uploadCheckmark: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: COLORS.background,
    borderRadius: 12,
  },
  uploadDoneText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.success,
    marginTop: 8,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    borderRadius: 14,
    marginTop: 8,
    gap: 8,
  },
  submitButtonDisabled: {
    opacity: 0.7,
  },
  submitButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  disclaimer: {
    fontSize: 12,
    color: COLORS.textLight,
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 18,
  },
  // Success screen styles
  successContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: COLORS.background,
  },
  successIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(40, 167, 69, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 12,
  },
  successMessage: {
    fontSize: 16,
    color: COLORS.textLight,
    textAlign: 'center',
    marginBottom: 24,
  },
  statusCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  statusTextContainer: {
    marginLeft: 12,
  },
  statusLabel: {
    fontSize: 12,
    color: COLORS.textLight,
  },
  statusValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  infoText: {
    fontSize: 14,
    color: COLORS.textLight,
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 22,
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 12,
    marginBottom: 12,
    width: '100%',
    alignItems: 'center',
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: COLORS.secondary,
    width: '100%',
    alignItems: 'center',
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.secondary,
  },
});
