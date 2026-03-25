import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Colors } from '../../utils/colors';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';

const UPI_NUMBER = "9876543210@upi"; // Static UPI for payment

export default function SimpleDriverRegistration() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1); // 1, 2, or 3

  // Step 1: Basic Info
  const [fullName, setFullName] = useState('');
  const [drivingExperience, setDrivingExperience] = useState('');
  const [vehicleType, setVehicleType] = useState<'sedan' | 'suv'>('sedan');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');

  // Step 2: Documents
  const [licenseFront, setLicenseFront] = useState('');
  const [licenseBack, setLicenseBack] = useState('');
  const [rcFront, setRcFront] = useState('');
  const [rcBack, setRcBack] = useState('');
  const [insurance, setInsurance] = useState('');
  const [driverPhoto, setDriverPhoto] = useState('');

  // Step 3: Payment & Agreement
  const [paymentScreenshot, setPaymentScreenshot] = useState('');
  const [agreementAccepted, setAgreementAccepted] = useState(false);
  const [signedAgreement, setSignedAgreement] = useState('');

  // File picker function (gallery only, no camera)
  const pickImage = async (setter: (value: string) => void) => {
    try {
      // For web, use a simple placeholder
      if (Platform.OS === 'web') {
        const placeholder = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
        setter(placeholder);
        Alert.alert('Success', 'File selected (web mock)');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        setter(`data:image/jpeg;base64,${result.assets[0].base64}`);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    }
  };

  // Validation
  const validateStep1 = () => {
    if (!fullName.trim()) {
      Alert.alert('Error', 'Please enter your full name');
      return false;
    }
    if (!drivingExperience || parseInt(drivingExperience) < 1) {
      Alert.alert('Error', 'Please enter valid driving experience (min 1 year)');
      return false;
    }
    if (!vehicleNumber.trim() || vehicleNumber.length < 6) {
      Alert.alert('Error', 'Please enter valid vehicle number');
      return false;
    }
    if (!vehicleModel.trim()) {
      Alert.alert('Error', 'Please enter vehicle model');
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (!licenseFront || !licenseBack) {
      Alert.alert('Error', 'Please upload both sides of Driving License');
      return false;
    }
    if (!rcFront || !rcBack) {
      Alert.alert('Error', 'Please upload both sides of RC Book');
      return false;
    }
    if (!insurance) {
      Alert.alert('Error', 'Please upload Insurance document');
      return false;
    }
    if (!driverPhoto) {
      Alert.alert('Error', 'Please upload your photo');
      return false;
    }
    return true;
  };

  const validateStep3 = () => {
    if (!paymentScreenshot) {
      Alert.alert('Error', 'Please upload payment screenshot');
      return false;
    }
    if (!agreementAccepted) {
      Alert.alert('Error', 'Please accept the terms and conditions');
      return false;
    }
    if (!signedAgreement) {
      Alert.alert('Error', 'Please upload signed agreement');
      return false;
    }
    return true;
  };

  const handleNext = () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    } else if (currentStep === 2 && validateStep2()) {
      setCurrentStep(3);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep3()) return;

    setLoading(true);
    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

      const payload = {
        phone: phone as string,
        full_name: fullName,
        driving_experience: parseInt(drivingExperience),
        vehicle_type: vehicleType,
        vehicle_number: vehicleNumber.toUpperCase(),
        vehicle_model: vehicleModel,
        documents: {
          license_front: licenseFront,
          license_back: licenseBack,
          rc_front: rcFront,
          rc_back: rcBack,
          insurance: insurance,
          driver_photo: driverPhoto,
        },
        payment: {
          amount: 500,
          screenshot: paymentScreenshot,
        },
        agreement: {
          accepted: agreementAccepted,
          signed_document: signedAgreement,
          accepted_at: new Date().toISOString(),
        },
      };

      const response = await fetch(`${API_URL}/api/driver/register-simple`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        Alert.alert(
          'Registration Successful!',
          'Your application has been submitted. You will be notified once approved.',
          [{ text: 'OK', onPress: () => router.replace('/auth/login?role=driver') }]
        );
      } else {
        Alert.alert('Error', data.detail || 'Registration failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Upload Button Component
  const UploadButton = ({ 
    label, 
    value, 
    onPress 
  }: { 
    label: string; 
    value: string; 
    onPress: () => void;
  }) => (
    <TouchableOpacity style={styles.uploadBtn} onPress={onPress}>
      <View style={styles.uploadContent}>
        {value ? (
          <>
            <Image source={{ uri: value }} style={styles.uploadPreview} />
            <Ionicons name="checkmark-circle" size={24} color={Colors.success} style={styles.uploadCheck} />
          </>
        ) : (
          <>
            <Ionicons name="cloud-upload" size={32} color={Colors.secondary} />
            <Text style={styles.uploadLabel}>{label}</Text>
            <Text style={styles.uploadHint}>Tap to upload</Text>
          </>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => currentStep > 1 ? setCurrentStep(currentStep - 1) : router.back()}>
          <Ionicons name="arrow-back" size={24} color={Colors.white} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>Driver Registration</Text>
          <Text style={styles.headerSubtitle}>Step {currentStep} of 3</Text>
        </View>
        <View style={{ width: 24 }} />
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        {[1, 2, 3].map((step) => (
          <View
            key={step}
            style={[
              styles.progressStep,
              step <= currentStep && styles.progressStepActive,
            ]}
          />
        ))}
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* STEP 1: Basic Info + Vehicle */}
        {currentStep === 1 && (
          <View>
            <Text style={styles.stepTitle}>Basic Information</Text>

            <Input
              label="Full Name *"
              value={fullName}
              onChangeText={setFullName}
              placeholder="Enter your full name"
            />

            <Input
              label="Mobile Number"
              value={phone as string}
              editable={false}
              placeholder="Mobile number"
            />

            <Input
              label="Driving Experience (Years) *"
              value={drivingExperience}
              onChangeText={setDrivingExperience}
              placeholder="e.g. 5"
              keyboardType="numeric"
            />

            <Text style={styles.sectionTitle}>Vehicle Details</Text>

            <Text style={styles.label}>Vehicle Type *</Text>
            <View style={styles.vehicleTypeRow}>
              <TouchableOpacity
                style={[styles.vehicleTypeBtn, vehicleType === 'sedan' && styles.vehicleTypeBtnActive]}
                onPress={() => setVehicleType('sedan')}
              >
                <Ionicons 
                  name="car-sport" 
                  size={28} 
                  color={vehicleType === 'sedan' ? Colors.white : Colors.text} 
                />
                <Text style={[styles.vehicleTypeText, vehicleType === 'sedan' && styles.vehicleTypeTextActive]}>
                  Sedan
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.vehicleTypeBtn, vehicleType === 'suv' && styles.vehicleTypeBtnActive]}
                onPress={() => setVehicleType('suv')}
              >
                <Ionicons 
                  name="car" 
                  size={28} 
                  color={vehicleType === 'suv' ? Colors.white : Colors.text} 
                />
                <Text style={[styles.vehicleTypeText, vehicleType === 'suv' && styles.vehicleTypeTextActive]}>
                  SUV
                </Text>
              </TouchableOpacity>
            </View>

            <Input
              label="Vehicle Number *"
              value={vehicleNumber}
              onChangeText={setVehicleNumber}
              placeholder="e.g. TN01AB1234"
              autoCapitalize="characters"
            />

            <Input
              label="Vehicle Model *"
              value={vehicleModel}
              onChangeText={setVehicleModel}
              placeholder="e.g. Swift Dzire"
            />

            <Button
              title="Next: Upload Documents"
              onPress={handleNext}
              variant="secondary"
              style={styles.nextBtn}
            />
          </View>
        )}

        {/* STEP 2: Document Uploads */}
        {currentStep === 2 && (
          <View>
            <Text style={styles.stepTitle}>Upload Documents</Text>
            <Text style={styles.stepHint}>Tap each box to upload from gallery</Text>

            <Text style={styles.docLabel}>Driving License</Text>
            <View style={styles.uploadRow}>
              <UploadButton
                label="Front Side"
                value={licenseFront}
                onPress={() => pickImage(setLicenseFront)}
              />
              <UploadButton
                label="Back Side"
                value={licenseBack}
                onPress={() => pickImage(setLicenseBack)}
              />
            </View>

            <Text style={styles.docLabel}>RC Book</Text>
            <View style={styles.uploadRow}>
              <UploadButton
                label="Front Side"
                value={rcFront}
                onPress={() => pickImage(setRcFront)}
              />
              <UploadButton
                label="Back Side"
                value={rcBack}
                onPress={() => pickImage(setRcBack)}
              />
            </View>

            <Text style={styles.docLabel}>Insurance</Text>
            <View style={styles.uploadRow}>
              <UploadButton
                label="Insurance Document"
                value={insurance}
                onPress={() => pickImage(setInsurance)}
              />
            </View>

            <Text style={styles.docLabel}>Your Photo</Text>
            <View style={styles.uploadRow}>
              <UploadButton
                label="Upload Photo"
                value={driverPhoto}
                onPress={() => pickImage(setDriverPhoto)}
              />
            </View>

            <View style={styles.buttonRow}>
              <Button
                title="Back"
                onPress={() => setCurrentStep(1)}
                variant="outline"
                style={styles.halfBtn}
              />
              <Button
                title="Next: Payment"
                onPress={handleNext}
                variant="secondary"
                style={styles.halfBtn}
              />
            </View>
          </View>
        )}

        {/* STEP 3: Payment & Agreement */}
        {currentStep === 3 && (
          <View>
            <Text style={styles.stepTitle}>Payment & Agreement</Text>

            {/* Payment Section */}
            <View style={styles.paymentCard}>
              <Text style={styles.paymentTitle}>Registration Fee</Text>
              <Text style={styles.paymentAmount}>₹500</Text>
              <Text style={styles.paymentHint}>(Non-refundable)</Text>
              
              <View style={styles.upiBox}>
                <Text style={styles.upiLabel}>Pay to UPI:</Text>
                <Text style={styles.upiNumber}>{UPI_NUMBER}</Text>
              </View>

              <Text style={styles.uploadInstruction}>Upload Payment Screenshot</Text>
              <UploadButton
                label="Payment Screenshot"
                value={paymentScreenshot}
                onPress={() => pickImage(setPaymentScreenshot)}
              />
            </View>

            {/* Agreement Section */}
            <View style={styles.agreementCard}>
              <Text style={styles.agreementTitle}>Driver Agreement</Text>
              
              <View style={styles.agreementTerms}>
                <Text style={styles.termText}>• Minimum wallet balance: ₹1000</Text>
                <Text style={styles.termText}>• Trip cancellation penalty: ₹500</Text>
                <Text style={styles.termText}>• Must follow all platform rules</Text>
                <Text style={styles.termText}>• Account may be blocked for violations</Text>
              </View>

              <TouchableOpacity
                style={styles.checkboxRow}
                onPress={() => setAgreementAccepted(!agreementAccepted)}
              >
                <View style={[styles.checkbox, agreementAccepted && styles.checkboxChecked]}>
                  {agreementAccepted && <Ionicons name="checkmark" size={18} color={Colors.white} />}
                </View>
                <Text style={styles.checkboxLabel}>
                  I accept all Terms and Conditions *
                </Text>
              </TouchableOpacity>

              <Text style={styles.uploadInstruction}>Upload Signed Agreement</Text>
              <UploadButton
                label="Signed Agreement"
                value={signedAgreement}
                onPress={() => pickImage(setSignedAgreement)}
              />
            </View>

            <View style={styles.buttonRow}>
              <Button
                title="Back"
                onPress={() => setCurrentStep(2)}
                variant="outline"
                style={styles.halfBtn}
              />
              <Button
                title="Submit"
                onPress={handleSubmit}
                loading={loading}
                variant="secondary"
                style={styles.halfBtn}
              />
            </View>
          </View>
        )}

        <View style={{ height: 40 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: Colors.secondary,
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
  },
  headerCenter: {
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.white,
  },
  headerSubtitle: {
    fontSize: 13,
    color: Colors.white,
    opacity: 0.9,
    marginTop: 2,
  },
  progressContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: Colors.white,
    gap: 8,
  },
  progressStep: {
    flex: 1,
    height: 4,
    backgroundColor: Colors.lightGray,
    borderRadius: 2,
  },
  progressStepActive: {
    backgroundColor: Colors.secondary,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 8,
  },
  stepHint: {
    fontSize: 13,
    color: Colors.textLight,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 24,
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 8,
  },
  vehicleTypeRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  vehicleTypeBtn: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: Colors.border,
    backgroundColor: Colors.white,
  },
  vehicleTypeBtnActive: {
    backgroundColor: Colors.secondary,
    borderColor: Colors.secondary,
  },
  vehicleTypeText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  vehicleTypeTextActive: {
    color: Colors.white,
  },
  nextBtn: {
    marginTop: 24,
  },
  docLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: Colors.text,
    marginTop: 16,
    marginBottom: 10,
  },
  uploadRow: {
    flexDirection: 'row',
    gap: 12,
  },
  uploadBtn: {
    flex: 1,
    minHeight: 100,
    backgroundColor: Colors.white,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: Colors.border,
    borderStyle: 'dashed',
    overflow: 'hidden',
  },
  uploadContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
  },
  uploadPreview: {
    width: '100%',
    height: 80,
    borderRadius: 8,
  },
  uploadCheck: {
    position: 'absolute',
    top: 4,
    right: 4,
  },
  uploadLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.text,
    marginTop: 8,
    textAlign: 'center',
  },
  uploadHint: {
    fontSize: 11,
    color: Colors.textLight,
    marginTop: 2,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
  },
  halfBtn: {
    flex: 1,
  },
  paymentCard: {
    backgroundColor: Colors.white,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
  },
  paymentTitle: {
    fontSize: 14,
    color: Colors.textLight,
  },
  paymentAmount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: Colors.secondary,
    marginVertical: 4,
  },
  paymentHint: {
    fontSize: 12,
    color: Colors.gray,
    marginBottom: 16,
  },
  upiBox: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    marginBottom: 16,
  },
  upiLabel: {
    fontSize: 12,
    color: Colors.textLight,
  },
  upiNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 4,
  },
  uploadInstruction: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.text,
    marginTop: 12,
    marginBottom: 8,
    alignSelf: 'flex-start',
  },
  agreementCard: {
    backgroundColor: Colors.white,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
  },
  agreementTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 12,
  },
  agreementTerms: {
    backgroundColor: '#fff8e1',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  termText: {
    fontSize: 13,
    color: Colors.text,
    marginBottom: 4,
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: Colors.secondary,
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: Colors.secondary,
  },
  checkboxLabel: {
    flex: 1,
    fontSize: 14,
    color: Colors.text,
  },
});
