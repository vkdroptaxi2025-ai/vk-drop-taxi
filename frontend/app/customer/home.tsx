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
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { MapViewWrapper, MarkerWrapper } from '../../components/MapViewWrapper';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Colors } from '../../utils/colors';
import { createSmartBooking, getTariffs } from '../../utils/api';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';
import DateTimePicker from '@react-native-community/datetimepicker';

// Mock location for web
let Location: any = null;
if (Platform.OS !== 'web') {
  Location = require('expo-location');
}

type TripType = 'one_way' | 'round_trip' | 'local_package';
type VehicleType = 'sedan' | 'suv';

export default function CustomerHomeScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  // Location state
  const [currentLocation, setCurrentLocation] = useState<any>(null);
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropAddress, setDropAddress] = useState('');
  const [pickupCoords, setPickupCoords] = useState({ latitude: 12.97, longitude: 80.24 });
  const [dropCoords, setDropCoords] = useState({ latitude: 13.08, longitude: 80.27 });

  // Booking options
  const [tripType, setTripType] = useState<TripType>('one_way');
  const [vehicleType, setVehicleType] = useState<VehicleType>('sedan');
  const [travelDate, setTravelDate] = useState(new Date());
  const [travelTime, setTravelTime] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);

  // Fare and booking
  const [estimatedFare, setEstimatedFare] = useState<number | null>(null);
  const [estimatedDistance, setEstimatedDistance] = useState<number | null>(null);
  const [tariffs, setTariffs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);

  useEffect(() => {
    getCurrentLocation();
    fetchTariffs();
  }, []);

  const getCurrentLocation = async () => {
    if (Platform.OS === 'web') {
      setCurrentLocation({ latitude: 12.97, longitude: 80.24 });
      setPickupAddress('Current Location (Web)');
      return;
    }

    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setCurrentLocation({ latitude: 12.97, longitude: 80.24 });
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
      setCurrentLocation({ latitude: 12.97, longitude: 80.24 });
      setPickupAddress('Current Location (Mock)');
    }
  };

  const fetchTariffs = async () => {
    try {
      const response = await getTariffs();
      setTariffs(response.data.tariffs || []);
    } catch (error) {
      console.error('Failed to fetch tariffs:', error);
    }
  };

  const calculateFare = () => {
    if (!pickupAddress || !dropAddress) {
      Alert.alert('Error', 'Please enter pickup and drop locations');
      return;
    }

    // Calculate distance using Haversine formula
    const R = 6371; // Earth radius in km
    const lat1 = pickupCoords.latitude * Math.PI / 180;
    const lat2 = dropCoords.latitude * Math.PI / 180;
    const deltaLat = (dropCoords.latitude - pickupCoords.latitude) * Math.PI / 180;
    const deltaLon = (dropCoords.longitude - pickupCoords.longitude) * Math.PI / 180;

    const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(deltaLon/2) * Math.sin(deltaLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    let distance = R * c;

    // Apply trip type multiplier
    if (tripType === 'round_trip') {
      distance = distance * 2;
    } else if (tripType === 'local_package') {
      distance = Math.max(distance, 50); // Minimum 50km for local package
    }

    // Get rate from tariffs
    const tariff = tariffs.find(t => t.vehicle_type === vehicleType);
    const rate = tariff ? tariff.rate_per_km : (vehicleType === 'sedan' ? 14 : 18);
    const minFare = tariff ? tariff.minimum_fare : 300;

    const fare = Math.max(distance * rate, minFare);
    
    setEstimatedDistance(Math.round(distance * 100) / 100);
    setEstimatedFare(Math.round(fare));
  };

  const handleBookRide = async () => {
    if (!pickupAddress || !dropAddress) {
      Alert.alert('Error', 'Please enter pickup and drop locations');
      return;
    }

    if (!estimatedFare) {
      Alert.alert('Error', 'Please calculate fare first');
      return;
    }

    setLoading(true);
    try {
      const response = await createSmartBooking({
        customer_id: user?.user_id || '',
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
        assignment_mode: 'auto',
      });

      if (response.data.success) {
        setShowBookingModal(false);
        Alert.alert(
          'Booking Confirmed!',
          `Booking ID: ${response.data.booking.booking_id.slice(0, 8)}\nDriver: ${response.data.booking.driver_name || 'Assigned'}\nFare: ₹${response.data.booking.fare}`,
          [
            {
              text: 'View Details',
              onPress: () => router.push(`/customer/booking-details?id=${response.data.booking.booking_id}`),
            },
            { text: 'OK' },
          ]
        );
        // Reset form
        setDropAddress('');
        setEstimatedFare(null);
        setEstimatedDistance(null);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'No drivers available. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  };

  const onDateChange = (event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (selectedDate) {
      setTravelDate(selectedDate);
    }
  };

  const onTimeChange = (event: any, selectedTime?: Date) => {
    setShowTimePicker(false);
    if (selectedTime) {
      setTravelTime(selectedTime);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.name || 'Customer'}!</Text>
          <Text style={styles.subtitle}>Where would you like to go?</Text>
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
                latitudeDelta: 0.1,
                longitudeDelta: 0.1,
              }}
            >
              <MarkerWrapper coordinate={pickupCoords} title="Pickup" pinColor={Colors.primary} />
              {dropAddress && (
                <MarkerWrapper coordinate={dropCoords} title="Drop" pinColor={Colors.secondary} />
              )}
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
            style={[styles.actionCard, styles.mainAction]}
            onPress={() => setShowBookingModal(true)}
          >
            <Ionicons name="car" size={36} color={Colors.white} />
            <Text style={styles.mainActionText}>Book a Ride</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push('/customer/history')}
          >
            <Ionicons name="time" size={28} color={Colors.secondary} />
            <Text style={styles.actionText}>History</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push('/customer/wallet')}
          >
            <Ionicons name="wallet" size={28} color={Colors.primary} />
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

            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Trip Type Selection */}
              <Text style={styles.sectionLabel}>Trip Type</Text>
              <View style={styles.tripTypeContainer}>
                {[
                  { value: 'one_way', label: 'One Way', icon: 'arrow-forward' },
                  { value: 'round_trip', label: 'Round Trip', icon: 'repeat' },
                  { value: 'local_package', label: 'Local Package', icon: 'location' },
                ].map((type) => (
                  <TouchableOpacity
                    key={type.value}
                    style={[
                      styles.tripTypeBtn,
                      tripType === type.value && styles.tripTypeBtnActive,
                    ]}
                    onPress={() => setTripType(type.value as TripType)}
                  >
                    <Ionicons
                      name={type.icon as any}
                      size={20}
                      color={tripType === type.value ? Colors.white : Colors.text}
                    />
                    <Text
                      style={[
                        styles.tripTypeText,
                        tripType === type.value && styles.tripTypeTextActive,
                      ]}
                    >
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* Pickup & Drop */}
              <Input
                label="Pickup Location"
                value={pickupAddress}
                onChangeText={setPickupAddress}
                placeholder="Enter pickup address"
              />

              <Input
                label="Drop Location"
                value={dropAddress}
                onChangeText={setDropAddress}
                placeholder="Enter drop address"
              />

              {/* Date & Time */}
              <View style={styles.dateTimeRow}>
                <View style={styles.dateTimeItem}>
                  <Text style={styles.inputLabel}>Date</Text>
                  <TouchableOpacity
                    style={styles.dateTimeBtn}
                    onPress={() => setShowDatePicker(true)}
                  >
                    <Ionicons name="calendar" size={18} color={Colors.secondary} />
                    <Text style={styles.dateTimeText}>{formatDate(travelDate)}</Text>
                  </TouchableOpacity>
                </View>

                <View style={styles.dateTimeItem}>
                  <Text style={styles.inputLabel}>Time</Text>
                  <TouchableOpacity
                    style={styles.dateTimeBtn}
                    onPress={() => setShowTimePicker(true)}
                  >
                    <Ionicons name="time" size={18} color={Colors.secondary} />
                    <Text style={styles.dateTimeText}>{formatTime(travelTime)}</Text>
                  </TouchableOpacity>
                </View>
              </View>

              {/* Vehicle Type */}
              <Text style={styles.sectionLabel}>Vehicle Type</Text>
              <View style={styles.vehicleContainer}>
                <TouchableOpacity
                  style={[
                    styles.vehicleBtn,
                    vehicleType === 'sedan' && styles.vehicleBtnActive,
                  ]}
                  onPress={() => setVehicleType('sedan')}
                >
                  <Ionicons
                    name="car-sport"
                    size={28}
                    color={vehicleType === 'sedan' ? Colors.white : Colors.text}
                  />
                  <Text
                    style={[
                      styles.vehicleText,
                      vehicleType === 'sedan' && styles.vehicleTextActive,
                    ]}
                  >
                    Sedan
                  </Text>
                  <Text
                    style={[
                      styles.vehicleRate,
                      vehicleType === 'sedan' && styles.vehicleRateActive,
                    ]}
                  >
                    ₹14/km
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[
                    styles.vehicleBtn,
                    vehicleType === 'suv' && styles.vehicleBtnActive,
                  ]}
                  onPress={() => setVehicleType('suv')}
                >
                  <Ionicons
                    name="car"
                    size={28}
                    color={vehicleType === 'suv' ? Colors.white : Colors.text}
                  />
                  <Text
                    style={[
                      styles.vehicleText,
                      vehicleType === 'suv' && styles.vehicleTextActive,
                    ]}
                  >
                    SUV
                  </Text>
                  <Text
                    style={[
                      styles.vehicleRate,
                      vehicleType === 'suv' && styles.vehicleRateActive,
                    ]}
                  >
                    ₹18/km
                  </Text>
                </TouchableOpacity>
              </View>

              {/* Calculate Fare Button */}
              <Button
                title="Calculate Fare"
                onPress={calculateFare}
                variant="outline"
                style={styles.calculateBtn}
              />

              {/* Fare Estimate */}
              {estimatedFare && (
                <View style={styles.fareCard}>
                  <View style={styles.fareRow}>
                    <Text style={styles.fareLabel}>Distance</Text>
                    <Text style={styles.fareValue}>{estimatedDistance} km</Text>
                  </View>
                  <View style={styles.fareRow}>
                    <Text style={styles.fareLabel}>Trip Type</Text>
                    <Text style={styles.fareValue}>
                      {tripType === 'one_way' ? 'One Way' : tripType === 'round_trip' ? 'Round Trip' : 'Local Package'}
                    </Text>
                  </View>
                  <View style={styles.fareDivider} />
                  <View style={styles.fareRow}>
                    <Text style={styles.fareTotalLabel}>Estimated Fare</Text>
                    <Text style={styles.fareTotalValue}>₹{estimatedFare}</Text>
                  </View>
                </View>
              )}

              {/* Book Button */}
              <Button
                title="Confirm Booking"
                onPress={handleBookRide}
                loading={loading}
                variant="primary"
                disabled={!estimatedFare}
              />
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Date Picker */}
      {showDatePicker && (
        <DateTimePicker
          value={travelDate}
          mode="date"
          display="default"
          onChange={onDateChange}
          minimumDate={new Date()}
        />
      )}

      {/* Time Picker */}
      {showTimePicker && (
        <DateTimePicker
          value={travelTime}
          mode="time"
          display="default"
          onChange={onTimeChange}
        />
      )}

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
    fontSize: 22,
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
    height: 250,
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
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  mainAction: {
    flex: 2,
    backgroundColor: Colors.secondary,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
  },
  mainActionText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.white,
  },
  actionText: {
    marginTop: 6,
    fontSize: 13,
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
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: Colors.text,
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 10,
    marginTop: 8,
  },
  tripTypeContainer: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  tripTypeBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 4,
  },
  tripTypeBtnActive: {
    backgroundColor: Colors.secondary,
    borderColor: Colors.secondary,
  },
  tripTypeText: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.text,
  },
  tripTypeTextActive: {
    color: Colors.white,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 8,
  },
  dateTimeRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  dateTimeItem: {
    flex: 1,
  },
  dateTimeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.white,
  },
  dateTimeText: {
    fontSize: 14,
    color: Colors.text,
  },
  vehicleContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  vehicleBtn: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: Colors.border,
    backgroundColor: Colors.white,
  },
  vehicleBtnActive: {
    backgroundColor: Colors.secondary,
    borderColor: Colors.secondary,
  },
  vehicleText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  vehicleTextActive: {
    color: Colors.white,
  },
  vehicleRate: {
    fontSize: 13,
    color: Colors.textLight,
    marginTop: 4,
  },
  vehicleRateActive: {
    color: Colors.white,
    opacity: 0.9,
  },
  calculateBtn: {
    marginBottom: 12,
  },
  fareCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  fareRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  fareLabel: {
    fontSize: 14,
    color: Colors.textLight,
  },
  fareValue: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  fareDivider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 8,
  },
  fareTotalLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
  },
  fareTotalValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255,255,255,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
