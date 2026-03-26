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
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../store/authStore';
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
import { Ionicons } from '@expo/vector-icons';

// Yellow + Green Theme
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
  warning: '#FF9800',
};

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
  
  const [driverData, setDriverData] = useState<any>(null);
  const [approvalStatus, setApprovalStatus] = useState(user?.approval_status || 'pending');
  const [dutyOn, setDutyOn] = useState(false);
  const [walletBalance, setWalletBalance] = useState(0);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [queueStatus, setQueueStatus] = useState<any>(null);
  const [currentTrip, setCurrentTrip] = useState<CurrentTrip | null>(null);
  const [tripStatus, setTripStatus] = useState<TripStatus>('none');
  const [incomingRequest, setIncomingRequest] = useState<CurrentTrip | null>(null);
  const [totalEarnings, setTotalEarnings] = useState(0);
  const [completedTrips, setCompletedTrips] = useState(0);

  const driverId = user?.driver_id || '';

  useEffect(() => {
    if (driverId) {
      fetchDriverData();
    }
  }, [driverId]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (dutyOn && walletBalance >= 1000 && driverId) {
      interval = setInterval(() => {
        pollForUpdates();
      }, 5000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [dutyOn, walletBalance, driverId, tripStatus]);

  const pollForUpdates = async () => {
    try {
      const ridesRes = await getDriverRides(driverId);
      const rides = ridesRes.data.rides || [];
      
      const requestedTrip = rides.find((r: any) => r.status === 'requested');
      const acceptedTrip = rides.find((r: any) => r.status === 'accepted');
      const ongoingTrip = rides.find((r: any) => r.status === 'ongoing');

      if (ongoingTrip) {
        setCurrentTrip(ongoingTrip);
        setTripStatus('ongoing');
        setIncomingRequest(null);
      } else if (acceptedTrip) {
        setCurrentTrip(acceptedTrip);
        setTripStatus('accepted');
        setIncomingRequest(null);
      } else if (requestedTrip) {
        setIncomingRequest(requestedTrip);
        setTripStatus('assigned');
        setCurrentTrip(null);
      } else {
        setTripStatus('none');
        setIncomingRequest(null);
        setCurrentTrip(null);
      }

      const walletRes = await getWallet(driverId);
      setWalletBalance(walletRes.data.wallet?.balance || 0);

      const queueRes = await getQueueStatus(driverId);
      setQueueStatus(queueRes.data);
    } catch (error) {
      console.error('Poll error:', error);
    }
  };

  const fetchDriverData = async () => {
    try {
      const profileRes = await getDriverProfileComplete(driverId);
      const driver = profileRes.data.driver;
      setDriverData(driver);
      setApprovalStatus(driver.approval_status);
      setDutyOn(driver.duty_on || false);
      setTotalEarnings(driver.earnings || 0);
      setCompletedTrips(driver.completed_trips || 0);
      setUser(driver);

      const walletRes = await getWallet(driverId);
      setWalletBalance(walletRes.data.wallet?.balance || 0);

      const queueRes = await getQueueStatus(driverId);
      setQueueStatus(queueRes.data);

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
      Alert.alert('Low Balance', 'Minimum Rs.1000 wallet balance required to go on duty.');
      return;
    }

    setLoading(true);
    try {
      await updateDutyStatus(driverId, { duty_on: value, go_home_mode: false });
      setDutyOn(value);
      if (!value) {
        setTripStatus('none');
        setIncomingRequest(null);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update duty');
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
      Alert.alert('Success', 'Ride accepted! Navigate to pickup.');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to accept');
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
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to reject');
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
      Alert.alert('Error', error.response?.data?.detail || 'Failed to start');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTrip = async () => {
    if (!currentTrip) return;
    Alert.alert('Complete Trip', `Earning: Rs.${currentTrip.driver_earning}`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Complete',
        onPress: async () => {
          setLoading(true);
          try {
            const res = await completeTrip(currentTrip.booking_id);
            Alert.alert('Trip Completed!', `You earned Rs.${res.data.earning || currentTrip.driver_earning}`);
            setCurrentTrip(null);
            setTripStatus('none');
            fetchDriverData();
          } catch (error: any) {
            Alert.alert('Error', error.response?.data?.detail || 'Failed');
          } finally {
            setLoading(false);
          }
        },
      },
    ]);
  };

  // Get driver display info
  const driverName = driverData?.full_name || user?.full_name || user?.personal_details?.full_name || user?.name || 'Driver';
  const vehicleType = (driverData?.vehicle_type || user?.vehicle_type || user?.vehicle_details?.vehicle_type || 'sedan').toUpperCase();
  const vehicleNumber = driverData?.vehicle_number || user?.vehicle_number || user?.vehicle_details?.vehicle_number || '';
  const vehicleModel = driverData?.vehicle_model || user?.vehicle_model || user?.vehicle_details?.vehicle_model || '';

  // Pending Approval Screen
  if (approvalStatus === 'pending') {
    return (
      <View style={styles.container}>
        <View style={styles.pendingContainer}>
          <View style={styles.pendingIcon}>
            <Ionicons name="time" size={60} color={COLORS.warning} />
          </View>
          <Text style={styles.pendingTitle}>Approval Pending</Text>
          <Text style={styles.pendingMessage}>
            Your registration is under review.{'\n'}
            Admin will verify your documents and approve.
          </Text>
          <TouchableOpacity style={styles.refreshButton} onPress={fetchDriverData}>
            <Ionicons name="refresh" size={20} color={COLORS.secondary} />
            <Text style={styles.refreshButtonText}>Refresh Status</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.logoutButtonSecondary} onPress={logout}>
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Rejected Screen
  if (approvalStatus === 'rejected') {
    return (
      <View style={styles.container}>
        <View style={styles.pendingContainer}>
          <View style={[styles.pendingIcon, { backgroundColor: 'rgba(220, 53, 69, 0.1)' }]}>
            <Ionicons name="close-circle" size={60} color={COLORS.error} />
          </View>
          <Text style={[styles.pendingTitle, { color: COLORS.error }]}>Application Rejected</Text>
          <Text style={styles.pendingMessage}>
            Your application was not approved.{'\n'}
            Please contact support for more information.
          </Text>
          <TouchableOpacity style={styles.logoutButtonSecondary} onPress={logout}>
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.greeting}>Hello, {driverName}!</Text>
          <Text style={styles.driverId}>{driverId}</Text>
        </View>
        <TouchableOpacity onPress={logout} style={styles.logoutIcon}>
          <Ionicons name="log-out-outline" size={24} color={COLORS.text} />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.secondary} />}
        showsVerticalScrollIndicator={false}
      >
        {/* Vehicle Info Card */}
        <View style={styles.vehicleCard}>
          <View style={styles.vehicleIconContainer}>
            <Ionicons name="car-sport" size={32} color={COLORS.secondary} />
          </View>
          <View style={styles.vehicleInfo}>
            <Text style={styles.vehicleNumber}>{vehicleNumber}</Text>
            <Text style={styles.vehicleDetails}>{vehicleType} - {vehicleModel}</Text>
          </View>
        </View>

        {/* Wallet Warning */}
        {walletBalance < 1000 && (
          <View style={styles.warningCard}>
            <Ionicons name="warning" size={24} color={COLORS.error} />
            <View style={styles.warningText}>
              <Text style={styles.warningTitle}>Low Wallet Balance</Text>
              <Text style={styles.warningSubtitle}>Rs.{walletBalance} (Min Rs.1000 required to go on duty)</Text>
            </View>
          </View>
        )}

        {/* Duty Switch Card */}
        <View style={[styles.dutyCard, dutyOn && styles.dutyCardActive]}>
          <View style={styles.dutyContent}>
            <View style={styles.dutyInfo}>
              <View style={[styles.dutyIndicator, dutyOn && styles.dutyIndicatorOn]} />
              <View style={styles.dutyTextContainer}>
                <Text style={styles.dutyTitle}>{dutyOn ? 'Duty ON' : 'Duty OFF'}</Text>
                <Text style={styles.dutySubtitle}>{dutyOn ? 'Accepting rides' : 'Toggle to start accepting'}</Text>
              </View>
            </View>
            <Switch
              value={dutyOn}
              onValueChange={handleDutyToggle}
              trackColor={{ false: COLORS.border, true: COLORS.success }}
              thumbColor={COLORS.background}
              disabled={loading || walletBalance < 1000}
            />
          </View>
        </View>

        {/* Stats Row */}
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Ionicons name="wallet" size={28} color={COLORS.primary} />
            <Text style={styles.statValue}>Rs.{walletBalance.toFixed(0)}</Text>
            <Text style={styles.statLabel}>Wallet</Text>
          </View>

          <View style={styles.statCard}>
            <Ionicons name="cash" size={28} color={COLORS.secondary} />
            <Text style={styles.statValue}>Rs.{totalEarnings.toFixed(0)}</Text>
            <Text style={styles.statLabel}>Earnings</Text>
          </View>

          <View style={styles.statCard}>
            <Ionicons name="car" size={28} color={COLORS.success} />
            <Text style={styles.statValue}>{completedTrips}</Text>
            <Text style={styles.statLabel}>Trips</Text>
          </View>
        </View>

        {/* Queue Status */}
        {queueStatus && dutyOn && (
          <View style={styles.queueCard}>
            <Text style={styles.queueTitle}>Queue Status</Text>
            <View style={styles.queueRow}>
              <View style={styles.queueItem}>
                <Text style={styles.queueValue}>{queueStatus.continuous_trips_count || 0}</Text>
                <Text style={styles.queueLabel}>Continuous</Text>
              </View>
              <View style={styles.queueDivider} />
              <View style={styles.queueItem}>
                <Text style={styles.queueValue}>{queueStatus.in_queue ? `#${queueStatus.queue_position || '-'}` : '-'}</Text>
                <Text style={styles.queueLabel}>Position</Text>
              </View>
              <View style={styles.queueDivider} />
              <View style={styles.queueItem}>
                <Text style={styles.queueValue}>{queueStatus.total_in_queue || 0}</Text>
                <Text style={styles.queueLabel}>In Queue</Text>
              </View>
            </View>
          </View>
        )}

        {/* Incoming Request Card */}
        {incomingRequest && tripStatus === 'assigned' && (
          <View style={styles.requestCard}>
            <View style={styles.requestHeader}>
              <View style={styles.newRideBadge}>
                <Ionicons name="car" size={16} color={COLORS.background} />
                <Text style={styles.newRideText}>NEW RIDE</Text>
              </View>
              <Text style={styles.requestFare}>Rs.{incomingRequest.fare}</Text>
            </View>

            <View style={styles.locationRow}>
              <View style={[styles.locationDot, { backgroundColor: COLORS.primary }]} />
              <Text style={styles.locationText} numberOfLines={2}>{incomingRequest.pickup.address}</Text>
            </View>

            <View style={styles.locationLine} />

            <View style={styles.locationRow}>
              <View style={[styles.locationDot, { backgroundColor: COLORS.success }]} />
              <Text style={styles.locationText} numberOfLines={2}>{incomingRequest.drop.address}</Text>
            </View>

            <View style={styles.requestInfoRow}>
              <Text style={styles.infoText}>{incomingRequest.distance} km</Text>
              <Text style={styles.infoText}>Earn: Rs.{incomingRequest.driver_earning}</Text>
            </View>

            <View style={styles.requestActions}>
              <TouchableOpacity style={styles.acceptBtn} onPress={handleAcceptRide} disabled={loading}>
                {loading ? <ActivityIndicator color={COLORS.background} /> : (
                  <>
                    <Ionicons name="checkmark" size={24} color={COLORS.background} />
                    <Text style={styles.acceptBtnText}>ACCEPT</Text>
                  </>
                )}
              </TouchableOpacity>

              <TouchableOpacity style={styles.rejectBtn} onPress={handleRejectRide} disabled={loading}>
                <Ionicons name="close" size={24} color={COLORS.error} />
                <Text style={styles.rejectBtnText}>REJECT</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Current Trip Card */}
        {currentTrip && (tripStatus === 'accepted' || tripStatus === 'ongoing') && (
          <View style={styles.tripCard}>
            <View style={styles.tripHeader}>
              <Text style={styles.tripTitle}>{tripStatus === 'accepted' ? 'Go to Pickup' : 'Trip Ongoing'}</Text>
              <View style={[styles.tripBadge, tripStatus === 'ongoing' && styles.tripBadgeOngoing]}>
                <Text style={styles.tripBadgeText}>{tripStatus === 'accepted' ? 'PICKUP' : 'IN PROGRESS'}</Text>
              </View>
            </View>

            <View style={styles.locationRow}>
              <View style={[styles.locationDot, { backgroundColor: COLORS.primary }]} />
              <Text style={styles.locationText} numberOfLines={2}>{currentTrip.pickup.address}</Text>
            </View>

            <View style={styles.locationLine} />

            <View style={styles.locationRow}>
              <View style={[styles.locationDot, { backgroundColor: COLORS.success }]} />
              <Text style={styles.locationText} numberOfLines={2}>{currentTrip.drop.address}</Text>
            </View>

            <View style={styles.tripStats}>
              <View style={styles.tripStatItem}>
                <Text style={styles.tripStatLabel}>Distance</Text>
                <Text style={styles.tripStatValue}>{currentTrip.distance} km</Text>
              </View>
              <View style={styles.tripStatItem}>
                <Text style={styles.tripStatLabel}>Fare</Text>
                <Text style={styles.tripStatValue}>Rs.{currentTrip.fare}</Text>
              </View>
              <View style={styles.tripStatItem}>
                <Text style={styles.tripStatLabel}>Earning</Text>
                <Text style={[styles.tripStatValue, { color: COLORS.success }]}>Rs.{currentTrip.driver_earning}</Text>
              </View>
            </View>

            {tripStatus === 'accepted' && (
              <TouchableOpacity style={styles.primaryButton} onPress={handleStartTrip} disabled={loading}>
                {loading ? <ActivityIndicator color={COLORS.background} /> : (
                  <Text style={styles.primaryButtonText}>START TRIP</Text>
                )}
              </TouchableOpacity>
            )}
            {tripStatus === 'ongoing' && (
              <TouchableOpacity style={[styles.primaryButton, { backgroundColor: COLORS.success }]} onPress={handleCompleteTrip} disabled={loading}>
                {loading ? <ActivityIndicator color={COLORS.background} /> : (
                  <Text style={styles.primaryButtonText}>COMPLETE TRIP</Text>
                )}
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* Waiting for Rides */}
        {dutyOn && tripStatus === 'none' && walletBalance >= 1000 && (
          <View style={styles.waitingCard}>
            <Ionicons name="car-outline" size={48} color={COLORS.border} />
            <Text style={styles.waitingText}>Waiting for ride requests...</Text>
            <Text style={styles.waitingSubtext}>Pull down to refresh</Text>
          </View>
        )}

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: COLORS.primary,
  },
  headerLeft: { flex: 1 },
  greeting: { fontSize: 22, fontWeight: 'bold', color: COLORS.text },
  driverId: { fontSize: 12, color: COLORS.textLight, marginTop: 4 },
  logoutIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  // Content
  content: { flex: 1, paddingHorizontal: 16, paddingTop: 16 },
  // Vehicle Card
  vehicleCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  vehicleIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(46, 125, 50, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  vehicleInfo: { flex: 1 },
  vehicleNumber: { fontSize: 20, fontWeight: 'bold', color: COLORS.text },
  vehicleDetails: { fontSize: 14, color: COLORS.textLight, marginTop: 4 },
  // Warning Card
  warningCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFEBEE',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.error,
    gap: 12,
  },
  warningText: { flex: 1 },
  warningTitle: { fontSize: 14, fontWeight: 'bold', color: COLORS.error },
  warningSubtitle: { fontSize: 12, color: COLORS.error, marginTop: 2 },
  // Duty Card
  dutyCard: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  dutyCardActive: {
    backgroundColor: 'rgba(40, 167, 69, 0.1)',
    borderColor: COLORS.success,
  },
  dutyContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  dutyInfo: { flexDirection: 'row', alignItems: 'center' },
  dutyIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: COLORS.border,
    marginRight: 12,
  },
  dutyIndicatorOn: { backgroundColor: COLORS.success },
  dutyTextContainer: {},
  dutyTitle: { fontSize: 18, fontWeight: 'bold', color: COLORS.text },
  dutySubtitle: { fontSize: 13, color: COLORS.textLight, marginTop: 2 },
  // Stats Row
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  statCard: {
    flex: 1,
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  statValue: { fontSize: 18, fontWeight: 'bold', color: COLORS.text, marginTop: 8 },
  statLabel: { fontSize: 11, color: COLORS.textLight, marginTop: 4 },
  // Queue Card
  queueCard: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  queueTitle: { fontSize: 14, fontWeight: 'bold', color: COLORS.textLight, marginBottom: 12 },
  queueRow: { flexDirection: 'row', justifyContent: 'space-around' },
  queueItem: { alignItems: 'center' },
  queueValue: { fontSize: 20, fontWeight: 'bold', color: COLORS.secondary },
  queueLabel: { fontSize: 11, color: COLORS.textLight, marginTop: 4 },
  queueDivider: { width: 1, backgroundColor: COLORS.border },
  // Request Card
  requestCard: {
    backgroundColor: 'rgba(46, 125, 50, 0.05)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: COLORS.secondary,
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  newRideBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.secondary,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    gap: 4,
  },
  newRideText: { fontSize: 12, fontWeight: 'bold', color: COLORS.background },
  requestFare: { fontSize: 28, fontWeight: 'bold', color: COLORS.secondary },
  locationRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginVertical: 4 },
  locationDot: { width: 12, height: 12, borderRadius: 6 },
  locationText: { flex: 1, fontSize: 14, color: COLORS.text },
  locationLine: { width: 2, height: 20, backgroundColor: COLORS.border, marginLeft: 5, marginVertical: 2 },
  requestInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  infoText: { fontSize: 13, color: COLORS.textLight },
  requestActions: { flexDirection: 'row', gap: 12, marginTop: 16 },
  acceptBtn: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.secondary,
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  acceptBtnText: { fontSize: 16, fontWeight: 'bold', color: COLORS.background },
  rejectBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: COLORS.error,
    paddingVertical: 12,
    gap: 4,
  },
  rejectBtnText: { fontSize: 14, fontWeight: 'bold', color: COLORS.error },
  // Trip Card
  tripCard: {
    backgroundColor: COLORS.card,
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  tripHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  tripTitle: { fontSize: 18, fontWeight: 'bold', color: COLORS.text },
  tripBadge: {
    backgroundColor: COLORS.warning,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tripBadgeOngoing: { backgroundColor: COLORS.success },
  tripBadgeText: { fontSize: 11, fontWeight: 'bold', color: COLORS.background },
  tripStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: COLORS.border,
  },
  tripStatItem: { alignItems: 'center' },
  tripStatLabel: { fontSize: 11, color: COLORS.textLight },
  tripStatValue: { fontSize: 16, fontWeight: 'bold', color: COLORS.text, marginTop: 4 },
  // Primary Button
  primaryButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryButtonText: { fontSize: 16, fontWeight: 'bold', color: COLORS.text },
  // Waiting Card
  waitingCard: { alignItems: 'center', paddingVertical: 40 },
  waitingText: { fontSize: 16, color: COLORS.textLight, marginTop: 16 },
  waitingSubtext: { fontSize: 12, color: COLORS.border, marginTop: 4 },
  // Pending Screen
  pendingContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  pendingIcon: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255, 152, 0, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  pendingTitle: { fontSize: 24, fontWeight: 'bold', color: COLORS.warning, marginBottom: 12 },
  pendingMessage: { fontSize: 14, color: COLORS.textLight, textAlign: 'center', lineHeight: 22, marginBottom: 32 },
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.secondary,
    gap: 8,
    marginBottom: 16,
  },
  refreshButtonText: { fontSize: 16, fontWeight: '600', color: COLORS.secondary },
  logoutButtonSecondary: {
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  logoutButtonText: { fontSize: 14, color: COLORS.textLight },
});
