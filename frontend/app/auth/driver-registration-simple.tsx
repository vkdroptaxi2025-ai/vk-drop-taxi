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
  TextInput,
} from 'react-native';
import * as ExpoClipboard from 'expo-clipboard';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Colors } from '../../utils/colors';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { LinearGradient } from 'expo-linear-gradient';

const UPI_ID = "9345538164@ybl";
const REGISTRATION_FEE = 500;

export default function SimpleDriverRegistration() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [copiedUPI, setCopiedUPI] = useState(false);
  const [submitted, setSubmitted] = useState(false);

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

  // Copy UPI to clipboard
  const copyUPI = async () => {
    try {
      await ExpoClipboard.setStringAsync(UPI_ID);
      setCopiedUPI(true);
      setTimeout(() => setCopiedUPI(false), 2000);
      Alert.alert('Copied!', 'UPI ID copied to clipboard');
    } catch (error) {
      Alert.alert('Error', 'Failed to copy UPI ID');
    }
  };

  // File picker function
  const pickImage = async (setter: (value: string) => void, label: string) => {
    try {
      if (Platform.OS === 'web') {
        const placeholder = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
        setter(placeholder);
        Alert.alert('Success', `${label} uploaded successfully!`);
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
        Alert.alert('Success', `${label} uploaded successfully!`);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    }
  };

  // Validation functions
  const validateStep1 = () => {
    if (!fullName.trim()) {
      Alert.alert('Required', 'Please enter your full name');
      return false;
    }
    if (!drivingExperience || parseInt(drivingExperience) < 1) {
      Alert.alert('Required', 'Please enter valid driving experience (min 1 year)');
      return false;
    }
    if (!vehicleNumber.trim() || vehicleNumber.length < 6) {
      Alert.alert('Required', 'Please enter valid vehicle number');
      return false;
    }
    if (!vehicleModel.trim()) {
      Alert.alert('Required', 'Please enter vehicle model');
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (!licenseFront || !licenseBack) {
      Alert.alert('Required', 'Please upload both sides of Driving License');
      return false;
    }
    if (!rcFront || !rcBack) {
      Alert.alert('Required', 'Please upload both sides of RC Book');
      return false;
    }
    if (!insurance) {
      Alert.alert('Required', 'Please upload Insurance document');
      return false;
    }
    if (!driverPhoto) {
      Alert.alert('Required', 'Please upload your photo');
      return false;
    }
    return true;
  };

  const validateStep3 = () => {
    if (!paymentScreenshot) {
      Alert.alert('Required', 'Please upload payment screenshot');
      return false;
    }
    if (!agreementAccepted) {
      Alert.alert('Required', 'Please accept the terms and conditions');
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
          amount: REGISTRATION_FEE,
          screenshot: paymentScreenshot,
        },
        agreement: {
          accepted: agreementAccepted,
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
        setSubmitted(true);
      } else {
        Alert.alert('Error', data.detail || 'Registration failed. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  // Success Screen
  if (submitted) {
    return (
      <View style={styles.container}>
        <LinearGradient
          colors={[Colors.backgroundGradientStart, Colors.backgroundGradientEnd]}
          style={styles.successContainer}
        >
          <View style={styles.successIcon}>
            <Ionicons name="checkmark-circle" size={80} color={Colors.success} />
          </View>
          <Text style={styles.successTitle}>Registration Submitted!</Text>
          <Text style={styles.successMessage}>
            Your application is under review.{'\n'}
            You will be notified once approved.
          </Text>
          <Text style={styles.successHint}>
            This usually takes 24-48 hours
          </Text>
          <TouchableOpacity
            style={styles.successButton}
            onPress={() => router.replace('/auth/login?role=driver')}
          >
            <LinearGradient
              colors={[Colors.gradientGoldStart, Colors.gradientGoldEnd]}
              style={styles.successButtonGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
            >
              <Text style={styles.successButtonText}>Back to Login</Text>
            </LinearGradient>
          </TouchableOpacity>
        </LinearGradient>
      </View>
    );
  }

  // Premium Input Component
  const PremiumInput = ({ 
    label, 
    value, 
    onChangeText, 
    placeholder,
    keyboardType = 'default',
    editable = true,
    autoCapitalize = 'sentences'
  }: any) => (
    <View style={styles.inputContainer}>
      <Text style={styles.inputLabel}>{label}</Text>
      <View style={[styles.inputWrapper, !editable && styles.inputDisabled]}>
        <TextInput
          style={styles.textInput}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={Colors.gray}
          editable={editable}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize as any}
        />
      </View>
    </View>
  );

  // Upload Card Component
  const UploadCard = ({ 
    label, 
    value, 
    onPress,
    icon = 'cloud-upload-outline'
  }: { 
    label: string; 
    value: string; 
    onPress: () => void;
    icon?: string;
  }) => (
    <TouchableOpacity 
      style={[styles.uploadCard, value && styles.uploadCardDone]} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      {value ? (
        <View style={styles.uploadDoneContent}>
          <Image source={{ uri: value }} style={styles.uploadPreview} />
          <View style={styles.uploadDoneBadge}>
            <Ionicons name="checkmark-circle" size={20} color={Colors.success} />
          </View>
        </View>
      ) : (
        <View style={styles.uploadContent}>
          <View style={styles.uploadIconWrapper}>
            <Ionicons name={icon as any} size={28} color={Colors.gold} />
          </View>
          <Text style={styles.uploadLabel}>{label}</Text>
          <Text style={styles.uploadHint}>Tap to upload from gallery</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={[Colors.backgroundGradientStart, Colors.backgroundGradientEnd]}
        style={styles.gradient}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => currentStep > 1 ? setCurrentStep(currentStep - 1) : router.back()}
          >
            <Ionicons name="arrow-back" size={24} color={Colors.white} />
          </TouchableOpacity>
          <View style={styles.headerCenter}>
            <Text style={styles.headerTitle}>Driver Registration</Text>
            <Text style={styles.headerSubtitle}>Step {currentStep} of 3</Text>
          </View>
          <View style={{ width: 40 }} />
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

        <KeyboardAvoidingView 
          style={styles.keyboardView}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <ScrollView 
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* STEP 1: Basic Info */}
            {currentStep === 1 && (
              <View style={styles.stepContainer}>
                <Text style={styles.stepTitle}>Basic Information</Text>
                <Text style={styles.stepSubtitle}>Enter your personal & vehicle details</Text>

                <PremiumInput
                  label="Full Name *"
                  value={fullName}
                  onChangeText={setFullName}
                  placeholder="Enter your full name"
                />

                <PremiumInput
                  label="Mobile Number"
                  value={phone as string}
                  editable={false}
                  placeholder="Mobile number"
                />

                <PremiumInput
                  label="Driving Experience (Years) *"
                  value={drivingExperience}
                  onChangeText={setDrivingExperience}
                  placeholder="e.g. 5"
                  keyboardType="numeric"
                />

                <Text style={styles.sectionTitle}>Vehicle Details</Text>

                <Text style={styles.inputLabel}>Vehicle Type *</Text>
                <View style={styles.vehicleTypeRow}>
                  <TouchableOpacity
                    style={[styles.vehicleTypeBtn, vehicleType === 'sedan' && styles.vehicleTypeBtnActive]}
                    onPress={() => setVehicleType('sedan')}
                  >
                    <Ionicons 
                      name="car-sport" 
                      size={32} 
                      color={vehicleType === 'sedan' ? Colors.background : Colors.gold} 
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
                      size={32} 
                      color={vehicleType === 'suv' ? Colors.background : Colors.gold} 
                    />
                    <Text style={[styles.vehicleTypeText, vehicleType === 'suv' && styles.vehicleTypeTextActive]}>
                      SUV
                    </Text>
                  </TouchableOpacity>
                </View>

                <PremiumInput
                  label="Vehicle Number *"
                  value={vehicleNumber}
                  onChangeText={setVehicleNumber}
                  placeholder="e.g. TN01AB1234"
                  autoCapitalize="characters"
                />

                <PremiumInput
                  label="Vehicle Model *"
                  value={vehicleModel}
                  onChangeText={setVehicleModel}
                  placeholder="e.g. Swift Dzire"
                />

                <TouchableOpacity style={styles.primaryButton} onPress={handleNext}>
                  <LinearGradient
                    colors={[Colors.gradientGoldStart, Colors.gradientGoldEnd]}
                    style={styles.buttonGradient}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                  >
                    <Text style={styles.primaryButtonText}>Next: Upload Documents</Text>
                    <Ionicons name="arrow-forward" size={20} color={Colors.background} />
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            )}

            {/* STEP 2: Document Uploads */}
            {currentStep === 2 && (
              <View style={styles.stepContainer}>
                <Text style={styles.stepTitle}>Upload Documents</Text>
                <Text style={styles.stepSubtitle}>Upload clear photos of your documents</Text>

                <Text style={styles.docSectionLabel}>Driving License</Text>
                <View style={styles.uploadRow}>
                  <UploadCard
                    label="Front Side"
                    value={licenseFront}
                    onPress={() => pickImage(setLicenseFront, 'License Front')}
                    icon="card-outline"
                  />
                  <UploadCard
                    label="Back Side"
                    value={licenseBack}
                    onPress={() => pickImage(setLicenseBack, 'License Back')}
                    icon="card-outline"
                  />
                </View>

                <Text style={styles.docSectionLabel}>RC Book</Text>
                <View style={styles.uploadRow}>
                  <UploadCard
                    label="Front Side"
                    value={rcFront}
                    onPress={() => pickImage(setRcFront, 'RC Front')}
                    icon="document-text-outline"
                  />
                  <UploadCard
                    label="Back Side"
                    value={rcBack}
                    onPress={() => pickImage(setRcBack, 'RC Back')}
                    icon="document-text-outline"
                  />
                </View>

                <Text style={styles.docSectionLabel}>Insurance & Photo</Text>
                <View style={styles.uploadRow}>
                  <UploadCard
                    label="Insurance"
                    value={insurance}
                    onPress={() => pickImage(setInsurance, 'Insurance')}
                    icon="shield-checkmark-outline"
                  />
                  <UploadCard
                    label="Your Photo"
                    value={driverPhoto}
                    onPress={() => pickImage(setDriverPhoto, 'Photo')}
                    icon="person-outline"
                  />
                </View>

                <View style={styles.buttonRow}>
                  <TouchableOpacity style={styles.outlineButton} onPress={() => setCurrentStep(1)}>
                    <Ionicons name="arrow-back" size={20} color={Colors.gold} />
                    <Text style={styles.outlineButtonText}>Back</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.primaryButton, { flex: 1 }]} onPress={handleNext}>
                    <LinearGradient
                      colors={[Colors.gradientGoldStart, Colors.gradientGoldEnd]}
                      style={styles.buttonGradient}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                    >
                      <Text style={styles.primaryButtonText}>Next: Payment</Text>
                      <Ionicons name="arrow-forward" size={20} color={Colors.background} />
                    </LinearGradient>
                  </TouchableOpacity>
                </View>
              </View>
            )}

            {/* STEP 3: Payment & Agreement */}
            {currentStep === 3 && (
              <View style={styles.stepContainer}>
                <Text style={styles.stepTitle}>Payment & Agreement</Text>
                <Text style={styles.stepSubtitle}>Complete payment to submit registration</Text>

                {/* Payment Card */}
                <View style={styles.paymentCard}>
                  <View style={styles.paymentHeader}>
                    <Text style={styles.paymentLabel}>Registration Fee</Text>
                    <Text style={styles.paymentAmount}>₹{REGISTRATION_FEE}</Text>
                    <Text style={styles.paymentNote}>(One-time, Non-refundable)</Text>
                  </View>

                  {/* Payment Steps */}
                  <View style={styles.paymentSteps}>
                    <View style={styles.paymentStep}>
                      <View style={styles.stepNumber}>
                        <Text style={styles.stepNumberText}>1</Text>
                      </View>
                      <Text style={styles.stepText}>Pay ₹{REGISTRATION_FEE} via UPI</Text>
                    </View>
                    <View style={styles.paymentStep}>
                      <View style={styles.stepNumber}>
                        <Text style={styles.stepNumberText}>2</Text>
                      </View>
                      <Text style={styles.stepText}>Take screenshot of payment</Text>
                    </View>
                    <View style={styles.paymentStep}>
                      <View style={styles.stepNumber}>
                        <Text style={styles.stepNumberText}>3</Text>
                      </View>
                      <Text style={styles.stepText}>Upload screenshot & submit</Text>
                    </View>
                  </View>

                  {/* UPI ID Box */}
                  <View style={styles.upiContainer}>
                    <Text style={styles.upiTitle}>UPI ID</Text>
                    <View style={styles.upiBox}>
                      <Text style={styles.upiId}>{UPI_ID}</Text>
                      <TouchableOpacity style={styles.copyButton} onPress={copyUPI}>
                        <Ionicons 
                          name={copiedUPI ? "checkmark" : "copy-outline"} 
                          size={20} 
                          color={Colors.background} 
                        />
                        <Text style={styles.copyButtonText}>
                          {copiedUPI ? 'Copied!' : 'Copy'}
                        </Text>
                      </TouchableOpacity>
                    </View>
                  </View>

                  {/* Payment Upload */}
                  <Text style={styles.uploadTitle}>Upload Payment Screenshot</Text>
                  <TouchableOpacity 
                    style={[styles.paymentUploadCard, paymentScreenshot && styles.paymentUploadDone]}
                    onPress={() => pickImage(setPaymentScreenshot, 'Payment Screenshot')}
                  >
                    {paymentScreenshot ? (
                      <View style={styles.paymentUploadDoneContent}>
                        <Image source={{ uri: paymentScreenshot }} style={styles.paymentPreview} />
                        <View style={styles.paymentUploadBadge}>
                          <Ionicons name="checkmark-circle" size={24} color={Colors.success} />
                          <Text style={styles.paymentUploadBadgeText}>Uploaded</Text>
                        </View>
                      </View>
                    ) : (
                      <View style={styles.paymentUploadContent}>
                        <Ionicons name="image-outline" size={40} color={Colors.gold} />
                        <Text style={styles.paymentUploadText}>Tap to Upload Screenshot</Text>
                        <Text style={styles.paymentUploadHint}>Select from gallery</Text>
                      </View>
                    )}
                  </TouchableOpacity>
                </View>

                {/* Agreement Card */}
                <View style={styles.agreementCard}>
                  <Text style={styles.agreementTitle}>Terms & Conditions</Text>
                  
                  <View style={styles.agreementTerms}>
                    <View style={styles.termItem}>
                      <Ionicons name="wallet-outline" size={18} color={Colors.gold} />
                      <Text style={styles.termText}>Minimum wallet balance: ₹1000</Text>
                    </View>
                    <View style={styles.termItem}>
                      <Ionicons name="warning-outline" size={18} color={Colors.warning} />
                      <Text style={styles.termText}>Trip cancellation penalty: ₹500</Text>
                    </View>
                    <View style={styles.termItem}>
                      <Ionicons name="shield-checkmark-outline" size={18} color={Colors.success} />
                      <Text style={styles.termText}>Follow all platform rules</Text>
                    </View>
                    <View style={styles.termItem}>
                      <Ionicons name="alert-circle-outline" size={18} color={Colors.error} />
                      <Text style={styles.termText}>Account blocked for violations</Text>
                    </View>
                  </View>

                  <TouchableOpacity
                    style={styles.checkboxRow}
                    onPress={() => setAgreementAccepted(!agreementAccepted)}
                  >
                    <View style={[styles.checkbox, agreementAccepted && styles.checkboxChecked]}>
                      {agreementAccepted && <Ionicons name="checkmark" size={18} color={Colors.background} />}
                    </View>
                    <Text style={styles.checkboxLabel}>
                      I accept all Terms & Conditions
                    </Text>
                  </TouchableOpacity>
                </View>

                {/* Submit Buttons */}
                <View style={styles.buttonRow}>
                  <TouchableOpacity style={styles.outlineButton} onPress={() => setCurrentStep(2)}>
                    <Ionicons name="arrow-back" size={20} color={Colors.gold} />
                    <Text style={styles.outlineButtonText}>Back</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={[styles.submitButton, { flex: 1 }]} 
                    onPress={handleSubmit}
                    disabled={loading}
                  >
                    <LinearGradient
                      colors={[Colors.gradientGreenStart, Colors.gradientGreenEnd]}
                      style={styles.buttonGradient}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                    >
                      {loading ? (
                        <Text style={styles.submitButtonText}>Submitting...</Text>
                      ) : (
                        <>
                          <Ionicons name="checkmark-circle" size={22} color={Colors.white} />
                          <Text style={styles.submitButtonText}>Submit Registration</Text>
                        </>
                      )}
                    </LinearGradient>
                  </TouchableOpacity>
                </View>
              </View>
            )}

            <View style={{ height: 40 }} />
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: Colors.cardBackground,
    alignItems: 'center',
    justifyContent: 'center',
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
    color: Colors.gold,
    marginTop: 2,
  },
  progressContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 16,
    gap: 8,
  },
  progressStep: {
    flex: 1,
    height: 4,
    backgroundColor: Colors.cardBackground,
    borderRadius: 2,
  },
  progressStepActive: {
    backgroundColor: Colors.gold,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
  },
  stepContainer: {
    paddingTop: 8,
  },
  stepTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.white,
    marginBottom: 4,
  },
  stepSubtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.gold,
    marginTop: 24,
    marginBottom: 16,
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.textLight,
    marginBottom: 8,
  },
  inputWrapper: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  textInput: {
    fontSize: 16,
    color: Colors.white,
  },
  inputDisabled: {
    opacity: 0.6,
  },
  vehicleTypeRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  vehicleTypeBtn: {
    flex: 1,
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: Colors.border,
    backgroundColor: Colors.cardBackground,
  },
  vehicleTypeBtnActive: {
    backgroundColor: Colors.gold,
    borderColor: Colors.gold,
  },
  vehicleTypeText: {
    fontSize: 15,
    fontWeight: 'bold',
    color: Colors.gold,
    marginTop: 8,
  },
  vehicleTypeTextActive: {
    color: Colors.background,
  },
  primaryButton: {
    marginTop: 24,
    borderRadius: 14,
    overflow: 'hidden',
  },
  buttonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    gap: 8,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.background,
  },
  outlineButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 14,
    borderWidth: 2,
    borderColor: Colors.gold,
    gap: 6,
  },
  outlineButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.gold,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
  },
  docSectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.white,
    marginTop: 16,
    marginBottom: 12,
  },
  uploadRow: {
    flexDirection: 'row',
    gap: 12,
  },
  uploadCard: {
    flex: 1,
    minHeight: 120,
    backgroundColor: Colors.cardBackground,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: Colors.border,
    borderStyle: 'dashed',
    overflow: 'hidden',
  },
  uploadCardDone: {
    borderColor: Colors.success,
    borderStyle: 'solid',
  },
  uploadContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  uploadIconWrapper: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  uploadLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.white,
    textAlign: 'center',
  },
  uploadHint: {
    fontSize: 11,
    color: Colors.textLight,
    marginTop: 4,
  },
  uploadDoneContent: {
    flex: 1,
    position: 'relative',
  },
  uploadPreview: {
    width: '100%',
    height: '100%',
    borderRadius: 14,
  },
  uploadDoneBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    padding: 2,
  },
  // Payment Card Styles
  paymentCard: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  paymentHeader: {
    alignItems: 'center',
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    marginBottom: 16,
  },
  paymentLabel: {
    fontSize: 14,
    color: Colors.textLight,
  },
  paymentAmount: {
    fontSize: 42,
    fontWeight: 'bold',
    color: Colors.gold,
    marginVertical: 4,
  },
  paymentNote: {
    fontSize: 12,
    color: Colors.textLight,
  },
  paymentSteps: {
    marginBottom: 20,
  },
  paymentStep: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  stepNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: Colors.gold,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.background,
  },
  stepText: {
    fontSize: 14,
    color: Colors.white,
    flex: 1,
  },
  upiContainer: {
    marginBottom: 20,
  },
  upiTitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginBottom: 8,
  },
  upiBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceGold,
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  upiId: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.gold,
    letterSpacing: 0.5,
  },
  copyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.gold,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  copyButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.background,
  },
  uploadTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.white,
    marginBottom: 12,
  },
  paymentUploadCard: {
    minHeight: 100,
    backgroundColor: Colors.cardBackgroundLight,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: Colors.border,
    borderStyle: 'dashed',
    overflow: 'hidden',
  },
  paymentUploadDone: {
    borderColor: Colors.success,
    borderStyle: 'solid',
  },
  paymentUploadContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  paymentUploadText: {
    fontSize: 15,
    fontWeight: '600',
    color: Colors.white,
    marginTop: 10,
  },
  paymentUploadHint: {
    fontSize: 12,
    color: Colors.textLight,
    marginTop: 4,
  },
  paymentUploadDoneContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
  },
  paymentPreview: {
    width: 80,
    height: 80,
    borderRadius: 12,
  },
  paymentUploadBadge: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  paymentUploadBadgeText: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.success,
  },
  // Agreement Card Styles
  agreementCard: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  agreementTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.white,
    marginBottom: 16,
  },
  agreementTerms: {
    backgroundColor: Colors.cardBackgroundLight,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  termItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 12,
  },
  termText: {
    fontSize: 14,
    color: Colors.white,
    flex: 1,
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 26,
    height: 26,
    borderWidth: 2,
    borderColor: Colors.gold,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: Colors.gold,
  },
  checkboxLabel: {
    flex: 1,
    fontSize: 15,
    fontWeight: '500',
    color: Colors.white,
  },
  submitButton: {
    borderRadius: 14,
    overflow: 'hidden',
  },
  submitButtonText: {
    fontSize: 17,
    fontWeight: 'bold',
    color: Colors.white,
  },
  // Success Screen
  successContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
  successIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.white,
    marginBottom: 12,
    textAlign: 'center',
  },
  successMessage: {
    fontSize: 16,
    color: Colors.textLight,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 8,
  },
  successHint: {
    fontSize: 14,
    color: Colors.gold,
    marginBottom: 32,
  },
  successButton: {
    borderRadius: 14,
    overflow: 'hidden',
    width: '100%',
    maxWidth: 280,
  },
  successButtonGradient: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    alignItems: 'center',
  },
  successButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.background,
  },
});
