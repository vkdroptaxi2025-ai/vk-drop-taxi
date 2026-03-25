import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { MapViewWrapper, MarkerWrapper } from '../../components/MapViewWrapper';
import { Colors } from '../../utils/colors';
import { getBooking, updateBooking } from '../../utils/api';
import { Button } from '../../components/Button';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';

export default function BookingDetailsScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const { user } = useAuthStore();
  const [booking, setBooking] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchBookingDetails();
    }
  }, [id]);

  const fetchBookingDetails = async () => {
    setLoading(true);
    try {
      const response = await getBooking(id as string);
      setBooking(response.data.booking);
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch booking details');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async () => {
    Alert.alert(
      'Cancel Booking',
      'Are you sure you want to cancel this booking?',
      [
        { text: 'No', style: 'cancel' },
        {
          text: 'Yes, Cancel',
          style: 'destructive',
          onPress: async () => {
            try {
              await updateBooking({
                booking_id: booking.booking_id,
                status: 'cancelled',
              });
              Alert.alert('Success', 'Booking cancelled');
              fetchBookingDetails();
            } catch (error) {
              Alert.alert('Error', 'Failed to cancel booking');
            }
          },
        },
      ]
    );
  };

  const handleCompleteRide = async () => {
    try {
      await updateBooking({
        booking_id: booking.booking_id,
        status: 'completed',
      });
      Alert.alert('Success', 'Ride completed!');
      fetchBookingDetails();
    } catch (error) {
      Alert.alert('Error', 'Failed to complete ride');
    }
  };

  const handleStartRide = async () => {
    try {
      await updateBooking({
        booking_id: booking.booking_id,
        status: 'ongoing',
      });
      Alert.alert('Success', 'Ride started!');
      fetchBookingDetails();
    } catch (error) {
      Alert.alert('Error', 'Failed to start ride');
    }
  };

  if (loading || !booking) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={Colors.text} />
          </TouchableOpacity>
          <Text style={styles.title}>Booking Details</Text>
          <View style={styles.placeholder} />
        </View>
        <View style={styles.loadingContainer}>
          <Text>Loading...</Text>
        </View>
      </View>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return Colors.success;
      case 'cancelled':
        return Colors.error;
      case 'ongoing':
        return Colors.warning;
      default:
        return Colors.primary;
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={styles.title}>Booking Details</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Status Badge */}
        <View style={[styles.statusBanner, { backgroundColor: getStatusColor(booking.status) }]}>
          <Ionicons name="information-circle" size={32} color={Colors.white} />
          <View style={styles.statusInfo}>
            <Text style={styles.statusTitle}>{booking.status.toUpperCase()}</Text>
            <Text style={styles.statusSubtitle}>Booking #{booking.booking_id.slice(0, 8)}</Text>
          </View>
        </View>

        {/* Map */}
        <View style={styles.mapContainer}>
          <MapViewWrapper
            style={styles.map}
            initialRegion={{
              latitude: booking.pickup.latitude,
              longitude: booking.pickup.longitude,
              latitudeDelta: 0.05,
              longitudeDelta: 0.05,
            }}
          >
            <MarkerWrapper
              coordinate={{
                latitude: booking.pickup.latitude,
                longitude: booking.pickup.longitude,
              }}
              title="Pickup"
              pinColor={Colors.primary}
            />
            <MarkerWrapper
              coordinate={{
                latitude: booking.drop.latitude,
                longitude: booking.drop.longitude,
              }}
              title="Drop"
              pinColor={Colors.secondary}
            />
          </MapViewWrapper>
        </View>

        {/* Locations */}
        <View style={styles.section}>
          <View style={styles.locationItem}>
            <View style={styles.locationIcon}>
              <Ionicons name="location" size={24} color={Colors.primary} />
            </View>
            <View style={styles.locationDetails}>
              <Text style={styles.locationLabel}>Pickup</Text>
              <Text style={styles.locationAddress}>{booking.pickup.address}</Text>
            </View>
          </View>

          <View style={styles.locationDivider} />

          <View style={styles.locationItem}>
            <View style={styles.locationIcon}>
              <Ionicons name="flag" size={24} color={Colors.secondary} />
            </View>
            <View style={styles.locationDetails}>
              <Text style={styles.locationLabel}>Drop</Text>
              <Text style={styles.locationAddress}>{booking.drop.address}</Text>
            </View>
          </View>
        </View>

        {/* Fare Details */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Fare Details</Text>
          <View style={styles.fareRow}>
            <Text style={styles.fareLabel}>Distance</Text>
            <Text style={styles.fareValue}>{booking.distance} km</Text>
          </View>
          <View style={styles.fareRow}>
            <Text style={styles.fareLabel}>Vehicle Type</Text>
            <Text style={styles.fareValue}>{booking.vehicle_type.toUpperCase()}</Text>
          </View>
          <View style={styles.fareRow}>
            <Text style={styles.fareLabel}>Base Fare</Text>
            <Text style={styles.fareValue}>₹{booking.fare}</Text>
          </View>
          <View style={styles.fareDivider} />
          <View style={styles.fareRow}>
            <Text style={styles.fareTotalLabel}>Total Amount</Text>
            <Text style={styles.fareTotalValue}>₹{booking.fare}</Text>
          </View>
        </View>

        {/* Driver Details (if available) */}
        {booking.driver_name && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Driver Details</Text>
            <View style={styles.driverCard}>
              <Ionicons name="person-circle" size={48} color={Colors.secondary} />
              <View style={styles.driverInfo}>
                <Text style={styles.driverName}>{booking.driver_name}</Text>
                <Text style={styles.driverPhone}>{booking.driver_phone}</Text>
                <Text style={styles.driverVehicle}>{booking.vehicle_number}</Text>
              </View>
            </View>
          </View>
        )}

        {/* Action Buttons */}
        {user?.role === 'customer' && booking.status === 'requested' && (
          <Button
            title="Cancel Booking"
            onPress={handleCancelBooking}
            variant="outline"
            style={styles.actionButton}
          />
        )}

        {user?.role === 'driver' && booking.status === 'accepted' && (
          <Button
            title="Start Ride"
            onPress={handleStartRide}
            variant="secondary"
            style={styles.actionButton}
          />
        )}

        {user?.role === 'driver' && booking.status === 'ongoing' && (
          <Button
            title="Complete Ride"
            onPress={handleCompleteRide}
            variant="secondary"
            style={styles.actionButton}
          />
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    paddingTop: 60,
    backgroundColor: Colors.white,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  placeholder: {
    width: 40,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    padding: 16,
  },
  statusBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  statusInfo: {
    marginLeft: 16,
    flex: 1,
  },
  statusTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.white,
  },
  statusSubtitle: {
    fontSize: 14,
    color: Colors.white,
    marginTop: 4,
    opacity: 0.9,
  },
  mapContainer: {
    height: 200,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
  },
  map: {
    flex: 1,
  },
  section: {
    backgroundColor: Colors.white,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  locationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  locationIcon: {
    width: 40,
    alignItems: 'center',
  },
  locationDetails: {
    flex: 1,
  },
  locationLabel: {
    fontSize: 12,
    color: Colors.textLight,
    marginBottom: 4,
  },
  locationAddress: {
    fontSize: 16,
    color: Colors.text,
  },
  locationDivider: {
    width: 2,
    height: 24,
    backgroundColor: Colors.border,
    marginLeft: 19,
    marginVertical: 8,
  },
  fareRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  fareLabel: {
    fontSize: 14,
    color: Colors.textLight,
  },
  fareValue: {
    fontSize: 14,
    color: Colors.text,
    fontWeight: '600',
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
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  driverCard: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  driverInfo: {
    marginLeft: 16,
    flex: 1,
  },
  driverName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
  },
  driverPhone: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 4,
  },
  driverVehicle: {
    fontSize: 14,
    color: Colors.secondary,
    marginTop: 4,
    fontWeight: '600',
  },
  actionButton: {
    marginTop: 8,
  },
});
