import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { MapViewWrapper, MarkerWrapper } from '../../components/MapViewWrapper';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Colors } from '../../utils/colors';
import { createBooking } from '../../utils/api';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';

// Conditional import for expo-location
let Location: any = null;
if (Platform.OS !== 'web') {
  Location = require('expo-location');
}

export default function CustomerHomeScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const [currentLocation, setCurrentLocation] = useState<any>(null);
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropAddress, setDropAddress] = useState('');
  const [vehicleType, setVehicleType] = useState<'sedan' | 'suv'>('sedan');
  const [estimatedFare, setEstimatedFare] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);

  // Mock coordinates for pickup and drop
  const [pickupCoords, setPickupCoords] = useState({ latitude: 19.0760, longitude: 72.8777 });
  const [dropCoords, setDropCoords] = useState({ latitude: 19.0896, longitude: 72.8656 });

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = async () => {
    if (Platform.OS === 'web') {
      // Use mock location for web
      setCurrentLocation({ latitude: 19.0760, longitude: 72.8777 });
      setPickupAddress('Current Location (Web - Mock)');
      return;
    }

    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location permission is required');
        // Use mock location
        setCurrentLocation({ latitude: 19.0760, longitude: 72.8777 });
        setPickupAddress('Current Location (Mock)');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setCurrentLocation({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
      setPickupCoords({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
      setPickupAddress('Current Location');
    } catch (error) {
      // Use mock location
      setCurrentLocation({ latitude: 19.0760, longitude: 72.8777 });
      setPickupAddress('Current Location (Mock)');
    }
  };

  const calculateFare = () => {
    // Mock distance calculation
    const distance = Math.sqrt(
      Math.pow(pickupCoords.latitude - dropCoords.latitude, 2) +
      Math.pow(pickupCoords.longitude - dropCoords.longitude, 2)
    ) * 111; // Convert to km

    const rate = vehicleType === 'sedan' ? 14 : 18;
    const fare = Math.max(distance * rate, 300);
    setEstimatedFare(Math.round(fare));
  };

  const handleBookRide = async () => {
    if (!pickupAddress || !dropAddress) {
      Alert.alert('Error', 'Please enter pickup and drop locations');
      return;
    }

    setLoading(true);
    try {
      const response = await createBooking({
        customer_id: user?.user_id,
        pickup: {
          latitude: pickupCoords.latitude,
          longitude: pickupCoords.longitude,
          address: pickupAddress,
        },
        drop: {
          latitude: dropCoords.latitude,
          longitude: dropCoords.longitude,
          address: dropAddress,
        },
        vehicle_type: vehicleType,
      });

      if (response.data.success) {
        setShowBookingModal(false);
        Alert.alert(
          'Booking Confirmed!',
          `Booking ID: ${response.data.booking.booking_id}\nDriver: ${response.data.booking.driver_name}\nFare: ₹${response.data.booking.fare}`,
          [
            {
              text: 'View Details',
              onPress: () => router.push(`/customer/booking-details?id=${response.data.booking.booking_id}`),
            },
            { text: 'OK' },
          ]
        );
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.name}!</Text>
          <Text style={styles.subtitle}>Where are you going?</Text>
        </View>
        <TouchableOpacity onPress={logout} style={styles.logoutButton}>
          <Ionicons name="log-out-outline" size={24} color={Colors.error} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Map */}
        <View style={styles.mapContainer}>
          {currentLocation ? (
            <MapViewWrapper
              style={styles.map}
              initialRegion={{
                latitude: currentLocation.latitude,
                longitude: currentLocation.longitude,
                latitudeDelta: 0.05,
                longitudeDelta: 0.05,
              }}
            >
              <MarkerWrapper coordinate={pickupCoords} title="Pickup" pinColor={Colors.primary} />
              <MarkerWrapper coordinate={dropCoords} title="Drop" pinColor={Colors.secondary} />
            </MapViewWrapper>
          ) : (
            <View style={styles.mapPlaceholder}>
              <Ionicons name="map" size={40} color={Colors.gray} />
              <Text style={styles.mapPlaceholderText}>Loading map...</Text>
            </View>
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => setShowBookingModal(true)}
          >
            <Ionicons name="add-circle" size={40} color={Colors.primary} />
            <Text style={styles.actionText}>Book Ride</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push('/customer/history')}
          >
            <Ionicons name="time" size={40} color={Colors.secondary} />
            <Text style={styles.actionText}>History</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push('/customer/wallet')}
          >
            <Ionicons name="wallet" size={40} color={Colors.primary} />
            <Text style={styles.actionText}>Wallet</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Booking Modal */}
      <Modal
        visible={showBookingModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowBookingModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Book a Ride</Text>
              <TouchableOpacity onPress={() => setShowBookingModal(false)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            <ScrollView>
              <Input
                label="Pickup Location"
                value={pickupAddress}
                onChangeText={setPickupAddress}
                placeholder="Enter pickup location"
              />

              <Input
                label="Drop Location"
                value={dropAddress}
                onChangeText={setDropAddress}
                placeholder="Enter drop location"
              />

              <View style={styles.inputContainer}>
                <Text style={styles.label}>Vehicle Type</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={vehicleType}
                    onValueChange={(value) => setVehicleType(value as 'sedan' | 'suv')}
                  >
                    <Picker.Item label="Sedan (₹14/km)" value="sedan" />
                    <Picker.Item label="SUV (₹18/km)" value="suv" />
                  </Picker>
                </View>
              </View>

              {estimatedFare && (
                <View style={styles.fareCard}>
                  <Text style={styles.fareLabel}>Estimated Fare</Text>
                  <Text style={styles.fareAmount}>₹{estimatedFare}</Text>
                </View>
              )}

              <Button
                title="Calculate Fare"
                onPress={calculateFare}
                variant="outline"
                style={styles.calculateButton}
              />

              <Button
                title="Confirm Booking"
                onPress={handleBookRide}
                loading={loading}
                variant="primary"
              />
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.white,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: Colors.primary,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 4,
  },
  logoutButton: {
    padding: 8,
  },
  content: {
    flex: 1,
  },
  mapContainer: {
    height: 300,
    margin: 16,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: Colors.lightGray,
  },
  map: {
    flex: 1,
  },
  mapPlaceholder: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mapPlaceholderText: {
    marginTop: 8,
    color: Colors.gray,
  },
  quickActions: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: Colors.white,
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: Colors.white,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
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
  fareCard: {
    backgroundColor: Colors.lightGray,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  fareLabel: {
    fontSize: 14,
    color: Colors.textLight,
  },
  fareAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: Colors.primary,
    marginTop: 4,
  },
  calculateButton: {
    marginBottom: 12,
  },
});
