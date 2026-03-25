import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Switch,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../store/authStore';
import { Colors } from '../../utils/colors';
import {
  updateDutyStatus,
  getWallet,
  getQueueStatus,
  getDriverProfileComplete,
  acceptRejectBooking,
  startTrip,
  completeTrip,
  getDriverRides,
} from '../../utils/api';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Ionicons } from '@expo/vector-icons';

type TripStatus = 'none' | 'assigned' | 'accepted' | 'ongoing' | 'completed';

interface CurrentTrip {
  booking_id: string;
  pickup: { address: string; latitude: number; longitude: number };
  drop: { address: string; latitude: number; longitude: number };
  fare: number;
  driver_earning: number;
  distance: number;
  status: string;
  customer_name?: string;
  customer_phone?: string;
}

export default function DriverDashboardScreen() {
  const router = useRouter();
  const { user, logout, setUser } = useAuthStore();
  
  // Driver state
  const [approvalStatus, setApprovalStatus] = useState(user?.approval_status || 'pending');
  const [dutyOn, setDutyOn] = useState(false);
  const [goHomeMode, setGoHomeMode] = useState(false);
  const [walletBalance, setWalletBalance] = useState(0);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Queue status
  const [queueStatus, setQueueStatus] = useState<any>(null);
  
  // Current trip
  const [currentTrip, setCurrentTrip] = useState<CurrentTrip | null>(null);
  const [tripStatus, setTripStatus] = useState<TripStatus>('none');
  
  // Go home modal
  const [showGoHomeModal, setShowGoHomeModal] = useState(false);
  const [homeAddress, setHomeAddress] = useState('');
  const [homeLatitude, setHomeLatitude] = useState('');
  const [homeLongitude, setHomeLongitude] = useState('');
  
  // Incoming request
  const [incomingRequest, setIncomingRequest] = useState<CurrentTrip | null>(null);
  
  // Notification state
  const [showNewBookingNotification, setShowNewBookingNotification] = useState(false);

  const driverId = user?.driver_id || '';
  const driverName = user?.personal_details?.full_name || user?.name || 'Driver';
  const vehicleType = user?.vehicle_details?.vehicle_type || user?.vehicle_type || 'sedan';
  const vehicleNumber = user?.vehicle_details?.vehicle_number || user?.vehicle_number || '';

  useEffect(() => {
    if (driverId) {
      fetchDriverData();
    }
  }, [driverId]);

  // Polling for updates when duty is on - every 5 seconds
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (dutyOn && walletBalance >= 1000 && driverId) {
      interval = setInterval(() => {
        pollForUpdates();
      }, 5000); // Poll every 5 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [dutyOn, walletBalance, driverId, tripStatus]);

  // Poll for updates (incoming requests, wallet, queue)
  const pollForUpdates = async () => {
    try {
      // Check for incoming requests
      const ridesRes = await getDriverRides(driverId);
      const rides = ridesRes.data.rides || [];
      
      const requestedTrip = rides.find((r: any) => r.status === 'requested');
      const acceptedTrip = rides.find((r: any) => r.status === 'accepted');
      const ongoingTrip = rides.find((r: any) => r.status === 'ongoing');

      // Update trip status based on current rides
      if (ongoingTrip) {
        setCurrentTrip(ongoingTrip);
        setTripStatus('ongoing');
        setIncomingRequest(null);
      } else if (acceptedTrip) {
        setCurrentTrip(acceptedTrip);
        setTripStatus('accepted');
        setIncomingRequest(null);
      } else if (requestedTrip) {
        // New booking notification
        if (!incomingRequest || incomingRequest.booking_id !== requestedTrip.booking_id) {
          setShowNewBookingNotification(true);
          setTimeout(() => setShowNewBookingNotification(false), 3000);
        }
        setIncomingRequest(requestedTrip);
        setTripStatus('assigned');
        setCurrentTrip(null);
      } else {
        setTripStatus('none');
        setIncomingRequest(null);
        setCurrentTrip(null);
      }

      // Refresh wallet balance
      const walletRes = await getWallet(driverId);
      setWalletBalance(walletRes.data.wallet.balance || 0);

      // Refresh queue status
      const queueRes = await getQueueStatus(driverId);
      setQueueStatus(queueRes.data);
    } catch (error) {
      console.error('Poll update error:', error);
    }
  };

  const fetchDriverData = async () => {
    try {
      // Fetch driver profile
      const profileRes = await getDriverProfileComplete(driverId);
      const driver = profileRes.data.driver;
      setApprovalStatus(driver.approval_status);
      setDutyOn(driver.duty_on || false);
      setGoHomeMode(driver.go_home_mode || false);
      setUser(driver);

      // Fetch wallet
      const walletRes = await getWallet(driverId);
      setWalletBalance(walletRes.data.wallet.balance || 0);

      // Fetch queue status
      const queueRes = await getQueueStatus(driverId);
      setQueueStatus(queueRes.data);

      // Check for current ongoing trip
      const ridesRes = await getDriverRides(driverId);
      const rides = ridesRes.data.rides || [];
      const ongoingTrip = rides.find((r: any) => r.status === 'ongoing');
      const acceptedTrip = rides.find((r: any) => r.status === 'accepted');
      const requestedTrip = rides.find((r: any) => r.status === 'requested');

      if (ongoingTrip) {
        setCurrentTrip(ongoingTrip);
        setTripStatus('ongoing');
      } else if (acceptedTrip) {
        setCurrentTrip(acceptedTrip);
        setTripStatus('accepted');
      } else if (requestedTrip) {
        setIncomingRequest(requestedTrip);
        setTripStatus('assigned');
      }
    } catch (error) {
      console.error('Failed to fetch driver data:', error);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchDriverData();
    await pollForUpdates();
    setRefreshing(false);
  }, [driverId]);

  const handleDutyToggle = async (value: boolean) => {
    if (walletBalance < 1000 && value) {
      Alert.alert(
        'Low Wallet Balance',
        'Your wallet balance is below ₹1000. Please recharge to go on duty.',
        [{ text: 'OK' }]
      );
      return;
    }

    setLoading(true);
    try {
      await updateDutyStatus(driverId, {
        duty_on: value,
        go_home_mode: false,
      });
      setDutyOn(value);
      setGoHomeMode(false);
      if (!value) {
        setTripStatus('none');
        setIncomingRequest(null);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update duty status');
    } finally {
      setLoading(false);
    }
  };

  const handleGoHomeToggle = async () => {
    if (!dutyOn) {
      Alert.alert('Info', 'Turn on duty first to enable Go Home mode');
      return;
    }
    
    if (!goHomeMode) {
      setShowGoHomeModal(true);
    } else {
      // Turn off go home mode
      try {
        await updateDutyStatus(driverId, {
          duty_on: true,
          go_home_mode: false,
        });
        setGoHomeMode(false);
      } catch (error: any) {
        Alert.alert('Error', error.response?.data?.detail || 'Failed to update');
      }
    }
  };

  const handleSetGoHome = async () => {
    if (!homeAddress) {
      Alert.alert('Error', 'Please enter home address');
      return;
    }

    setLoading(true);
    try {
      await updateDutyStatus(driverId, {
        duty_on: true,
        go_home_mode: true,
        home_latitude: parseFloat(homeLatitude) || 13.0,
        home_longitude: parseFloat(homeLongitude) || 80.0,
        home_address: homeAddress,
      });
      setGoHomeMode(true);
      setShowGoHomeModal(false);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to set Go Home');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRide = async () => {
    if (!incomingRequest) return;
    
    setLoading(true);
    try {
      await acceptRejectBooking({
        booking_id: incomingRequest.booking_id,
        driver_id: driverId,
        action: 'accept',
      });
      setCurrentTrip(incomingRequest);
      setIncomingRequest(null);
      setTripStatus('accepted');
      Alert.alert('Success', 'Ride accepted! Navigate to pickup location.');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to accept ride');
    } finally {
      setLoading(false);
    }
  };

  const handleRejectRide = async () => {
    if (!incomingRequest) return;
    
    setLoading(true);
    try {
      await acceptRejectBooking({
        booking_id: incomingRequest.booking_id,
        driver_id: driverId,
        action: 'reject',
      });
      setIncomingRequest(null);
      setTripStatus('none');
      Alert.alert('Ride Rejected', 'The booking has been cancelled');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to reject ride');
    } finally {
      setLoading(false);
    }
  };

  const handleStartTrip = async () => {
    if (!currentTrip) return;
    
    setLoading(true);
    try {
      await startTrip(currentTrip.booking_id);
      setTripStatus('ongoing');
      Alert.alert('Trip Started', 'Navigate to drop location.');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to start trip');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTrip = async () => {
    if (!currentTrip) return;
    
    Alert.alert(
      'Complete Trip',
      `Confirm trip completion?\nEarning: ₹${currentTrip.driver_earning}`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Complete',
          onPress: async () => {
            setLoading(true);
            try {
              const res = await completeTrip(currentTrip.booking_id);
              setTripStatus('completed');
              Alert.alert(
                'Trip Completed!',
                `You earned ₹${res.data.earning || currentTrip.driver_earning}`,
                [
                  {
                    text: 'OK',
                    onPress: () => {
                      setCurrentTrip(null);
                      setTripStatus('none');
                      fetchDriverData();
                    },
                  },
                ]
              );
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to complete trip');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  // Pending approval screen
  if (approvalStatus === 'pending') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome, {driverName}!</Text>
          <TouchableOpacity onPress={logout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={Colors.error} />
          </TouchableOpacity>
        </View>
        <View style={styles.centerContainer}>
          <Ionicons name="time-outline" size={80} color={Colors.warning} />
          <Text style={styles.centerTitle}>Approval Pending</Text>
          <Text style={styles.centerText}>
            Your account is under review. You will be notified once approved.
          </Text>
          <Button title="Refresh Status" onPress={fetchDriverData} variant="primary" style={styles.refreshBtn} />
        </View>
      </View>
    );
  }

  // Rejected screen
  if (approvalStatus === 'rejected') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome, {driverName}!</Text>
          <TouchableOpacity onPress={logout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={Colors.error} />
          </TouchableOpacity>
        </View>
        <View style={styles.centerContainer}>
          <Ionicons name="close-circle-outline" size={80} color={Colors.error} />
          <Text style={styles.centerTitle}>Application Rejected</Text>
          <Text style={styles.centerText}>
            Your application was not approved. Please contact support.
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* New Booking Notification Banner */}
      {showNewBookingNotification && (
        <View style={styles.notificationBanner}>
          <Ionicons name="notifications" size={20} color={Colors.white} />
          <Text style={styles.notificationText}>New Booking Request!</Text>
        </View>
      )}

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome, {driverName}!</Text>
          <Text style={styles.subtitle}>
            {vehicleType.toUpperCase()} • {vehicleNumber}
          </Text>
        </View>
        <TouchableOpacity onPress={logout} style={styles.logoutButton}>
          <Ionicons name="log-out-outline" size={24} color={Colors.error} />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Wallet Warning */}
        {walletBalance < 1000 && (
          <View style={styles.warningCard}>
            <Ionicons name="warning" size={24} color={Colors.white} />
            <View style={styles.warningText}>
              <Text style={styles.warningTitle}>Low Wallet Balance</Text>
              <Text style={styles.warningSubtitle}>
                Balance: ₹{walletBalance.toFixed(0)} (Minimum ₹1000 required)
              </Text>
            </View>
            <TouchableOpacity onPress={() => router.push('/driver/earnings')}>
              <Text style={styles.warningAction}>Add Money</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Wallet Balance Card */}
        <View style={styles.walletCard}>
          <View style={styles.walletInfo}>
            <Ionicons name="wallet" size={28} color={Colors.secondary} />
            <View style={styles.walletTextContainer}>
              <Text style={styles.walletLabel}>Wallet Balance</Text>
              <Text style={styles.walletAmount}>₹{walletBalance.toFixed(0)}</Text>
            </View>
          </View>
          <TouchableOpacity
            style={styles.addMoneyBtn}
            onPress={() => router.push('/driver/earnings')}
          >
            <Text style={styles.addMoneyText}>Add Money</Text>
          </TouchableOpacity>
        </View>

        {/* Duty Status Card */}
        <View style={styles.dutyCard}>
          <View style={styles.dutyRow}>
            <View style={styles.dutyInfo}>
              <Ionicons
                name={dutyOn ? 'radio-button-on' : 'radio-button-off'}
                size={32}
                color={dutyOn ? Colors.success : Colors.gray}
              />
              <View style={styles.dutyTextContainer}>
                <Text style={styles.dutyTitle}>
                  {dutyOn ? 'Duty ON' : 'Duty OFF'}
                </Text>
                <Text style={styles.dutySubtitle}>
                  {dutyOn ? 'Accepting rides' : 'Toggle to start'}
                </Text>
              </View>
            </View>
            <Switch
              value={dutyOn}
              onValueChange={handleDutyToggle}
              trackColor={{ false: Colors.gray, true: Colors.success }}
              thumbColor={Colors.white}
              disabled={loading || walletBalance < 1000}
            />
          </View>

          {/* Go Home Toggle */}
          {dutyOn && (
            <TouchableOpacity
              style={[styles.goHomeBtn, goHomeMode && styles.goHomeBtnActive]}
              onPress={handleGoHomeToggle}
            >
              <Ionicons
                name="home"
                size={20}
                color={goHomeMode ? Colors.white : Colors.secondary}
              />
              <Text style={[styles.goHomeText, goHomeMode && styles.goHomeTextActive]}>
                {goHomeMode ? 'Go Home: ON' : 'Go Home Mode'}
              </Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Queue Status */}
        {queueStatus && dutyOn && (
          <View style={styles.queueCard}>
            <Text style={styles.queueTitle}>Queue Status</Text>
            <View style={styles.queueRow}>
              <View style={styles.queueItem}>
                <Text style={styles.queueValue}>{queueStatus.continuous_trips_count || 0}</Text>
                <Text style={styles.queueLabel}>Trips Today</Text>
              </View>
              <View style={styles.queueDivider} />
              <View style={styles.queueItem}>
                <Text style={styles.queueValue}>
                  {queueStatus.in_queue ? `#${queueStatus.queue_position || '-'}` : '-'}
                </Text>
                <Text style={styles.queueLabel}>Queue Position</Text>
              </View>
              <View style={styles.queueDivider} />
              <View style={styles.queueItem}>
                <Text style={styles.queueValue}>{queueStatus.total_in_queue || 0}</Text>
                <Text style={styles.queueLabel}>In Queue</Text>
              </View>
            </View>
          </View>
        )}

        {/* Incoming Request */}
        {incomingRequest && tripStatus === 'assigned' && (
          <View style={styles.requestCard}>
            <View style={styles.requestHeader}>
              <Text style={styles.requestTitle}>New Ride Request!</Text>
              <Text style={styles.requestFare}>₹{incomingRequest.fare}</Text>
            </View>

            <View style={styles.locationRow}>
              <Ionicons name="location" size={18} color={Colors.primary} />
              <Text style={styles.locationText} numberOfLines={2}>
                {incomingRequest.pickup.address}
              </Text>
            </View>

            <View style={styles.locationRow}>
              <Ionicons name="flag" size={18} color={Colors.secondary} />
              <Text style={styles.locationText} numberOfLines={2}>
                {incomingRequest.drop.address}
              </Text>
            </View>

            <View style={styles.requestInfo}>
              <Text style={styles.infoText}>Distance: {incomingRequest.distance} km</Text>
              <Text style={styles.infoText}>Your Earning: ₹{incomingRequest.driver_earning}</Text>
            </View>

            <View style={styles.requestActions}>
              <Button
                title="Accept"
                onPress={handleAcceptRide}
                variant="secondary"
                loading={loading}
                style={styles.acceptBtn}
              />
              <Button
                title="Reject"
                onPress={handleRejectRide}
                variant="outline"
                loading={loading}
                style={styles.rejectBtn}
              />
            </View>
          </View>
        )}

        {/* Current Trip */}
        {currentTrip && (tripStatus === 'accepted' || tripStatus === 'ongoing') && (
          <View style={styles.tripCard}>
            <View style={styles.tripHeader}>
              <Text style={styles.tripTitle}>
                {tripStatus === 'accepted' ? 'Trip Assigned' : 'Trip Ongoing'}
              </Text>
              <View style={[styles.statusBadge, tripStatus === 'ongoing' && styles.statusOngoing]}>
                <Text style={styles.statusText}>
                  {tripStatus === 'accepted' ? 'Go to Pickup' : 'In Progress'}
                </Text>
              </View>
            </View>

            <View style={styles.locationRow}>
              <Ionicons name="location" size={18} color={Colors.primary} />
              <Text style={styles.locationText} numberOfLines={2}>
                {currentTrip.pickup.address}
              </Text>
            </View>

            <View style={styles.locationRow}>
              <Ionicons name="flag" size={18} color={Colors.secondary} />
              <Text style={styles.locationText} numberOfLines={2}>
                {currentTrip.drop.address}
              </Text>
            </View>

            <View style={styles.tripInfo}>
              <View style={styles.tripInfoItem}>
                <Text style={styles.tripInfoLabel}>Distance</Text>
                <Text style={styles.tripInfoValue}>{currentTrip.distance} km</Text>
              </View>
              <View style={styles.tripInfoItem}>
                <Text style={styles.tripInfoLabel}>Fare</Text>
                <Text style={styles.tripInfoValue}>₹{currentTrip.fare}</Text>
              </View>
              <View style={styles.tripInfoItem}>
                <Text style={styles.tripInfoLabel}>Earning</Text>
                <Text style={styles.tripInfoValue}>₹{currentTrip.driver_earning}</Text>
              </View>
            </View>

            {tripStatus === 'accepted' && (
              <Button
                title="Start Trip"
                onPress={handleStartTrip}
                variant="primary"
                loading={loading}
                style={styles.tripBtn}
              />
            )}

            {tripStatus === 'ongoing' && (
              <Button
                title="Complete Trip"
                onPress={handleCompleteTrip}
                variant="secondary"
                loading={loading}
                style={styles.tripBtn}
              />
            )}
          </View>
        )}

        {/* Quick Actions */}
        {tripStatus === 'none' && (
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
        )}

        {/* No requests message */}
        {dutyOn && tripStatus === 'none' && walletBalance >= 1000 && (
          <View style={styles.noRequestsContainer}>
            <Ionicons name="car-outline" size={60} color={Colors.gray} />
            <Text style={styles.noRequestsText}>Waiting for ride requests...</Text>
            <Text style={styles.noRequestsSubtext}>Pull down to refresh</Text>
          </View>
        )}
      </ScrollView>

      {/* Go Home Modal */}
      <Modal
        visible={showGoHomeModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowGoHomeModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Set Home Location</Text>
              <TouchableOpacity onPress={() => setShowGoHomeModal(false)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            <Input
              label="Home Address"
              value={homeAddress}
              onChangeText={setHomeAddress}
              placeholder="Enter your home address"
            />

            <Input
              label="Latitude (optional)"
              value={homeLatitude}
              onChangeText={setHomeLatitude}
              placeholder="e.g. 13.0827"
              keyboardType="numeric"
            />

            <Input
              label="Longitude (optional)"
              value={homeLongitude}
              onChangeText={setHomeLongitude}
              placeholder="e.g. 80.2707"
              keyboardType="numeric"
            />

            <Button
              title="Enable Go Home"
              onPress={handleSetGoHome}
              variant="secondary"
              loading={loading}
            />
          </View>
        </View>
      </Modal>

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
    backgroundColor: Colors.secondary,
  },
  greeting: {
    fontSize: 22,
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
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  centerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 24,
  },
  centerText: {
    fontSize: 16,
    color: Colors.textLight,
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 24,
  },
  refreshBtn: {
    marginTop: 32,
    minWidth: 200,
  },
  warningCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.error,
    margin: 16,
    marginBottom: 8,
    padding: 16,
    borderRadius: 12,
  },
  warningText: {
    flex: 1,
    marginLeft: 12,
  },
  warningTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.white,
  },
  warningSubtitle: {
    fontSize: 13,
    color: Colors.white,
    opacity: 0.9,
  },
  warningAction: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.white,
    textDecorationLine: 'underline',
  },
  walletCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.white,
    margin: 16,
    marginTop: 8,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  walletInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  walletTextContainer: {
    marginLeft: 12,
  },
  walletLabel: {
    fontSize: 13,
    color: Colors.textLight,
  },
  walletAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
  },
  addMoneyBtn: {
    backgroundColor: Colors.secondary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addMoneyText: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.white,
  },
  dutyCard: {
    backgroundColor: Colors.white,
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  dutyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dutyInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  dutyTextContainer: {
    marginLeft: 12,
  },
  dutyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
  },
  dutySubtitle: {
    fontSize: 13,
    color: Colors.textLight,
    marginTop: 2,
  },
  goHomeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: Colors.secondary,
    borderRadius: 8,
  },
  goHomeBtnActive: {
    backgroundColor: Colors.secondary,
  },
  goHomeText: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.secondary,
    marginLeft: 8,
  },
  goHomeTextActive: {
    color: Colors.white,
  },
  queueCard: {
    backgroundColor: Colors.white,
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  queueTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 12,
  },
  queueRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  queueItem: {
    alignItems: 'center',
  },
  queueValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.secondary,
  },
  queueLabel: {
    fontSize: 12,
    color: Colors.textLight,
    marginTop: 4,
  },
  queueDivider: {
    width: 1,
    backgroundColor: Colors.border,
  },
  requestCard: {
    backgroundColor: Colors.white,
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderWidth: 3,
    borderColor: Colors.primary,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  requestTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.secondary,
  },
  requestFare: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  locationText: {
    flex: 1,
    fontSize: 14,
    color: Colors.text,
    marginLeft: 8,
  },
  requestInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  infoText: {
    fontSize: 14,
    color: Colors.textLight,
  },
  requestActions: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  acceptBtn: {
    flex: 1,
  },
  rejectBtn: {
    flex: 1,
  },
  tripCard: {
    backgroundColor: Colors.white,
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: Colors.secondary,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 3,
  },
  tripHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  tripTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
  },
  statusBadge: {
    backgroundColor: Colors.warning,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusOngoing: {
    backgroundColor: Colors.success,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: Colors.white,
  },
  tripInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  tripInfoItem: {
    alignItems: 'center',
  },
  tripInfoLabel: {
    fontSize: 12,
    color: Colors.textLight,
  },
  tripInfoValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 4,
  },
  tripBtn: {
    marginTop: 16,
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: Colors.white,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  actionText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  noRequestsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  noRequestsText: {
    marginTop: 16,
    fontSize: 16,
    color: Colors.gray,
  },
  noRequestsSubtext: {
    marginTop: 4,
    fontSize: 13,
    color: Colors.gray,
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
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
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
  notificationBanner: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: Colors.success,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingTop: 50,
    zIndex: 1000,
    gap: 8,
  },
  notificationText: {
    color: Colors.white,
    fontSize: 16,
    fontWeight: 'bold',
  },
});
