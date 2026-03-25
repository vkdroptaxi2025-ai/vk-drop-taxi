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
import { onboardDriver } from '../../utils/api';
import { useAuthStore } from '../../store/authStore';

// Yellow + Green theme
const COLORS = {
  primary: '#FFD700',
  secondary: '#2E7D32',
  background: '#FFFFFF',
  card: '#F8F9FA',
  text: '#1A1A1A',
  textLight: '#666666',
  border: '#E0E0E0',
  error: '#DC3545',
  success: '#28A745',
};

const SECTIONS = [
  { id: 1, title: 'Basic Details', icon: 'person' },
  { id: 2, title: 'Driver Photos', icon: 'camera' },
  { id: 3, title: 'Driver Documents', icon: 'document-text' },
  { id: 4, title: 'Vehicle Details', icon: 'car' },
  { id: 5, title: 'Vehicle Documents', icon: 'documents' },
  { id: 6, title: 'Vehicle Photos', icon: 'images' },
  { id: 7, title: 'Payment', icon: 'card' },
  { id: 8, title: 'Submit', icon: 'checkmark-circle' },
];

export default function DriverOnboardingForm() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const { setUser } = useAuthStore();
  
  const [currentSection, setCurrentSection] = useState(1);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [driverId, setDriverId] = useState<string | null>(null);

  // Section 1: Basic Details
  const [fullName, setFullName] = useState('');
  const [address, setAddress] = useState('');
  const [aadhaarNumber, setAadhaarNumber] = useState('');
  const [panNumber, setPanNumber] = useState('');
  const [dlNumber, setDlNumber] = useState('');
  const [experience, setExperience] = useState('');

  // Section 2: Driver Photos
  const [driverPhoto, setDriverPhoto] = useState<string | null>(null);
  const [driverWithVehicle, setDriverWithVehicle] = useState<string | null>(null);

  // Section 3: Driver Documents
  const [aadhaarFront, setAadhaarFront] = useState<string | null>(null);
  const [aadhaarBack, setAadhaarBack] = useState<string | null>(null);
  const [licenseFront, setLicenseFront] = useState<string | null>(null);
  const [licenseBack, setLicenseBack] = useState<string | null>(null);

  // Section 4: Vehicle Details
  const [vehicleType, setVehicleType] = useState<string>('sedan');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [vehicleYear, setVehicleYear] = useState('');

  // Section 5: Vehicle Documents
  const [rcFront, setRcFront] = useState<string | null>(null);
  const [rcBack, setRcBack] = useState<string | null>(null);
  const [insurance, setInsurance] = useState<string | null>(null);
  const [permit, setPermit] = useState<string | null>(null);
  const [pollution, setPollution] = useState<string | null>(null);

  // Section 6: Vehicle Photos
  const [vehicleFront, setVehicleFront] = useState<string | null>(null);
  const [vehicleBack, setVehicleBack] = useState<string | null>(null);
  const [vehicleLeft, setVehicleLeft] = useState<string | null>(null);
  const [vehicleRight, setVehicleRight] = useState<string | null>(null);

  // Section 7: Payment
  const [paymentAmount, setPaymentAmount] = useState('500');
  const [paymentScreenshot, setPaymentScreenshot] = useState<string | null>(null);

  // Image picker
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
        }
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  // Validation for each section
  const validateSection = (section: number): boolean => {
    switch (section) {
      case 1:
        if (!fullName.trim()) { Alert.alert('Required', 'Enter full name'); return false; }
        if (!address.trim()) { Alert.alert('Required', 'Enter address'); return false; }
        if (!aadhaarNumber.trim() || aadhaarNumber.length !== 12) { Alert.alert('Required', 'Enter valid 12-digit Aadhaar'); return false; }
        if (!dlNumber.trim()) { Alert.alert('Required', 'Enter DL number'); return false; }
        if (!experience.trim() || parseInt(experience) < 1) { Alert.alert('Required', 'Enter driving experience'); return false; }
        return true;
      case 2:
        if (!driverPhoto) { Alert.alert('Required', 'Upload driver photo'); return false; }
        if (!driverWithVehicle) { Alert.alert('Required', 'Upload driver with vehicle photo'); return false; }
        return true;
      case 3:
        if (!aadhaarFront) { Alert.alert('Required', 'Upload Aadhaar front'); return false; }
        if (!aadhaarBack) { Alert.alert('Required', 'Upload Aadhaar back'); return false; }
        if (!licenseFront) { Alert.alert('Required', 'Upload License front'); return false; }
        if (!licenseBack) { Alert.alert('Required', 'Upload License back'); return false; }
        return true;
      case 4:
        if (!vehicleNumber.trim()) { Alert.alert('Required', 'Enter vehicle number'); return false; }
        if (!vehicleModel.trim()) { Alert.alert('Required', 'Enter vehicle model'); return false; }
        if (!vehicleYear.trim() || parseInt(vehicleYear) < 2000) { Alert.alert('Required', 'Enter valid year'); return false; }
        return true;
      case 5:
        if (!rcFront) { Alert.alert('Required', 'Upload RC front'); return false; }
        if (!rcBack) { Alert.alert('Required', 'Upload RC back'); return false; }
        if (!insurance) { Alert.alert('Required', 'Upload insurance'); return false; }
        if (!permit) { Alert.alert('Required', 'Upload permit'); return false; }
        if (!pollution) { Alert.alert('Required', 'Upload pollution certificate'); return false; }
        return true;
      case 6:
        if (!vehicleFront) { Alert.alert('Required', 'Upload vehicle front photo'); return false; }
        if (!vehicleBack) { Alert.alert('Required', 'Upload vehicle back photo'); return false; }
        if (!vehicleLeft) { Alert.alert('Required', 'Upload vehicle left photo'); return false; }
        if (!vehicleRight) { Alert.alert('Required', 'Upload vehicle right photo'); return false; }
        return true;
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateSection(currentSection)) {
      setCurrentSection(currentSection + 1);
    }
  };

  const handlePrev = () => {
    if (currentSection > 1) {
      setCurrentSection(currentSection - 1);
    }
  };

  const handleSubmit = async () => {
    // Final validation
    for (let i = 1; i <= 6; i++) {
      if (!validateSection(i)) {
        setCurrentSection(i);
        return;
      }
    }

    setLoading(true);
    try {
      const data = {
        basic_details: {
          full_name: fullName.trim(),
          phone: phone as string,
          address: address.trim(),
          aadhaar_number: aadhaarNumber.trim(),
          pan_number: panNumber.trim() || null,
          driving_license_number: dlNumber.trim().toUpperCase(),
          driving_experience_years: parseInt(experience),
        },
        driver_photos: {
          driver_photo: driverPhoto,
          driver_with_vehicle_photo: driverWithVehicle,
        },
        driver_documents: {
          aadhaar_front: aadhaarFront,
          aadhaar_back: aadhaarBack,
          license_front: licenseFront,
          license_back: licenseBack,
        },
        vehicle_details: {
          vehicle_type: vehicleType,
          vehicle_number: vehicleNumber.trim().toUpperCase(),
          vehicle_model: vehicleModel.trim(),
          vehicle_year: parseInt(vehicleYear),
        },
        vehicle_documents: {
          rc_front: rcFront,
          rc_back: rcBack,
          insurance: insurance,
          permit: permit,
          pollution_certificate: pollution,
        },
        vehicle_photos: {
          front_photo: vehicleFront,
          back_photo: vehicleBack,
          left_photo: vehicleLeft,
          right_photo: vehicleRight,
        },
        payment: paymentScreenshot ? {
          amount: parseInt(paymentAmount) || 500,
          screenshot: paymentScreenshot,
        } : null,
      };

      const response = await onboardDriver(data);
      
      if (response.data.success) {
        setDriverId(response.data.driver_id);
        setSubmitted(true);
        await setUser({
          driver_id: response.data.driver_id,
          phone: phone as string,
          full_name: fullName,
          role: 'driver',
          approval_status: 'pending',
        });
      }
    } catch (error: any) {
      console.error('Onboarding error:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  // Success Screen
  if (submitted) {
    return (
      <View style={styles.container}>
        <View style={styles.successContainer}>
          <View style={styles.successIcon}>
            <Ionicons name="checkmark-circle" size={80} color={COLORS.success} />
          </View>
          <Text style={styles.successTitle}>Registration Complete!</Text>
          <Text style={styles.successMessage}>
            Your application has been submitted.{'\n'}
            Admin will verify your documents.
          </Text>
          <View style={styles.statusBadge}>
            <Ionicons name="time" size={20} color={COLORS.primary} />
            <Text style={styles.statusText}>PENDING APPROVAL</Text>
          </View>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => router.replace('/driver/pending-approval')}
          >
            <Text style={styles.primaryButtonText}>Check Status</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Upload Button Component
  const UploadButton = ({ 
    label, 
    value, 
    onPress,
    required = true 
  }: { 
    label: string; 
    value: string | null; 
    onPress: () => void;
    required?: boolean;
  }) => (
    <TouchableOpacity 
      style={[styles.uploadBtn, value && styles.uploadBtnDone]}
      onPress={onPress}
    >
      {value ? (
        <View style={styles.uploadDone}>
          <Image source={{ uri: value }} style={styles.uploadPreview} />
          <View style={styles.uploadCheck}>
            <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
          </View>
        </View>
      ) : (
        <View style={styles.uploadEmpty}>
          <Ionicons name="cloud-upload-outline" size={28} color={COLORS.secondary} />
          <Text style={styles.uploadLabel}>{label}</Text>
          {required && <Text style={styles.requiredStar}>*</Text>}
        </View>
      )}
    </TouchableOpacity>
  );

  // Input Component
  const FormInput = ({
    label,
    value,
    onChangeText,
    placeholder,
    keyboardType = 'default',
    maxLength,
    editable = true,
    required = true,
  }: any) => (
    <View style={styles.inputGroup}>
      <Text style={styles.inputLabel}>
        {label} {required && <Text style={styles.requiredStar}>*</Text>}
      </Text>
      <TextInput
        style={[styles.input, !editable && styles.inputDisabled]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={COLORS.textLight}
        keyboardType={keyboardType}
        maxLength={maxLength}
        editable={editable}
      />
    </View>
  );

  // Render Section Content
  const renderSectionContent = () => {
    switch (currentSection) {
      case 1:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Driver Basic Details</Text>
            <FormInput label="Full Name" value={fullName} onChangeText={setFullName} placeholder="Enter full name" />
            <FormInput label="Mobile Number" value={phone as string} editable={false} />
            <FormInput label="Address" value={address} onChangeText={setAddress} placeholder="Complete address" />
            <FormInput label="Aadhaar Number" value={aadhaarNumber} onChangeText={setAadhaarNumber} placeholder="12-digit Aadhaar" keyboardType="numeric" maxLength={12} />
            <FormInput label="PAN Number" value={panNumber} onChangeText={setPanNumber} placeholder="PAN (Optional)" required={false} maxLength={10} />
            <FormInput label="Driving License No." value={dlNumber} onChangeText={setDlNumber} placeholder="e.g. TN01 2020 0012345" />
            <FormInput label="Driving Experience (Years)" value={experience} onChangeText={setExperience} placeholder="e.g. 5" keyboardType="numeric" maxLength={2} />
          </View>
        );

      case 2:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Driver Photos</Text>
            <Text style={styles.sectionHint}>Upload clear photos for verification</Text>
            <View style={styles.uploadGrid}>
              <View style={styles.uploadItem}>
                <Text style={styles.uploadTitle}>Driver Photo *</Text>
                <UploadButton label="Passport Size" value={driverPhoto} onPress={() => pickImage(setDriverPhoto, 'Driver Photo')} />
              </View>
              <View style={styles.uploadItem}>
                <Text style={styles.uploadTitle}>Driver with Vehicle *</Text>
                <UploadButton label="Number Plate Visible" value={driverWithVehicle} onPress={() => pickImage(setDriverWithVehicle, 'Driver with Vehicle')} />
              </View>
            </View>
          </View>
        );

      case 3:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Driver Documents</Text>
            <Text style={styles.sectionHint}>Upload both sides of documents</Text>
            <Text style={styles.docLabel}>Aadhaar Card</Text>
            <View style={styles.uploadRow}>
              <UploadButton label="Front Side" value={aadhaarFront} onPress={() => pickImage(setAadhaarFront, 'Aadhaar Front')} />
              <UploadButton label="Back Side" value={aadhaarBack} onPress={() => pickImage(setAadhaarBack, 'Aadhaar Back')} />
            </View>
            <Text style={styles.docLabel}>Driving License</Text>
            <View style={styles.uploadRow}>
              <UploadButton label="Front Side" value={licenseFront} onPress={() => pickImage(setLicenseFront, 'License Front')} />
              <UploadButton label="Back Side" value={licenseBack} onPress={() => pickImage(setLicenseBack, 'License Back')} />
            </View>
          </View>
        );

      case 4:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Vehicle Details</Text>
            <Text style={styles.inputLabel}>Vehicle Type *</Text>
            <View style={styles.vehicleTypeRow}>
              {['sedan', 'suv', 'crysta'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[styles.vehicleTypeBtn, vehicleType === type && styles.vehicleTypeBtnActive]}
                  onPress={() => setVehicleType(type)}
                >
                  <Ionicons name="car" size={24} color={vehicleType === type ? COLORS.background : COLORS.secondary} />
                  <Text style={[styles.vehicleTypeText, vehicleType === type && styles.vehicleTypeTextActive]}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            <FormInput label="Vehicle Number" value={vehicleNumber} onChangeText={setVehicleNumber} placeholder="e.g. TN01AB1234" />
            <FormInput label="Vehicle Model" value={vehicleModel} onChangeText={setVehicleModel} placeholder="e.g. Swift Dzire" />
            <FormInput label="Vehicle Year" value={vehicleYear} onChangeText={setVehicleYear} placeholder="e.g. 2020" keyboardType="numeric" maxLength={4} />
          </View>
        );

      case 5:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Vehicle Documents</Text>
            <Text style={styles.sectionHint}>All documents are mandatory</Text>
            <Text style={styles.docLabel}>RC Book</Text>
            <View style={styles.uploadRow}>
              <UploadButton label="RC Front" value={rcFront} onPress={() => pickImage(setRcFront, 'RC Front')} />
              <UploadButton label="RC Back" value={rcBack} onPress={() => pickImage(setRcBack, 'RC Back')} />
            </View>
            <Text style={styles.docLabel}>Other Documents</Text>
            <View style={styles.uploadRow}>
              <UploadButton label="Insurance" value={insurance} onPress={() => pickImage(setInsurance, 'Insurance')} />
              <UploadButton label="Permit" value={permit} onPress={() => pickImage(setPermit, 'Permit')} />
            </View>
            <View style={styles.uploadSingle}>
              <UploadButton label="Pollution Certificate" value={pollution} onPress={() => pickImage(setPollution, 'Pollution')} />
            </View>
          </View>
        );

      case 6:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Vehicle Photos</Text>
            <Text style={styles.sectionHint}>Upload clear photos from all angles</Text>
            <View style={styles.uploadGrid}>
              <View style={styles.uploadItem}>
                <Text style={styles.uploadTitle}>Front View *</Text>
                <UploadButton label="Front" value={vehicleFront} onPress={() => pickImage(setVehicleFront, 'Front')} />
              </View>
              <View style={styles.uploadItem}>
                <Text style={styles.uploadTitle}>Back View *</Text>
                <UploadButton label="Back" value={vehicleBack} onPress={() => pickImage(setVehicleBack, 'Back')} />
              </View>
              <View style={styles.uploadItem}>
                <Text style={styles.uploadTitle}>Left Side *</Text>
                <UploadButton label="Left" value={vehicleLeft} onPress={() => pickImage(setVehicleLeft, 'Left')} />
              </View>
              <View style={styles.uploadItem}>
                <Text style={styles.uploadTitle}>Right Side *</Text>
                <UploadButton label="Right" value={vehicleRight} onPress={() => pickImage(setVehicleRight, 'Right')} />
              </View>
            </View>
          </View>
        );

      case 7:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Payment (Optional)</Text>
            <Text style={styles.sectionHint}>Attachment fee for driver registration</Text>
            <View style={styles.paymentCard}>
              <Text style={styles.paymentAmount}>₹{paymentAmount}</Text>
              <Text style={styles.paymentNote}>One-time attachment fee</Text>
            </View>
            <Text style={styles.docLabel}>Payment Screenshot</Text>
            <View style={styles.uploadSingle}>
              <UploadButton label="Upload Screenshot" value={paymentScreenshot} onPress={() => pickImage(setPaymentScreenshot, 'Payment')} required={false} />
            </View>
            <Text style={styles.paymentSkip}>You can skip this and pay later</Text>
          </View>
        );

      case 8:
        return (
          <View style={styles.sectionContent}>
            <Text style={styles.sectionTitle}>Review & Submit</Text>
            <View style={styles.summaryCard}>
              <Text style={styles.summaryTitle}>Application Summary</Text>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Name:</Text>
                <Text style={styles.summaryValue}>{fullName}</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Phone:</Text>
                <Text style={styles.summaryValue}>{phone}</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Vehicle:</Text>
                <Text style={styles.summaryValue}>{vehicleType.toUpperCase()} - {vehicleNumber}</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Documents:</Text>
                <Text style={styles.summaryValue}>
                  {[aadhaarFront, aadhaarBack, licenseFront, licenseBack, rcFront, rcBack, insurance, permit, pollution].filter(Boolean).length} / 9 uploaded
                </Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Photos:</Text>
                <Text style={styles.summaryValue}>
                  {[driverPhoto, driverWithVehicle, vehicleFront, vehicleBack, vehicleLeft, vehicleRight].filter(Boolean).length} / 6 uploaded
                </Text>
              </View>
            </View>
            <TouchableOpacity
              style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
              onPress={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="checkmark-circle" size={24} color="#fff" />
                  <Text style={styles.submitBtnText}>SUBMIT APPLICATION</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        );
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => currentSection > 1 ? handlePrev() : router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.text} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>Driver Onboarding</Text>
          <Text style={styles.headerSubtitle}>Step {currentSection} of 8</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      {/* Progress Steps */}
      <View style={styles.progressContainer}>
        {SECTIONS.map((s) => (
          <View
            key={s.id}
            style={[
              styles.progressDot,
              s.id < currentSection && styles.progressDotDone,
              s.id === currentSection && styles.progressDotActive,
            ]}
          />
        ))}
      </View>

      {/* Content */}
      <KeyboardAvoidingView style={styles.keyboardView} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {renderSectionContent()}
          <View style={{ height: 100 }} />
        </ScrollView>
      </KeyboardAvoidingView>

      {/* Footer Navigation */}
      {currentSection < 8 && (
        <View style={styles.footer}>
          {currentSection > 1 && (
            <TouchableOpacity style={styles.prevBtn} onPress={handlePrev}>
              <Ionicons name="arrow-back" size={20} color={COLORS.secondary} />
              <Text style={styles.prevBtnText}>Back</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity style={styles.nextBtn} onPress={handleNext}>
            <Text style={styles.nextBtnText}>
              {currentSection === 7 ? 'Review' : 'Next'}
            </Text>
            <Ionicons name="arrow-forward" size={20} color={COLORS.text} />
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: COLORS.primary,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerCenter: { alignItems: 'center' },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: COLORS.text },
  headerSubtitle: { fontSize: 12, color: COLORS.textLight, marginTop: 2 },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
    backgroundColor: COLORS.card,
  },
  progressDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.border,
  },
  progressDotDone: { backgroundColor: COLORS.success },
  progressDotActive: { backgroundColor: COLORS.primary, width: 24 },
  keyboardView: { flex: 1 },
  scrollView: { flex: 1 },
  scrollContent: { padding: 16 },
  sectionContent: { backgroundColor: COLORS.card, borderRadius: 16, padding: 16 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.text, marginBottom: 8 },
  sectionHint: { fontSize: 14, color: COLORS.textLight, marginBottom: 16 },
  inputGroup: { marginBottom: 16 },
  inputLabel: { fontSize: 14, fontWeight: '600', color: COLORS.text, marginBottom: 8 },
  requiredStar: { color: COLORS.error },
  input: {
    backgroundColor: COLORS.background,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    color: COLORS.text,
  },
  inputDisabled: { backgroundColor: '#F0F0F0' },
  vehicleTypeRow: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  vehicleTypeBtn: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 14,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: COLORS.border,
    backgroundColor: COLORS.background,
  },
  vehicleTypeBtnActive: { backgroundColor: COLORS.secondary, borderColor: COLORS.secondary },
  vehicleTypeText: { fontSize: 13, fontWeight: '600', color: COLORS.secondary, marginTop: 4 },
  vehicleTypeTextActive: { color: COLORS.background },
  docLabel: { fontSize: 16, fontWeight: '600', color: COLORS.text, marginTop: 12, marginBottom: 10 },
  uploadRow: { flexDirection: 'row', gap: 12 },
  uploadGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  uploadItem: { width: '47%' },
  uploadTitle: { fontSize: 13, fontWeight: '600', color: COLORS.text, marginBottom: 6 },
  uploadSingle: { marginTop: 12 },
  uploadBtn: {
    flex: 1,
    minHeight: 100,
    backgroundColor: COLORS.background,
    borderWidth: 2,
    borderColor: COLORS.border,
    borderStyle: 'dashed',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
  },
  uploadBtnDone: { borderColor: COLORS.success, borderStyle: 'solid' },
  uploadEmpty: { alignItems: 'center' },
  uploadLabel: { fontSize: 13, color: COLORS.textLight, marginTop: 6, textAlign: 'center' },
  uploadDone: { alignItems: 'center', position: 'relative' },
  uploadPreview: { width: 70, height: 50, borderRadius: 6 },
  uploadCheck: { position: 'absolute', top: -8, right: -8, backgroundColor: '#fff', borderRadius: 10 },
  paymentCard: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 20,
  },
  paymentAmount: { fontSize: 36, fontWeight: 'bold', color: COLORS.text },
  paymentNote: { fontSize: 14, color: COLORS.textLight, marginTop: 4 },
  paymentSkip: { fontSize: 12, color: COLORS.textLight, textAlign: 'center', marginTop: 12 },
  summaryCard: {
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 20,
  },
  summaryTitle: { fontSize: 16, fontWeight: 'bold', color: COLORS.text, marginBottom: 12 },
  summaryRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  summaryLabel: { fontSize: 14, color: COLORS.textLight },
  summaryValue: { fontSize: 14, fontWeight: '600', color: COLORS.text },
  submitBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.secondary,
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
  },
  submitBtnDisabled: { opacity: 0.6 },
  submitBtnText: { fontSize: 16, fontWeight: 'bold', color: '#fff' },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: COLORS.background,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  prevBtn: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 20, gap: 6 },
  prevBtnText: { fontSize: 16, fontWeight: '600', color: COLORS.secondary },
  nextBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.primary,
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 10,
    gap: 8,
    marginLeft: 'auto',
  },
  nextBtnText: { fontSize: 16, fontWeight: 'bold', color: COLORS.text },
  successContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  successIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(40,167,69,0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  successTitle: { fontSize: 26, fontWeight: 'bold', color: COLORS.text, marginBottom: 12 },
  successMessage: { fontSize: 16, color: COLORS.textLight, textAlign: 'center', lineHeight: 24, marginBottom: 24 },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    gap: 8,
    marginBottom: 32,
  },
  statusText: { fontSize: 14, fontWeight: 'bold', color: COLORS.primary },
  primaryButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 12,
  },
  primaryButtonText: { fontSize: 16, fontWeight: 'bold', color: COLORS.text },
});
