import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Switch,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../store/authStore';
import { Colors } from '../../utils/colors';
import {
  updateDriverStatus,
  getPendingRides,
  updateBooking,
  getDriverProfile,
} from '../../utils/api';
import { Button } from '../../components/Button';
import { Ionicons } from '@expo/vector-icons';

export default function DriverDashboardScreen() {
  const router = useRouter();
  const { user, logout, setUser } = useAuthStore();
  const [isOnline, setIsOnline] = useState(user?.is_online || false);
  const [pendingRides, setPendingRides] = useState([]);
  const [loading, setLoading] = useState(false);
  const [approvalStatus, setApprovalStatus] = useState(user?.approval_status);

  useEffect(() => {
    fetchDriverProfile();
    if (approvalStatus === 'approved') {
      fetchPendingRides();
    }
  }, []);

  const fetchDriverProfile = async () => {
    try {
      const response = await getDriverProfile(user?.driver_id || '');
      const driver = response.data.driver;
      setApprovalStatus(driver.approval_status);
      setIsOnline(driver.is_online);
      setUser(driver);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    }
  };

  const fetchPendingRides = async () => {
    setLoading(true);
    try {
      const response = await getPendingRides(user?.driver_id || '');
      setPendingRides(response.data.pending_rides);
    } catch (error) {
      console.error('Failed to fetch rides:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleOnline = async (value: boolean) => {
    try {
      await updateDriverStatus(user?.driver_id || '', value);
      setIsOnline(value);
      if (value) {
        fetchPendingRides();
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update status');
    }
  };

  const handleAcceptRide = async (bookingId: string) => {
    try {
      await updateBooking({
        booking_id: bookingId,
        status: 'accepted',
      });
      Alert.alert('Success', 'Ride accepted!');
      fetchPendingRides();
    } catch (error) {
      Alert.alert('Error', 'Failed to accept ride');
    }
  };

  const handleRejectRide = async (bookingId: string) => {
    try {
      await updateBooking({
        booking_id: bookingId,
        status: 'cancelled',
      });
      Alert.alert('Ride Rejected', 'The ride has been cancelled');
      fetchPendingRides();
    } catch (error) {
      Alert.alert('Error', 'Failed to reject ride');
    }
  };

  if (approvalStatus === 'pending') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome, {user?.name}!</Text>
          <TouchableOpacity onPress={logout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={Colors.error} />
          </TouchableOpacity>
        </View>

        <View style={styles.pendingApprovalContainer}>
          <Ionicons name="time-outline" size={80} color={Colors.warning} />
          <Text style={styles.pendingTitle}>Approval Pending</Text>
          <Text style={styles.pendingText}>
            Your account is under review. You will be notified once approved.
          </Text>
          <Button
            title="Refresh Status"
            onPress={fetchDriverProfile}
            variant="primary"
            style={styles.refreshButton}
          />
        </View>
      </View>
    );
  }

  if (approvalStatus === 'rejected') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome, {user?.name}!</Text>
          <TouchableOpacity onPress={logout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={Colors.error} />
          </TouchableOpacity>
        </View>

        <View style={styles.pendingApprovalContainer}>
          <Ionicons name="close-circle-outline" size={80} color={Colors.error} />
          <Text style={styles.pendingTitle}>Application Rejected</Text>
          <Text style={styles.pendingText}>
            Your application was not approved. Please contact support for more information.
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome, {user?.name}!</Text>
          <Text style={styles.subtitle}>
            {user?.vehicle_type.toUpperCase()} • {user?.vehicle_number}
          </Text>
        </View>
        <TouchableOpacity onPress={logout} style={styles.logoutButton}>
          <Ionicons name="log-out-outline" size={24} color={Colors.error} />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={fetchPendingRides} />
        }
      >
        {/* Online Status Toggle */}
        <View style={styles.statusCard}>
          <View style={styles.statusInfo}>
            <Ionicons
              name={isOnline ? 'radio-button-on' : 'radio-button-off'}
              size={32}
              color={isOnline ? Colors.success : Colors.gray}
            />
            <View style={styles.statusText}>
              <Text style={styles.statusTitle}>
                {isOnline ? 'You are Online' : 'You are Offline'}
              </Text>
              <Text style={styles.statusSubtitle}>
                {isOnline ? 'Ready to accept rides' : 'Toggle to go online'}
              </Text>
            </View>
          </View>
          <Switch
            value={isOnline}
            onValueChange={handleToggleOnline}
            trackColor={{ false: Colors.gray, true: Colors.success }}
            thumbColor={Colors.white}
          />
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push('/driver/earnings')}
          >
            <Ionicons name="cash" size={32} color={Colors.primary} />
            <Text style={styles.actionText}>Earnings</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push('/customer/history')}
          >
            <Ionicons name="list" size={32} color={Colors.secondary} />
            <Text style={styles.actionText}>My Rides</Text>
          </TouchableOpacity>
        </View>

        {/* Pending Ride Requests */}
        {isOnline && (
          <View style={styles.ridesSection}>
            <Text style={styles.sectionTitle}>Incoming Requests</Text>
            {pendingRides.length > 0 ? (
              pendingRides.map((ride: any) => (
                <View key={ride.booking_id} style={styles.rideCard}>
                  <View style={styles.rideHeader}>
                    <Text style={styles.rideId}>#{ride.booking_id.slice(0, 8)}</Text>
                    <Text style={styles.rideFare}>₹{ride.fare}</Text>
                  </View>

                  <View style={styles.locationRow}>
                    <Ionicons name="location" size={16} color={Colors.primary} />
                    <Text style={styles.address} numberOfLines={1}>
                      {ride.pickup.address}
                    </Text>
                  </View>

                  <View style={styles.locationRow}>
                    <Ionicons name="flag" size={16} color={Colors.secondary} />
                    <Text style={styles.address} numberOfLines={1}>
                      {ride.drop.address}
                    </Text>
                  </View>

                  <View style={styles.rideFooter}>
                    <Text style={styles.distance}>{ride.distance} km</Text>
                    <Text style={styles.earning}>
                      Your Earning: ₹{ride.driver_earning}
                    </Text>
                  </View>

                  <View style={styles.actionButtons}>
                    <Button
                      title="Accept"
                      onPress={() => handleAcceptRide(ride.booking_id)}
                      variant="secondary"
                      style={styles.acceptButton}
                    />
                    <Button
                      title="Reject"
                      onPress={() => handleRejectRide(ride.booking_id)}
                      variant="outline"
                      style={styles.rejectButton}
                    />
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.noRidesContainer}>
                <Ionicons name="car-outline" size={60} color={Colors.gray} />
                <Text style={styles.noRidesText}>No pending requests</Text>
              </View>
            )}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: Colors.secondary,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.white,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.white,
    marginTop: 4,
    opacity: 0.9,
  },
  logoutButton: {
    padding: 8,
    backgroundColor: Colors.white,
    borderRadius: 20,
  },
  content: {
    flex: 1,
  },
  statusCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    margin: 16,
    padding: 20,
    backgroundColor: Colors.white,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  statusText: {
    marginLeft: 16,
    flex: 1,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
  },
  statusSubtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 4,
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 16,
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
  ridesSection: {
    padding: 16,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  rideCard: {
    backgroundColor: Colors.white,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: Colors.primary,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  rideHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  rideId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
  },
  rideFare: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 8,
  },
  address: {
    flex: 1,
    fontSize: 14,
    color: Colors.textLight,
  },
  rideFooter: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  distance: {
    fontSize: 14,
    color: Colors.gray,
    marginBottom: 4,
  },
  earning: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.secondary,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  acceptButton: {
    flex: 1,
  },
  rejectButton: {
    flex: 1,
  },
  noRidesContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  noRidesText: {
    marginTop: 16,
    fontSize: 16,
    color: Colors.gray,
  },
  pendingApprovalContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  pendingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 24,
  },
  pendingText: {
    fontSize: 16,
    color: Colors.textLight,
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 24,
  },
  refreshButton: {
    marginTop: 32,
    minWidth: 200,
  },
});