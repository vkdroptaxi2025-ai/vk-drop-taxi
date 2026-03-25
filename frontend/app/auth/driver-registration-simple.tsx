import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Platform,
  Image,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Colors } from '../../utils/colors';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';
import axios from 'axios';

// Conditional import for image picker
let ImagePicker: any = null;
if (Platform.OS !== 'web') {
  ImagePicker = require('expo-image-picker');
}

export default function SimpleDriverRegistration() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const [loading, setLoading] = useState(false);
  const [currentSection, setCurrentSection] = useState(1); // 1, 2, or 3

  // Form state
  const [formData, setFormData] = useState({
    // Personal Details
    full_name: '',
    mobile_number: phone as string,
    full_address: '',
    aadhaar_number: '',
    pan_number: '',
    driving_license_number: '',
    driving_experience_years: '5',
    driver_photo: '',

    // Bank Details
    account_holder_name: '',
    bank_name: '',
    account_number: '',
    ifsc_code: '',
    branch_name: '',

    // Vehicle Details
    vehicle_type: 'sedan',
    vehicle_number: '',
    vehicle_model: '',
    vehicle_year: new Date().getFullYear().toString(),

    // Documents (single image each)
    aadhaar_doc: '',
    pan_doc: '',
    license_doc: '',
    rc_doc: '',
    insurance_doc: '',
    fc_doc: '',
    permit_doc: '',
    pollution_doc: '',

    // Expiry Dates
    insurance_expiry: '',
    fc_expiry: '',
    permit_expiry: '',
    pollution_expiry: '',
    license_expiry: '',

    // Driver + Vehicle Photo
    driver_vehicle_photo: '',
  });

  const pickImage = async (field: string) => {
    if (Platform.OS === 'web') {
      Alert.alert('Not Available', 'Image upload works on mobile. Using placeholder for web.');
      const placeholder = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
      setFormData({ ...formData, [field]: placeholder });
      return;
    }

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.3,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        setFormData({ ...formData, [field]: base64Image });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const takePhoto = async (field: string) => {
    if (Platform.OS === 'web') {
      pickImage(field);
      return;
    }

    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Camera permission is required');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.3,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        setFormData({ ...formData, [field]: base64Image });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take photo');
    }
  };

  const validateSection1 = () => {
    if (!formData.full_name.trim()) {
      Alert.alert('Validation Error', 'Please enter full name');
      return false;
    }
    if (!formData.full_address.trim()) {
      Alert.alert('Validation Error', 'Please enter full address');
      return false;
    }
    if (formData.aadhaar_number.length !== 12) {
      Alert.alert('Validation Error', 'Aadhaar must be 12 digits');
      return false;
    }
    if (formData.pan_number.length !== 10) {
      Alert.alert('Validation Error', 'PAN must be 10 characters');
      return false;
    }
    if (!formData.driving_license_number.trim()) {
      Alert.alert('Validation Error', 'Please enter license number');
      return false;
    }
    if (!formData.driver_photo) {
      Alert.alert('Validation Error', 'Please upload driver photo');
      return false;
    }
    if (!formData.account_holder_name.trim()) {
      Alert.alert('Validation Error', 'Please enter account holder name');
      return false;
    }
    if (!formData.bank_name.trim()) {
      Alert.alert('Validation Error', 'Please enter bank name');
      return false;
    }
    if (formData.account_number.length < 9) {
      Alert.alert('Validation Error', 'Invalid account number');
      return false;
    }
    if (formData.ifsc_code.length !== 11) {
      Alert.alert('Validation Error', 'IFSC must be 11 characters');
      return false;
    }
    if (!formData.vehicle_number.trim()) {
      Alert.alert('Validation Error', 'Please enter vehicle number');
      return false;
    }
    if (!formData.vehicle_model.trim()) {
      Alert.alert('Validation Error', 'Please enter vehicle model');
      return false;
    }
    return true;
  };

  const validateSection2 = () => {
    const docs = [
      { field: 'aadhaar_doc', name: 'Aadhaar' },
      { field: 'pan_doc', name: 'PAN Card' },
      { field: 'license_doc', name: 'Driving License' },
      { field: 'rc_doc', name: 'RC Book' },
      { field: 'insurance_doc', name: 'Insurance' },
      { field: 'fc_doc', name: 'Fitness Certificate' },
      { field: 'permit_doc', name: 'Permit' },
      { field: 'pollution_doc', name: 'Pollution Certificate' },
    ];

    for (const doc of docs) {
      if (!formData[doc.field as keyof typeof formData]) {
        Alert.alert('Validation Error', `Please upload ${doc.name}`);
        return false;
      }
    }

    // Validate expiry dates
    const dates = [
      { field: 'insurance_expiry', name: 'Insurance' },
      { field: 'fc_expiry', name: 'FC' },
      { field: 'permit_expiry', name: 'Permit' },
      { field: 'pollution_expiry', name: 'Pollution' },
      { field: 'license_expiry', name: 'License' },
    ];

    for (const date of dates) {
      if (!formData[date.field as keyof typeof formData]) {
        Alert.alert('Validation Error', `Please enter ${date.name} expiry date`);
        return false;
      }
    }

    return true;
  };

  const validateSection3 = () => {
    if (!formData.driver_vehicle_photo) {
      Alert.alert('Validation Error', 'Driver + Vehicle photo is mandatory');
      return false;
    }
    return true;
  };

  const handleNext = () => {
    if (currentSection === 1 && validateSection1()) {
      setCurrentSection(2);
    } else if (currentSection === 2 && validateSection2()) {
      setCurrentSection(3);
    }
  };

  const handleSubmit = async () => {
    if (!validateSection3()) return;

    setLoading(true);
    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

      const payload = {
        phone: phone as string,
        personal_details: {
          full_name: formData.full_name,
          mobile_number: formData.mobile_number,
          full_address: formData.full_address,
          aadhaar_number: formData.aadhaar_number,
          pan_number: formData.pan_number.toUpperCase(),
          driving_license_number: formData.driving_license_number,
          driving_experience_years: parseInt(formData.driving_experience_years),
          driver_photo: formData.driver_photo,
        },
        bank_details: {
          account_holder_name: formData.account_holder_name,
          bank_name: formData.bank_name,
          account_number: formData.account_number,
          ifsc_code: formData.ifsc_code.toUpperCase(),
          branch_name: formData.branch_name,
        },
        vehicle_details: {
          vehicle_type: formData.vehicle_type,
          vehicle_number: formData.vehicle_number.toUpperCase(),
          vehicle_model: formData.vehicle_model,
          vehicle_year: parseInt(formData.vehicle_year),
        },
        documents: {
          aadhaar_card: { front_image: formData.aadhaar_doc, back_image: null },
          pan_card: { front_image: formData.pan_doc, back_image: null },
          driving_license: { front_image: formData.license_doc, back_image: null },
          rc_book: { front_image: formData.rc_doc, back_image: null },
          insurance: { front_image: formData.insurance_doc, back_image: null },
          fitness_certificate: { front_image: formData.fc_doc, back_image: null },
          permit: { front_image: formData.permit_doc, back_image: null },
          pollution_certificate: { front_image: formData.pollution_doc, back_image: null },
        },
        document_expiry: {
          insurance_expiry: formData.insurance_expiry,
          fc_expiry: formData.fc_expiry,
          permit_expiry: formData.permit_expiry,
          pollution_expiry: formData.pollution_expiry,
          license_expiry: formData.license_expiry,
        },
        driver_vehicle_photo: {
          photo: formData.driver_vehicle_photo,
        },
      };

      const response = await axios.post(`${API_URL}/api/driver/register-kyc`, payload);

      if (response.data.success) {
        Alert.alert(
          'Registration Successful!',
          'Your application has been submitted. Admin will review and approve soon.',
          [{ text: 'OK', onPress: () => router.replace('/') }]
        );
      }
    } catch (error: any) {
      Alert.alert(
        'Registration Failed',
        error.response?.data?.detail || 'Please check all fields and try again.'
      );
      console.error('Registration error:', error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const renderImagePicker = (field: string, label: string) => (
    <View style={styles.imagePickerContainer}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.imageActions}>
        <TouchableOpacity
          style={styles.imageButton}
          onPress={() => takePhoto(field)}
        >
          <Ionicons name="camera" size={24} color={Colors.white} />
          <Text style={styles.imageButtonText}>Camera</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.imageButton, styles.galleryButton]}
          onPress={() => pickImage(field)}
        >
          <Ionicons name="images" size={24} color={Colors.white} />
          <Text style={styles.imageButtonText}>Gallery</Text>
        </TouchableOpacity>
      </View>
      {formData[field as keyof typeof formData] && (
        <View style={styles.imagePreview}>
          <Image
            source={{ uri: formData[field as keyof typeof formData] as string }}
            style={styles.previewImage}
          />
          <Ionicons name="checkmark-circle" size={24} color={Colors.success} style={styles.checkmark} />
        </View>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.white} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>Driver Registration</Text>
          <Text style={styles.headerSubtitle}>Section {currentSection} of 3</Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {currentSection === 1 && (
          <View>
            <Text style={styles.sectionTitle}>Personal & Bank & Vehicle Details</Text>
            
            <Input
              label="Full Name *"
              placeholder="Enter your full name"
              value={formData.full_name}
              onChangeText={(text) => setFormData({ ...formData, full_name: text })}
            />

            <Input
              label="Full Address *"
              placeholder="Complete address"
              value={formData.full_address}
              onChangeText={(text) => setFormData({ ...formData, full_address: text })}
              multiline
            />

            <Input
              label="Aadhaar Number *"
              placeholder="12 digit Aadhaar"
              value={formData.aadhaar_number}
              onChangeText={(text) => setFormData({ ...formData, aadhaar_number: text.replace(/\D/g, '') })}
              keyboardType="number-pad"
              maxLength={12}
            />

            <Input
              label="PAN Number *"
              placeholder="10 character PAN"
              value={formData.pan_number}
              onChangeText={(text) => setFormData({ ...formData, pan_number: text.toUpperCase() })}
              maxLength={10}
              autoCapitalize="characters"
            />

            <Input
              label="Driving License Number *"
              placeholder="License number"
              value={formData.driving_license_number}
              onChangeText={(text) => setFormData({ ...formData, driving_license_number: text })}
            />

            <Input
              label="Driving Experience (Years) *"
              placeholder="Years"
              value={formData.driving_experience_years}
              onChangeText={(text) => setFormData({ ...formData, driving_experience_years: text.replace(/\D/g, '') })}
              keyboardType="number-pad"
            />

            {renderImagePicker('driver_photo', 'Driver Photo *')}

            <Text style={[styles.sectionTitle, { marginTop: 24 }]}>Bank Details</Text>

            <Input
              label="Account Holder Name *"
              placeholder="As per bank"
              value={formData.account_holder_name}
              onChangeText={(text) => setFormData({ ...formData, account_holder_name: text })}
            />

            <Input
              label="Bank Name *"
              placeholder="Bank name"
              value={formData.bank_name}
              onChangeText={(text) => setFormData({ ...formData, bank_name: text })}
            />

            <Input
              label="Account Number *"
              placeholder="Account number"
              value={formData.account_number}
              onChangeText={(text) => setFormData({ ...formData, account_number: text.replace(/\D/g, '') })}
              keyboardType="number-pad"
            />

            <Input
              label="IFSC Code *"
              placeholder="11 character IFSC"
              value={formData.ifsc_code}
              onChangeText={(text) => setFormData({ ...formData, ifsc_code: text.toUpperCase() })}
              maxLength={11}
              autoCapitalize="characters"
            />

            <Input
              label="Branch Name"
              placeholder="Branch name"
              value={formData.branch_name}
              onChangeText={(text) => setFormData({ ...formData, branch_name: text })}
            />

            <Text style={[styles.sectionTitle, { marginTop: 24 }]}>Vehicle Details</Text>

            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Vehicle Type *</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={formData.vehicle_type}
                  onValueChange={(value) => setFormData({ ...formData, vehicle_type: value })}
                >
                  <Picker.Item label="Sedan (₹14/km)" value="sedan" />
                  <Picker.Item label="SUV (₹18/km)" value="suv" />
                </Picker>
              </View>
            </View>

            <Input
              label="Vehicle Number *"
              placeholder="e.g., MH12AB1234"
              value={formData.vehicle_number}
              onChangeText={(text) => setFormData({ ...formData, vehicle_number: text.toUpperCase() })}
              autoCapitalize="characters"
            />

            <Input
              label="Vehicle Model *"
              placeholder="e.g., Swift Dzire"
              value={formData.vehicle_model}
              onChangeText={(text) => setFormData({ ...formData, vehicle_model: text })}
            />

            <Input
              label="Vehicle Year *"
              placeholder="Year"
              value={formData.vehicle_year}
              onChangeText={(text) => setFormData({ ...formData, vehicle_year: text.replace(/\D/g, '') })}
              keyboardType="number-pad"
              maxLength={4}
            />

            <Button title="Next: Documents" onPress={handleNext} variant="secondary" />
          </View>
        )}

        {currentSection === 2 && (
          <View>
            <Text style={styles.sectionTitle}>Documents & Expiry Dates</Text>
            
            {renderImagePicker('aadhaar_doc', 'Aadhaar Card *')}
            {renderImagePicker('pan_doc', 'PAN Card *')}
            {renderImagePicker('license_doc', 'Driving License *')}
            {renderImagePicker('rc_doc', 'RC Book *')}
            {renderImagePicker('insurance_doc', 'Insurance *')}
            {renderImagePicker('fc_doc', 'Fitness Certificate *')}
            {renderImagePicker('permit_doc', 'Permit *')}
            {renderImagePicker('pollution_doc', 'Pollution Certificate *')}

            <Text style={[styles.sectionTitle, { marginTop: 24 }]}>Expiry Dates (YYYY-MM-DD)</Text>

            <Input
              label="Insurance Expiry *"
              placeholder="YYYY-MM-DD"
              value={formData.insurance_expiry}
              onChangeText={(text) => setFormData({ ...formData, insurance_expiry: text })}
            />

            <Input
              label="FC Expiry *"
              placeholder="YYYY-MM-DD"
              value={formData.fc_expiry}
              onChangeText={(text) => setFormData({ ...formData, fc_expiry: text })}
            />

            <Input
              label="Permit Expiry *"
              placeholder="YYYY-MM-DD"
              value={formData.permit_expiry}
              onChangeText={(text) => setFormData({ ...formData, permit_expiry: text })}
            />

            <Input
              label="Pollution Expiry *"
              placeholder="YYYY-MM-DD"
              value={formData.pollution_expiry}
              onChangeText={(text) => setFormData({ ...formData, pollution_expiry: text })}
            />

            <Input
              label="License Expiry *"
              placeholder="YYYY-MM-DD"
              value={formData.license_expiry}
              onChangeText={(text) => setFormData({ ...formData, license_expiry: text })}
            />

            <View style={styles.buttonGroup}>
              <Button
                title="Back"
                onPress={() => setCurrentSection(1)}
                variant="outline"
                style={styles.halfButton}
              />
              <Button
                title="Next: Final Photo"
                onPress={handleNext}
                variant="secondary"
                style={styles.halfButton}
              />
            </View>
          </View>
        )}

        {currentSection === 3 && (
          <View>
            <Text style={styles.sectionTitle}>Driver + Vehicle Verification Photo</Text>
            <Text style={styles.instructionText}>
              Take a photo of yourself standing near your vehicle with the number plate clearly visible.
              This is mandatory for verification.
            </Text>

            {renderImagePicker('driver_vehicle_photo', 'Driver + Vehicle Photo *')}

            <View style={styles.buttonGroup}>
              <Button
                title="Back"
                onPress={() => setCurrentSection(2)}
                variant="outline"
                style={styles.halfButton}
              />
              <Button
                title="Submit Registration"
                onPress={handleSubmit}
                loading={loading}
                variant="secondary"
                style={styles.halfButton}
              />
            </View>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.white,
  },
  header: {
    backgroundColor: Colors.secondary,
    padding: 16,
    paddingTop: 60,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.white,
  },
  headerSubtitle: {
    fontSize: 14,
    color: Colors.white,
    opacity: 0.9,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  instructionText: {
    fontSize: 14,
    color: Colors.textLight,
    marginBottom: 16,
    lineHeight: 20,
  },
  imagePickerContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 8,
  },
  imageActions: {
    flexDirection: 'row',
    gap: 12,
  },
  imageButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Colors.secondary,
    padding: 12,
    borderRadius: 12,
    gap: 8,
  },
  galleryButton: {
    backgroundColor: Colors.primary,
  },
  imageButtonText: {
    color: Colors.white,
    fontSize: 14,
    fontWeight: '600',
  },
  imagePreview: {
    marginTop: 12,
    position: 'relative',
  },
  previewImage: {
    width: '100%',
    height: 150,
    borderRadius: 12,
    backgroundColor: Colors.lightGray,
  },
  checkmark: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 12,
    backgroundColor: Colors.white,
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  halfButton: {
    flex: 1,
  },
});
