import React, { useState, useCallback } from 'react';
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

// Safe Image Component to prevent crashes
const SafeImage = ({ uri, style }: { uri: string | null; style: any }) => {
  if (!uri || typeof uri !== 'string' || uri.length < 10) {
    return null;
  }
  return <Image source={{ uri: uri }} style={style} />;
};

// Upload Button Component - DEFINED OUTSIDE to prevent re-creation
const UploadButton = React.memo(({ 
  label, 
  value, 
  onPress,
  required = true 
}: { 
  label: string; 
  value: string | null; 
  onPress: () => void;
  required?: boolean;
}) => {
  const hasValidImage = value && typeof value === 'string' && value.length > 10;
  
  return (
    <TouchableOpacity 
      style={[styles.uploadBtn, hasValidImage && styles.uploadBtnDone]}
      onPress={onPress}
    >
      {hasValidImage ? (
        <View style={styles.uploadDone}>
          <SafeImage uri={value} style={styles.uploadPreview} />
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
});

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
  const [paymentScreenshot, setPaymentScreenshot] = useState<string | null>(null);

  // SIMPLIFIED Image picker - directly opens gallery (works on ALL devices)
  const pickImage = useCallback(async (setter: (uri: string) => void, label: string) => {
    console.log(`[ImagePicker] Opening gallery for: ${label}`);
    
    try {
      // Request permission first
      console.log('[ImagePicker] Requesting permissions...');
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      console.log('[ImagePicker] Permission status:', status);
      
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required', 
          'Please allow photo library access to upload images. Go to Settings > Apps > VK Drop Taxi > Permissions'
        );
        return;
      }
      
      // Launch image library directly (no alert dialog)
      console.log('[ImagePicker] Launching image library...');
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.3,
        base64: true,
      });
      
      console.log('[ImagePicker] Result:', result.canceled ? 'Cancelled' : 'Image selected');
      
      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        console.log('[ImagePicker] Asset uri:', asset.uri?.substring(0, 50) + '...');
        console.log('[ImagePicker] Asset base64 length:', asset.base64?.length || 0);
        
        if (asset.base64 && typeof asset.base64 === 'string' && asset.base64.length > 0) {
          const imageData = `data:image/jpeg;base64,${asset.base64}`;
          setter(imageData);
          console.log(`[ImagePicker] ${label} uploaded successfully (base64)`);
          Alert.alert('Success', `${label} uploaded!`);
        } else if (asset.uri && typeof asset.uri === 'string') {
          // Use URI directly if it's already a data URL or valid URI
          if (asset.uri.startsWith('data:')) {
            setter(asset.uri);
            console.log(`[ImagePicker] ${label} uploaded successfully (data URI)`);
            Alert.alert('Success', `${label} uploaded!`);
          } else {
            setter(asset.uri);
            console.log(`[ImagePicker] ${label} uploaded successfully (file URI)`);
            Alert.alert('Success', `${label} uploaded!`);
          }
        } else {
          console.error('[ImagePicker] No valid image data');
          Alert.alert('Upload Failed', 'Could not process the image. Please try again.');
        }
      } else {
        console.log('[ImagePicker] Image selection cancelled');
      }
    } catch (error: any) {
      console.error('[ImagePicker] Error:', error);
      Alert.alert('Error', error.message || 'Failed to open gallery. Please try again.');
    }
  }, []);

  // FIXED: Simplified validation - only validates on final submit, not blocking navigation
  const validateSectionForSubmit = useCallback((section: number): { valid: boolean; message: string } => {
    switch (section) {
      case 1:
        if (!fullName.trim()) return { valid: false, message: 'Enter full name in Basic Details' };
        if (!address.trim()) return { valid: false, message: 'Enter address in Basic Details' };
        if (!aadhaarNumber.trim() || aadhaarNumber.length !== 12) return { valid: false, message: 'Enter valid 12-digit Aadhaar in Basic Details' };
        if (!dlNumber.trim()) return { valid: false, message: 'Enter DL number in Basic Details' };
        if (!experience.trim() || parseInt(experience) < 1) return { valid: false, message: 'Enter driving experience in Basic Details' };
        return { valid: true, message: '' };
      case 2:
        if (!driverPhoto) return { valid: false, message: 'Upload driver photo in Driver Photos section' };
        if (!driverWithVehicle) return { valid: false, message: 'Upload driver with vehicle photo in Driver Photos section' };
        return { valid: true, message: '' };
      case 3:
        if (!aadhaarFront) return { valid: false, message: 'Upload Aadhaar front in Driver Documents section' };
        if (!aadhaarBack) return { valid: false, message: 'Upload Aadhaar back in Driver Documents section' };
        if (!licenseFront) return { valid: false, message: 'Upload License front in Driver Documents section' };
        if (!licenseBack) return { valid: false, message: 'Upload License back in Driver Documents section' };
        return { valid: true, message: '' };
      case 4:
        if (!vehicleNumber.trim()) return { valid: false, message: 'Enter vehicle number in Vehicle Details' };
        if (!vehicleModel.trim()) return { valid: false, message: 'Enter vehicle model in Vehicle Details' };
        if (!vehicleYear.trim() || parseInt(vehicleYear) < 2000) return { valid: false, message: 'Enter valid vehicle year (2000+) in Vehicle Details' };
        return { valid: true, message: '' };
      case 5:
        if (!rcFront) return { valid: false, message: 'Upload RC front in Vehicle Documents section' };
        if (!rcBack) return { valid: false, message: 'Upload RC back in Vehicle Documents section' };
        if (!insurance) return { valid: false, message: 'Upload insurance in Vehicle Documents section' };
        if (!permit) return { valid: false, message: 'Upload permit in Vehicle Documents section' };
        if (!pollution) return { valid: false, message: 'Upload pollution certificate in Vehicle Documents section' };
        return { valid: true, message: '' };
      case 6:
        if (!vehicleFront) return { valid: false, message: 'Upload vehicle front photo in Vehicle Photos section' };
        if (!vehicleBack) return { valid: false, message: 'Upload vehicle back photo in Vehicle Photos section' };
        if (!vehicleLeft) return { valid: false, message: 'Upload vehicle left photo in Vehicle Photos section' };
        if (!vehicleRight) return { valid: false, message: 'Upload vehicle right photo in Vehicle Photos section' };
        return { valid: true, message: '' };
      case 7:
        if (!paymentScreenshot) return { valid: false, message: 'Payment screenshot is MANDATORY. Please pay ₹500 and upload proof.' };
        return { valid: true, message: '' };
      default:
        return { valid: true, message: '' };
    }
  }, [fullName, address, aadhaarNumber, dlNumber, experience, driverPhoto, driverWithVehicle, 
      aadhaarFront, aadhaarBack, licenseFront, licenseBack, vehicleNumber, vehicleModel, vehicleYear,
      rcFront, rcBack, insurance, permit, pollution, vehicleFront, vehicleBack, vehicleLeft, vehicleRight, paymentScreenshot]);

  // FIXED: Next button now works without blocking - validates only on submit
  const handleNext = useCallback(() => {
    if (currentSection < 8) {
      setCurrentSection(currentSection + 1);
    }
  }, [currentSection]);

  const handlePrev = useCallback(() => {
    if (currentSection > 1) {
      setCurrentSection(currentSection - 1);
    }
  }, [currentSection]);

  const handleSubmit = async () => {
    // Final validation - check all sections
    for (let i = 1; i <= 7; i++) {
      const result = validateSectionForSubmit(i);
      if (!result.valid) {
        Alert.alert('Missing Information', result.message);
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
          amount: 500,
          screenshot: paymentScreenshot,
        } : null,
      };

      const response = await onboardDriver(data);
      
      if (response.data.success) {
        setDriverId(response.data.driver_id);
        setSubmitted(true);
        // Store driver data in auth store
        await setUser({
          driver_id: response.data.driver_id,
          phone: phone as string,
          name: fullName,
          role: 'driver',
          approval_status: 'pending',
        });
        console.log('Driver registered with ID:', response.data.driver_id);
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
          {driverId && (
            <View style={styles.driverIdBox}>
              <Text style={styles.driverIdLabel}>Your Driver ID</Text>
              <Text style={styles.driverIdValue}>{driverId}</Text>
            </View>
          )}
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

  // Get completion status for each section
  const getSectionStatus = (sectionId: number): 'complete' | 'incomplete' | 'current' => {
    if (sectionId === currentSection) return 'current';
    const result = validateSectionForSubmit(sectionId);
    return result.valid ? 'complete' : 'incomplete';
  };

  // Render Section 1 - Basic Details
  const renderSection1 = () => (
    <View style={styles.sectionContent}>
      <Text style={styles.sectionTitle}>Driver Basic Details</Text>
      <Text style={styles.sectionHint}>Fill in your personal information</Text>
      
      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Full Name <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={fullName}
          onChangeText={setFullName}
          placeholder="Enter full name"
          placeholderTextColor={COLORS.textLight}
          autoCorrect={false}
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Mobile Number <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={[styles.input, styles.inputDisabled]}
          value={phone as string}
          editable={false}
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Address <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={address}
          onChangeText={setAddress}
          placeholder="Complete address"
          placeholderTextColor={COLORS.textLight}
          multiline
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Aadhaar Number <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={aadhaarNumber}
          onChangeText={setAadhaarNumber}
          placeholder="12-digit Aadhaar"
          placeholderTextColor={COLORS.textLight}
          keyboardType="numeric"
          maxLength={12}
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>PAN Number</Text>
        <TextInput
          style={styles.input}
          value={panNumber}
          onChangeText={setPanNumber}
          placeholder="PAN (Optional)"
          placeholderTextColor={COLORS.textLight}
          maxLength={10}
          autoCapitalize="characters"
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Driving License No. <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={dlNumber}
          onChangeText={setDlNumber}
          placeholder="e.g. TN01 2020 0012345"
          placeholderTextColor={COLORS.textLight}
          autoCapitalize="characters"
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Driving Experience (Years) <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={experience}
          onChangeText={setExperience}
          placeholder="e.g. 5"
          placeholderTextColor={COLORS.textLight}
          keyboardType="numeric"
          maxLength={2}
        />
      </View>
    </View>
  );

  // Render Section 2 - Driver Photos
  const renderSection2 = () => (
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

  // Render Section 3 - Driver Documents
  const renderSection3 = () => (
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

  // Render Section 4 - Vehicle Details
  const renderSection4 = () => (
    <View style={styles.sectionContent}>
      <Text style={styles.sectionTitle}>Vehicle Details</Text>
      <Text style={styles.sectionHint}>Enter your vehicle information</Text>
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

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Vehicle Number <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={vehicleNumber}
          onChangeText={setVehicleNumber}
          placeholder="e.g. TN01AB1234"
          placeholderTextColor={COLORS.textLight}
          autoCapitalize="characters"
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Vehicle Model <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={vehicleModel}
          onChangeText={setVehicleModel}
          placeholder="e.g. Swift Dzire"
          placeholderTextColor={COLORS.textLight}
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>Vehicle Year <Text style={styles.requiredStar}>*</Text></Text>
        <TextInput
          style={styles.input}
          value={vehicleYear}
          onChangeText={setVehicleYear}
          placeholder="e.g. 2020"
          placeholderTextColor={COLORS.textLight}
          keyboardType="numeric"
          maxLength={4}
        />
      </View>
    </View>
  );

  // Render Section 5 - Vehicle Documents
  const renderSection5 = () => (
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

  // Render Section 6 - Vehicle Photos
  const renderSection6 = () => (
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

  // Render Section 7 - Payment
  const renderSection7 = () => (
    <View style={styles.sectionContent}>
      <Text style={styles.sectionTitle}>Registration Payment</Text>
      <Text style={styles.sectionHint}>Pay attachment fee to complete registration</Text>
      
      <View style={styles.paymentCard}>
        <Text style={styles.paymentAmount}>Rs.500</Text>
        <Text style={styles.paymentNote}>One-time attachment fee (NON-REFUNDABLE)</Text>
      </View>
      
      <View style={styles.upiBox}>
        <Text style={styles.upiLabel}>UPI ID</Text>
        <Text style={styles.upiId}>vkdrop@upi</Text>
        <Text style={styles.upiInstructions}>
          1. Open any UPI app (GPay, PhonePe, Paytm){'\n'}
          2. Pay Rs.500 to above UPI ID{'\n'}
          3. Take screenshot of payment{'\n'}
          4. Upload screenshot below
        </Text>
      </View>
      
      <Text style={styles.docLabel}>Payment Screenshot <Text style={styles.requiredStar}>* MANDATORY</Text></Text>
      <View style={styles.uploadSingle}>
        <UploadButton label="Upload Payment Proof" value={paymentScreenshot} onPress={() => pickImage(setPaymentScreenshot, 'Payment')} required={true} />
      </View>
      
      <View style={styles.warningBox}>
        <Ionicons name="warning" size={20} color={COLORS.error} />
        <Text style={styles.warningText}>You cannot submit without payment screenshot</Text>
      </View>
    </View>
  );

  // Render Section 8 - Submit
  const renderSection8 = () => {
    // Count completed items
    const documentsCount = [aadhaarFront, aadhaarBack, licenseFront, licenseBack, rcFront, rcBack, insurance, permit, pollution].filter(Boolean).length;
    const photosCount = [driverPhoto, driverWithVehicle, vehicleFront, vehicleBack, vehicleLeft, vehicleRight].filter(Boolean).length;
    
    return (
      <View style={styles.sectionContent}>
        <Text style={styles.sectionTitle}>Review & Submit</Text>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Application Summary</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Name:</Text>
            <Text style={styles.summaryValue}>{fullName || 'Not entered'}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Phone:</Text>
            <Text style={styles.summaryValue}>{phone}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Vehicle:</Text>
            <Text style={styles.summaryValue}>{vehicleType.toUpperCase()} - {vehicleNumber || 'Not entered'}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Documents:</Text>
            <Text style={[styles.summaryValue, documentsCount < 9 && { color: COLORS.error }]}>
              {documentsCount} / 9 uploaded
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Photos:</Text>
            <Text style={[styles.summaryValue, photosCount < 6 && { color: COLORS.error }]}>
              {photosCount} / 6 uploaded
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Payment:</Text>
            <Text style={[styles.summaryValue, !paymentScreenshot && { color: COLORS.error }]}>
              {paymentScreenshot ? 'Uploaded' : 'Not uploaded'}
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
  };

  // Render Section Content based on current section
  const renderSectionContent = () => {
    switch (currentSection) {
      case 1: return renderSection1();
      case 2: return renderSection2();
      case 3: return renderSection3();
      case 4: return renderSection4();
      case 5: return renderSection5();
      case 6: return renderSection6();
      case 7: return renderSection7();
      case 8: return renderSection8();
      default: return renderSection1();
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
        {SECTIONS.map((s) => {
          const status = getSectionStatus(s.id);
          return (
            <TouchableOpacity
              key={s.id}
              onPress={() => setCurrentSection(s.id)}
              style={[
                styles.progressDot,
                status === 'complete' && styles.progressDotDone,
                status === 'current' && styles.progressDotActive,
              ]}
            />
          );
        })}
      </View>

      {/* Content */}
      <KeyboardAvoidingView style={styles.keyboardView} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView 
          style={styles.scrollView} 
          contentContainerStyle={styles.scrollContent} 
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="none"
        >
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
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.text, marginBottom: 4 },
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
  upiBox: {
    backgroundColor: '#FFF9E6',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  upiLabel: { fontSize: 12, color: COLORS.textLight, marginBottom: 4 },
  upiId: { fontSize: 22, fontWeight: 'bold', color: COLORS.secondary, marginBottom: 12 },
  upiInstructions: { fontSize: 14, color: COLORS.text, lineHeight: 22 },
  warningBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFEBEE',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
    gap: 8,
    borderWidth: 1,
    borderColor: COLORS.error,
  },
  warningText: { fontSize: 13, color: COLORS.error, flex: 1 },
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
  successMessage: { fontSize: 16, color: COLORS.textLight, textAlign: 'center', lineHeight: 24, marginBottom: 16 },
  driverIdBox: {
    backgroundColor: COLORS.card,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 16,
    alignItems: 'center',
  },
  driverIdLabel: { fontSize: 12, color: COLORS.textLight, marginBottom: 4 },
  driverIdValue: { fontSize: 20, fontWeight: 'bold', color: COLORS.secondary },
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
