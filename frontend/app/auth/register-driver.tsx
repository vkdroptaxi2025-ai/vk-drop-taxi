import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  TouchableOpacity,
  Image,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { Colors } from '../../utils/colors';
import { registerDriver } from '../../utils/api';
import { useAuthStore } from '../../store/authStore';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';

// Conditional import for expo-image-picker
let ImagePicker: any = null;
if (Platform.OS !== 'web') {
  ImagePicker = require('expo-image-picker');
}

export default function RegisterDriverScreen() {
  const router = useRouter();
  const { phone } = useLocalSearchParams();
  const { setUser } = useAuthStore();

  const [name, setName] = useState('');
  const [vehicleType, setVehicleType] = useState<'sedan' | 'suv'>('sedan');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [licenseImage, setLicenseImage] = useState<string | null>(null);
  const [rcImage, setRcImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async (type: 'license' | 'rc') => {
    if (Platform.OS === 'web') {
      Alert.alert('Not Available', 'Image upload works on mobile app. Using placeholder for web.');
      const placeholder = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
      if (type === 'license') {
        setLicenseImage(placeholder);
      } else {
        setRcImage(placeholder);
      }
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
      const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
      if (type === 'license') {
        setLicenseImage(base64Image);
      } else {
        setRcImage(base64Image);
      }
    }
  };

  const handleRegister = async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter your name');
      return;
    }
    if (!vehicleNumber.trim()) {
      Alert.alert('Error', 'Please enter vehicle number');
      return;
    }
    if (!licenseImage) {
      Alert.alert('Error', 'Please upload driving license');
      return;
    }
    if (!rcImage) {
      Alert.alert('Error', 'Please upload RC document');
      return;
    }

    setLoading(true);
    try {
      const response = await registerDriver({
        phone,
        name: name.trim(),
        vehicle_type: vehicleType,
        vehicle_number: vehicleNumber.trim().toUpperCase(),
        license_image: licenseImage,
        rc_image: rcImage,
      });

      if (response.data.success) {
        await setUser(response.data.driver);
        Alert.alert(
          'Success',
          'Registration submitted! Your account is under review.',
          [{ text: 'OK', onPress: () => router.replace('/driver/dashboard') }]
        );
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Registration failed');
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
          <Ionicons name="car-sport" size={80} color={Colors.secondary} />
          <Text style={styles.title}>Driver Registration</Text>
          <Text style={styles.subtitle}>Complete your profile</Text>
        </View>

        <View style={styles.form}>
          <Input
            label="Phone Number"
            value={phone as string}
            editable={false}
          />

          <Input
            label="Full Name"
            placeholder="Enter your name"
            value={name}
            onChangeText={setName}
          />

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Vehicle Type</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={vehicleType}
                onValueChange={(value) => setVehicleType(value as 'sedan' | 'suv')}
                style={styles.picker}
              >
                <Picker.Item label="Sedan (₹14/km)" value="sedan" />
                <Picker.Item label="SUV (₹18/km)" value="suv" />
              </Picker>
            </View>
          </View>

          <Input
            label="Vehicle Number"
            placeholder="e.g., MH12AB1234"
            value={vehicleNumber}
            onChangeText={setVehicleNumber}
            autoCapitalize="characters"
          />

          {/* License Upload */}
          <View style={styles.uploadSection}>
            <Text style={styles.label}>Driving License</Text>
            <TouchableOpacity
              style={styles.uploadButton}
              onPress={() => pickImage('license')}
            >
              {licenseImage ? (
                <Image source={{ uri: licenseImage }} style={styles.previewImage} />
              ) : (
                <View style={styles.uploadPlaceholder}>
                  <Ionicons name="cloud-upload" size={40} color={Colors.gray} />
                  <Text style={styles.uploadText}>Upload License</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>

          {/* RC Upload */}
          <View style={styles.uploadSection}>
            <Text style={styles.label}>Vehicle RC</Text>
            <TouchableOpacity
              style={styles.uploadButton}
              onPress={() => pickImage('rc')}
            >
              {rcImage ? (
                <Image source={{ uri: rcImage }} style={styles.previewImage} />
              ) : (
                <View style={styles.uploadPlaceholder}>
                  <Ionicons name="cloud-upload" size={40} color={Colors.gray} />
                  <Text style={styles.uploadText}>Upload RC</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>

          <Button
            title="Submit Registration"
            onPress={handleRegister}
            loading={loading}
            variant="secondary"
          />
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
    marginBottom: 32,
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
  },
  form: {
    gap: 8,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 8,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 12,
    backgroundColor: Colors.white,
  },
  picker: {
    height: 50,
  },
  uploadSection: {
    marginBottom: 16,
  },
  uploadButton: {
    borderWidth: 2,
    borderColor: Colors.border,
    borderRadius: 12,
    borderStyle: 'dashed',
    overflow: 'hidden',
  },
  uploadPlaceholder: {
    height: 150,
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadText: {
    marginTop: 8,
    fontSize: 14,
    color: Colors.gray,
  },
  previewImage: {
    width: '100%',
    height: 150,
    resizeMode: 'cover',
  },
});