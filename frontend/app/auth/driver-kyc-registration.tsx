import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Colors } from '../../utils/colors';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '../../components/Button';
import axios from 'axios';

// Import step components
import PersonalDetailsStep from '../../components/kyc/PersonalDetailsStep';
import BankDetailsStep from '../../components/kyc/BankDetailsStep';
import VehicleDetailsStep from '../../components/kyc/VehicleDetailsStep';
import DocumentsStep from '../../components/kyc/DocumentsStep';
import ExpiryDatesStep from '../../components/kyc/ExpiryDatesStep';
import DriverVehiclePhotoStep from '../../components/kyc/DriverVehiclePhotoStep';
import ReviewStep from '../../components/kyc/ReviewStep';

const STEPS = [
  { title: 'Personal', icon: 'person' },
  { title: 'Bank', icon: 'card' },
  { title: 'Vehicle', icon: 'car' },
  { title: 'Documents', icon: 'document-text' },
  { title: 'Expiry', icon: 'calendar' },
  { title: 'Photo', icon: 'camera' },
  { title: 'Review', icon: 'checkmark-circle' },
];

export default function DriverKYCRegistration() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Form data state
  const [formData, setFormData] = useState({
    phone: phone as string,
    personalDetails: {
      full_name: '',
      mobile_number: phone as string,
      full_address: '',
      aadhaar_number: '',
      pan_number: '',
      driving_license_number: '',
      driving_experience_years: 0,
      driver_photo: '',
    },
    bankDetails: {
      account_holder_name: '',
      bank_name: '',
      account_number: '',
      ifsc_code: '',
      branch_name: '',
    },
    vehicleDetails: {
      vehicle_type: 'sedan',
      vehicle_number: '',
      vehicle_model: '',
      vehicle_year: new Date().getFullYear(),
    },
    documents: {
      aadhaar_card: { front_image: '', back_image: null },
      pan_card: { front_image: '', back_image: null },
      driving_license: { front_image: '', back_image: null },
      rc_book: { front_image: '', back_image: null },
      insurance: { front_image: '', back_image: null },
      fitness_certificate: { front_image: '', back_image: null },
      permit: { front_image: '', back_image: null },
      pollution_certificate: { front_image: '', back_image: null },
    },
    documentExpiry: {
      insurance_expiry: '',
      fc_expiry: '',
      permit_expiry: '',
      pollution_expiry: '',
      license_expiry: '',
    },
    driverVehiclePhoto: {
      photo: '',
    },
  });

  const updateFormData = (stepData: any) => {
    setFormData({ ...formData, ...stepData });
  };

  const nextStep = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const previousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
      
      const response = await axios.post(`${API_URL}/api/driver/register-kyc`, {
        phone: formData.phone,
        personal_details: formData.personalDetails,
        bank_details: formData.bankDetails,
        vehicle_details: formData.vehicleDetails,
        documents: formData.documents,
        document_expiry: formData.documentExpiry,
        driver_vehicle_photo: formData.driverVehiclePhoto,
      });

      if (response.data.success) {
        Alert.alert(
          'Registration Successful!',
          'Your KYC application has been submitted. Admin will review and approve soon.',
          [
            {
              text: 'OK',
              onPress: () => router.replace('/driver/dashboard'),
            },
          ]
        );
      }
    } catch (error: any) {
      Alert.alert(
        'Registration Failed',
        error.response?.data?.detail || 'Please check all fields and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <PersonalDetailsStep
            data={formData.personalDetails}
            onUpdate={(data) => updateFormData({ personalDetails: data })}
            onNext={nextStep}
          />
        );
      case 1:
        return (
          <BankDetailsStep
            data={formData.bankDetails}
            onUpdate={(data) => updateFormData({ bankDetails: data })}
            onNext={nextStep}
            onBack={previousStep}
          />
        );
      case 2:
        return (
          <VehicleDetailsStep
            data={formData.vehicleDetails}
            onUpdate={(data) => updateFormData({ vehicleDetails: data })}
            onNext={nextStep}
            onBack={previousStep}
          />
        );
      case 3:
        return (
          <DocumentsStep
            data={formData.documents}
            onUpdate={(data) => updateFormData({ documents: data })}
            onNext={nextStep}
            onBack={previousStep}
          />
        );
      case 4:
        return (
          <ExpiryDatesStep
            data={formData.documentExpiry}
            onUpdate={(data) => updateFormData({ documentExpiry: data })}
            onNext={nextStep}
            onBack={previousStep}
          />
        );
      case 5:
        return (
          <DriverVehiclePhotoStep
            data={formData.driverVehiclePhoto}
            onUpdate={(data) => updateFormData({ driverVehiclePhoto: data })}
            onNext={nextStep}
            onBack={previousStep}
          />
        );
      case 6:
        return (
          <ReviewStep
            formData={formData}
            onBack={previousStep}
            onSubmit={handleSubmit}
            loading={loading}
          />
        );
      default:
        return null;
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Driver Registration</Text>
        <Text style={styles.headerSubtitle}>Complete KYC Process</Text>
      </View>

      {/* Progress Indicator */}
      <View style={styles.progressContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {STEPS.map((step, index) => (
            <View key={index} style={styles.progressStep}>
              <View
                style={[
                  styles.progressCircle,
                  index <= currentStep && styles.progressCircleActive,
                  index < currentStep && styles.progressCircleCompleted,
                ]}
              >
                {index < currentStep ? (
                  <Ionicons name=\"checkmark\" size={16} color={Colors.white} />
                ) : (
                  <Text
                    style={[
                      styles.progressNumber,
                      index <= currentStep && styles.progressNumberActive,
                    ]}
                  >
                    {index + 1}
                  </Text>
                )}
              </View>
              <Text
                style={[
                  styles.progressLabel,
                  index === currentStep && styles.progressLabelActive,
                ]}
              >
                {step.title}
              </Text>
              {index < STEPS.length - 1 && (
                <View
                  style={[
                    styles.progressLine,
                    index < currentStep && styles.progressLineActive,
                  ]}
                />
              )}
            </View>
          ))}
        </ScrollView>
      </View>

      {/* Step Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {renderStep()}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.white,
  },
  header: {
    backgroundColor: Colors.secondary,
    padding: 20,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.white,
  },
  headerSubtitle: {
    fontSize: 14,
    color: Colors.white,
    marginTop: 4,
    opacity: 0.9,
  },
  progressContainer: {
    backgroundColor: Colors.white,
    paddingVertical: 16,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  progressStep: {
    alignItems: 'center',
    marginHorizontal: 8,
    position: 'relative',
  },
  progressCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: Colors.lightGray,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  progressCircleActive: {
    backgroundColor: Colors.secondary,
  },
  progressCircleCompleted: {
    backgroundColor: Colors.success,
  },
  progressNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.gray,
  },
  progressNumberActive: {
    color: Colors.white,
  },
  progressLabel: {
    fontSize: 10,
    color: Colors.gray,
    marginTop: 4,
  },
  progressLabelActive: {
    color: Colors.secondary,
    fontWeight: '600',
  },
  progressLine: {
    position: 'absolute',
    top: 16,
    left: 32,
    width: 40,
    height: 2,
    backgroundColor: Colors.lightGray,
  },
  progressLineActive: {
    backgroundColor: Colors.success,
  },
  content: {
    flex: 1,
    padding: 16,
  },
});
