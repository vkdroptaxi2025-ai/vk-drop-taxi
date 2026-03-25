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
import { LinearGradient } from 'expo-linear-gradient';
import { MapViewWrapper, MarkerWrapper } from '../../components/MapViewWrapper';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Colors } from '../../utils/colors';
import { createSmartBooking, getTariffs } from '../../utils/api';
import { Ionicons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';

let Location: any = null;
if (Platform.OS !== 'web') {
  Location = require('expo-location');
}

type TripType = 'one_way' | 'round_trip' | 'local_package';
type VehicleType = 'sedan' | 'suv';

export default function CustomerHomeScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const [currentLocation, setCurrentLocation] = useState<any>(null);
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropAddress, setDropAddress] = useState('');
  const [pickupCoords, setPickupCoords] = useState({ latitude: 12.97, longitude: 80.24 });
  const [dropCoords, setDropCoords] = useState({ latitude: 13.08, longitude: 80.27 });

  const [tripType, setTripType] = useState<TripType>('one_way');
  const [vehicleType, setVehicleType] = useState<VehicleType>('sedan');
  const [travelDate, setTravelDate] = useState(new Date());
  const [travelTime, setTravelTime] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);

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
      setPickupAddress('Current Location');
      return;
    }
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setCurrentLocation({ latitude: 12.97, longitude: 80.24 });
        setPickupAddress('Current Location');
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
      setPickupAddress('Current Location');
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

    const R = 6371;
    const lat1 = pickupCoords.latitude * Math.PI / 180;
    const lat2 = dropCoords.latitude * Math.PI / 180;
    const deltaLat = (dropCoords.latitude - pickupCoords.latitude) * Math.PI / 180;
    const deltaLon = (dropCoords.longitude - pickupCoords.longitude) * Math.PI / 180;

    const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(deltaLon/2) * Math.sin(deltaLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    let distance = R * c;

    if (tripType === 'round_trip') {
      distance = distance * 2;
    } else if (tripType === 'local_package') {
      distance = Math.max(distance, 50);
    }

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
          `Your ride has been booked!\n\nFare: ₹${response.data.booking.fare}\nDriver will arrive shortly.`,
          [{ text: 'OK' }]
        );
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

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#1A1A1A', '#0D0D0D']} style={styles.gradient}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hello, {user?.name || 'Customer'}!</Text>
            <Text style={styles.subtitle}>Where would you like to go?</Text>
          </View>
          <TouchableOpacity onPress={logout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={Colors.gold} />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
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
                <MarkerWrapper coordinate={pickupCoords} title="Pickup" pinColor={Colors.gold} />
                {dropAddress && (
                  <MarkerWrapper coordinate={dropCoords} title="Drop" pinColor={Colors.green} />
                )}
              </MapViewWrapper>
            ) : (
              <View style={styles.mapPlaceholder}>
                <Ionicons name="map" size={40} color={Colors.gray} />
                <Text style={styles.mapPlaceholderText}>Loading map...</Text>
              </View>
            )}
          </View>

          {/* Quick Book Button */}
          <TouchableOpacity
            style={styles.bookCard}
            onPress={() => setShowBookingModal(true)}
            activeOpacity={0.9}
          >
            <LinearGradient
              colors={[Colors.gold, Colors.goldDark]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.bookCardGradient}
            >
              <Ionicons name="car-sport" size={32} color={Colors.black} />
              <View style={styles.bookCardText}>
                <Text style={styles.bookCardTitle}>Book a Ride</Text>
                <Text style={styles.bookCardSubtitle}>Premium taxi service</Text>
              </View>
              <Ionicons name="arrow-forward" size={24} color={Colors.black} />
            </LinearGradient>
          </TouchableOpacity>

          {/* Quick Actions */}
          <View style={styles.quickActions}>
            <TouchableOpacity
              style={styles.actionCard}
              onPress={() => router.push('/customer/history')}
            >
              <View style={styles.actionIcon}>
                <Ionicons name="time" size={24} color={Colors.gold} />
              </View>
              <Text style={styles.actionText}>My Rides</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionCard}>
              <View style={styles.actionIcon}>
                <Ionicons name="wallet" size={24} color={Colors.greenLight} />
              </View>
              <Text style={styles.actionText}>Wallet</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionCard}>
              <View style={styles.actionIcon}>
                <Ionicons name="help-circle" size={24} color={Colors.gold} />
              </View>
              <Text style={styles.actionText}>Support</Text>
            </TouchableOpacity>
          </View>

          {/* Benefits Banner */}
          <View style={styles.benefitsBanner}>
            <Text style={styles.benefitsTitle}>Why Choose VK Drop Taxi?</Text>
            <View style={styles.benefitsRow}>
              <View style={styles.benefitItem}>
                <Ionicons name="shield-checkmark" size={20} color={Colors.gold} />
                <Text style={styles.benefitText}>Safe Rides</Text>
              </View>
              <View style={styles.benefitItem}>
                <Ionicons name="cash" size={20} color={Colors.gold} />
                <Text style={styles.benefitText}>Low Fare</Text>
              </View>
              <View style={styles.benefitItem}>
                <Ionicons name="star" size={20} color={Colors.gold} />
                <Text style={styles.benefitText}>Top Drivers</Text>
              </View>
            </View>
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
              <LinearGradient
                colors={['#2C2C2E', '#1C1C1E']}
                style={styles.modalGradient}
              >
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>Book Your Ride</Text>
                  <TouchableOpacity onPress={() => setShowBookingModal(false)}>
                    <Ionicons name="close" size={28} color={Colors.text} />
                  </TouchableOpacity>
                </View>

                <ScrollView showsVerticalScrollIndicator={false}>
                  {/* Trip Type */}
                  <Text style={styles.sectionLabel}>Trip Type</Text>
                  <View style={styles.tripTypeContainer}>
                    {[
                      { value: 'one_way', label: 'One Way', icon: 'arrow-forward' },
                      { value: 'round_trip', label: 'Round', icon: 'repeat' },
                      { value: 'local_package', label: 'Local', icon: 'location' },
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
                          size={18}
                          color={tripType === type.value ? Colors.black : Colors.gold}
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

                  {/* Locations */}
                  <Input
                    label="Pickup Location"
                    value={pickupAddress}
                    onChangeText={setPickupAddress}
                    placeholder="Enter pickup address"
                    icon={<Ionicons name="location" size={20} color={Colors.gold} />}
                  />

                  <Input
                    label="Drop Location"
                    value={dropAddress}
                    onChangeText={setDropAddress}
                    placeholder="Enter drop address"
                    icon={<Ionicons name="flag" size={20} color={Colors.greenLight} />}
                  />

                  {/* Vehicle Type */}
                  <Text style={styles.sectionLabel}>Select Vehicle</Text>
                  <View style={styles.vehicleContainer}>
                    <TouchableOpacity
                      style={[
                        styles.vehicleCard,
                        vehicleType === 'sedan' && styles.vehicleCardActive,
                      ]}
                      onPress={() => setVehicleType('sedan')}
                    >
                      <LinearGradient
                        colors={vehicleType === 'sedan' ? [Colors.gold, Colors.goldDark] : ['#2C2C2E', '#1C1C1E']}
                        style={styles.vehicleGradient}
                      >
                        <Ionicons
                          name="car-sport"
                          size={32}
                          color={vehicleType === 'sedan' ? Colors.black : Colors.gold}
                        />
                        <Text style={[styles.vehicleName, vehicleType === 'sedan' && styles.vehicleNameActive]}>
                          Sedan
                        </Text>
                        <Text style={[styles.vehicleRate, vehicleType === 'sedan' && styles.vehicleRateActive]}>
                          ₹14/km
                        </Text>
                      </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={[
                        styles.vehicleCard,
                        vehicleType === 'suv' && styles.vehicleCardActive,
                      ]}
                      onPress={() => setVehicleType('suv')}
                    >
                      <LinearGradient
                        colors={vehicleType === 'suv' ? [Colors.greenLight, Colors.greenDark] : ['#2C2C2E', '#1C1C1E']}
                        style={styles.vehicleGradient}
                      >
                        <Ionicons
                          name="car"
                          size={32}
                          color={vehicleType === 'suv' ? Colors.white : Colors.greenLight}
                        />
                        <Text style={[styles.vehicleName, vehicleType === 'suv' && styles.vehicleNameActiveSuv]}>
                          SUV
                        </Text>
                        <Text style={[styles.vehicleRate, vehicleType === 'suv' && styles.vehicleRateActiveSuv]}>
                          ₹18/km
                        </Text>
                      </LinearGradient>
                    </TouchableOpacity>
                  </View>

                  {/* Calculate Fare */}
                  <Button
                    title="Calculate Fare"
                    onPress={calculateFare}
                    variant="outline"
                    style={styles.calculateBtn}
                  />

                  {/* Fare Estimate */}
                  {estimatedFare && (
                    <View style={styles.fareCard}>
                      <LinearGradient
                        colors={['rgba(255, 215, 0, 0.15)', 'rgba(255, 215, 0, 0.05)']}
                        style={styles.fareGradient}
                      >
                        <View style={styles.fareRow}>
                          <Text style={styles.fareLabel}>Distance</Text>
                          <Text style={styles.fareValue}>{estimatedDistance} km</Text>
                        </View>
                        <View style={styles.fareRow}>
                          <Text style={styles.fareLabel}>Trip Type</Text>
                          <Text style={styles.fareValue}>
                            {tripType === 'one_way' ? 'One Way' : tripType === 'round_trip' ? 'Round Trip' : 'Local'}
                          </Text>
                        </View>
                        <View style={styles.fareDivider} />
                        <View style={styles.fareRow}>
                          <Text style={styles.fareTotalLabel}>Total Fare</Text>
                          <Text style={styles.fareTotalValue}>₹{estimatedFare}</Text>
                        </View>
                      </LinearGradient>
                    </View>
                  )}

                  {/* Book Button */}
                  <Button
                    title="Book Now"
                    onPress={handleBookRide}
                    loading={loading}
                    variant="gold"
                    disabled={!estimatedFare}
                    icon={<Ionicons name="checkmark-circle" size={20} color={Colors.black} />}
                  />

                  <View style={{ height: 20 }} />
                </ScrollView>
              </LinearGradient>
            </View>
          </View>
        </Modal>

        {showDatePicker && (
          <DateTimePicker
            value={travelDate}
            mode="date"
            display="default"
            onChange={(e, d) => { setShowDatePicker(false); d && setTravelDate(d); }}
            minimumDate={new Date()}
          />
        )}

        {showTimePicker && (
          <DateTimePicker
            value={travelTime}
            mode="time"
            display="default"
            onChange={(e, t) => { setShowTimePicker(false); t && setTravelTime(t); }}
          />
        )}
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
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
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
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  mapContainer: {
    height: 200,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: Colors.cardBackground,
    borderWidth: 1,
    borderColor: Colors.border,
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
  bookCard: {
    marginTop: 16,
    borderRadius: 16,
    overflow: 'hidden',
  },
  bookCardGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    gap: 16,
  },
  bookCardText: {
    flex: 1,
  },
  bookCardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.black,
  },
  bookCardSubtitle: {
    fontSize: 13,
    color: Colors.black,
    opacity: 0.7,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  actionCard: {
    flex: 1,
    backgroundColor: Colors.cardBackground,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  actionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  actionText: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.text,
  },
  benefitsBanner: {
    backgroundColor: 'rgba(255, 215, 0, 0.08)',
    borderRadius: 16,
    padding: 20,
    marginTop: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  benefitsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.gold,
    textAlign: 'center',
    marginBottom: 16,
  },
  benefitsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  benefitItem: {
    alignItems: 'center',
  },
  benefitText: {
    fontSize: 11,
    color: Colors.text,
    marginTop: 6,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: Colors.overlay,
    justifyContent: 'flex-end',
  },
  modalContent: {
    maxHeight: '92%',
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    overflow: 'hidden',
  },
  modalGradient: {
    padding: 24,
    paddingTop: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.gold,
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.textLight,
    marginBottom: 12,
    marginTop: 8,
  },
  tripTypeContainer: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },
  tripTypeBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: Colors.borderGold,
    gap: 6,
  },
  tripTypeBtnActive: {
    backgroundColor: Colors.gold,
    borderColor: Colors.gold,
  },
  tripTypeText: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.gold,
  },
  tripTypeTextActive: {
    color: Colors.black,
  },
  vehicleContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  vehicleCard: {
    flex: 1,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: Colors.border,
  },
  vehicleCardActive: {
    borderColor: Colors.gold,
  },
  vehicleGradient: {
    alignItems: 'center',
    padding: 20,
  },
  vehicleName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  vehicleNameActive: {
    color: Colors.black,
  },
  vehicleNameActiveSuv: {
    color: Colors.white,
  },
  vehicleRate: {
    fontSize: 13,
    color: Colors.textLight,
    marginTop: 4,
  },
  vehicleRateActive: {
    color: Colors.black,
    opacity: 0.7,
  },
  vehicleRateActiveSuv: {
    color: Colors.white,
    opacity: 0.8,
  },
  calculateBtn: {
    marginBottom: 16,
  },
  fareCard: {
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.borderGold,
  },
  fareGradient: {
    padding: 20,
  },
  fareRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
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
    backgroundColor: Colors.borderGold,
    marginVertical: 10,
  },
  fareTotalLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
  },
  fareTotalValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.gold,
  },
});
