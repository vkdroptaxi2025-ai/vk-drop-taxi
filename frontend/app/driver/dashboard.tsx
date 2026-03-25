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
  Animated,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
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
  
  const [approvalStatus, setApprovalStatus] = useState(user?.approval_status || 'pending');
  const [dutyOn, setDutyOn] = useState(false);
  const [goHomeMode, setGoHomeMode] = useState(false);
  const [walletBalance, setWalletBalance] = useState(0);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [queueStatus, setQueueStatus] = useState<any>(null);
  const [currentTrip, setCurrentTrip] = useState<CurrentTrip | null>(null);
  const [tripStatus, setTripStatus] = useState<TripStatus>('none');
  const [showGoHomeModal, setShowGoHomeModal] = useState(false);
  const [homeAddress, setHomeAddress] = useState('');
  const [incomingRequest, setIncomingRequest] = useState<CurrentTrip | null>(null);
  const [showNewBookingNotification, setShowNewBookingNotification] = useState(false);

  // Animation for duty switch glow
  const glowAnim = new Animated.Value(0);

  const driverId = user?.driver_id || '';
  const driverName = user?.personal_details?.full_name || user?.name || 'Driver';
  const vehicleType = user?.vehicle_details?.vehicle_type || user?.vehicle_type || 'sedan';
  const vehicleNumber = user?.vehicle_details?.vehicle_number || user?.vehicle_number || '';

  useEffect(() => {
    if (driverId) {
      fetchDriverData();
    }
  }, [driverId]);

  useEffect(() => {
    if (dutyOn) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(glowAnim, { toValue: 1, duration: 1000, useNativeDriver: false }),
          Animated.timing(glowAnim, { toValue: 0.3, duration: 1000, useNativeDriver: false }),
        ])
      ).start();
    } else {
      glowAnim.setValue(0);
    }
  }, [dutyOn]);

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

      const walletRes = await getWallet(driverId);
      setWalletBalance(walletRes.data.wallet.balance || 0);

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
      setApprovalStatus(driver.approval_status);
      setDutyOn(driver.duty_on || false);
      setGoHomeMode(driver.go_home_mode || false);
      setUser(driver);

      const walletRes = await getWallet(driverId);
      setWalletBalance(walletRes.data.wallet.balance || 0);

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
      Alert.alert('Low Balance', 'Minimum ₹1000 wallet balance required to go on duty.');
      return;
    }

    setLoading(true);
    try {
      await updateDutyStatus(driverId, { duty_on: value, go_home_mode: false });
      setDutyOn(value);
      setGoHomeMode(false);
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
    Alert.alert('Complete Trip', `Earning: ₹${currentTrip.driver_earning}`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Complete',
        onPress: async () => {
          setLoading(true);
          try {
            const res = await completeTrip(currentTrip.booking_id);
            Alert.alert('Trip Completed!', `You earned ₹${res.data.earning || currentTrip.driver_earning}`);
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

  // Pending Approval Screen
  if (approvalStatus === 'pending') {
    return (
      <View style={styles.container}>
        <LinearGradient colors={['#1A1A1A', '#0D0D0D']} style={styles.gradient}>
          <View style={styles.centerContainer}>
            <View style={styles.pendingIcon}>
              <Ionicons name="time" size={60} color={Colors.gold} />
            </View>
            <Text style={styles.centerTitle}>Approval Pending</Text>
            <Text style={styles.centerText}>Your registration is under review. You'll be notified once approved.</Text>
            <Button title="Refresh Status" onPress={fetchDriverData} variant="outline" style={styles.refreshBtn} />
            <Button title="Logout" onPress={logout} variant="outline" style={styles.logoutBtnCenter} />
          </View>
        </LinearGradient>
      </View>
    );
  }

  // Rejected Screen
  if (approvalStatus === 'rejected') {
    return (
      <View style={styles.container}>
        <LinearGradient colors={['#1A1A1A', '#0D0D0D']} style={styles.gradient}>
          <View style={styles.centerContainer}>
            <View style={[styles.pendingIcon, { backgroundColor: 'rgba(255, 82, 82, 0.1)' }]}>
              <Ionicons name="close-circle" size={60} color={Colors.error} />
            </View>
            <Text style={[styles.centerTitle, { color: Colors.error }]}>Application Rejected</Text>
            <Text style={styles.centerText}>Your application was not approved. Please contact support.</Text>
            <Button title="Logout" onPress={logout} variant="outline" style={styles.logoutBtnCenter} />
          </View>
        </LinearGradient>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#1A1A1A', '#0D0D0D']} style={styles.gradient}>
        {/* Notification Banner */}
        {showNewBookingNotification && (
          <View style={styles.notificationBanner}>
            <LinearGradient colors={[Colors.greenLight, Colors.greenDark]} style={styles.notificationGradient}>
              <Ionicons name="notifications" size={20} color={Colors.white} />
              <Text style={styles.notificationText}>New Booking Request!</Text>
            </LinearGradient>
          </View>
        )}

        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hello, {driverName}!</Text>
            <Text style={styles.subtitle}>{vehicleType.toUpperCase()} • {vehicleNumber}</Text>
          </View>
          <TouchableOpacity onPress={logout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={Colors.gold} />
          </TouchableOpacity>
        </View>

        <ScrollView
          style={styles.content}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.gold} />}
          showsVerticalScrollIndicator={false}
        >
          {/* Wallet Warning */}
          {walletBalance < 1000 && (
            <View style={styles.warningCard}>
              <LinearGradient colors={[Colors.error, '#B71C1C']} style={styles.warningGradient}>
                <Ionicons name="warning" size={24} color={Colors.white} />
                <View style={styles.warningText}>
                  <Text style={styles.warningTitle}>Low Wallet Balance</Text>
                  <Text style={styles.warningSubtitle}>₹{walletBalance} (Min ₹1000 required)</Text>
                </View>
                <TouchableOpacity style={styles.addMoneyBtnSmall}>
                  <Text style={styles.addMoneyTextSmall}>Add Money</Text>
                </TouchableOpacity>
              </LinearGradient>
            </View>
          )}

          {/* Duty Switch Card */}
          <View style={styles.dutyCard}>
            <LinearGradient
              colors={dutyOn ? ['rgba(76, 175, 80, 0.2)', 'rgba(76, 175, 80, 0.05)'] : ['#2C2C2E', '#1C1C1E']}
              style={styles.dutyGradient}
            >
              <View style={styles.dutyContent}>
                <View style={styles.dutyInfo}>
                  <Animated.View 
                    style={[
                      styles.dutyGlow,
                      dutyOn && {
                        opacity: glowAnim,
                        backgroundColor: Colors.glowGreen,
                      }
                    ]}
                  />
                  <View style={[styles.dutyIndicator, dutyOn && styles.dutyIndicatorOn]}>
                    <Ionicons name={dutyOn ? 'radio-button-on' : 'radio-button-off'} size={24} color={dutyOn ? Colors.greenLight : Colors.gray} />
                  </View>
                  <View style={styles.dutyTextContainer}>
                    <Text style={styles.dutyTitle}>{dutyOn ? 'Duty ON' : 'Duty OFF'}</Text>
                    <Text style={styles.dutySubtitle}>{dutyOn ? 'Accepting rides' : 'Toggle to start'}</Text>
                  </View>
                </View>
                <Switch
                  value={dutyOn}
                  onValueChange={handleDutyToggle}
                  trackColor={{ false: Colors.gray, true: Colors.greenLight }}
                  thumbColor={Colors.white}
                  disabled={loading || walletBalance < 1000}
                  style={styles.dutySwitch}
                />
              </View>
            </LinearGradient>
          </View>

          {/* Wallet & Earnings Row */}
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <LinearGradient colors={['rgba(255, 215, 0, 0.15)', 'rgba(255, 215, 0, 0.05)']} style={styles.statGradient}>
                <Ionicons name="wallet" size={28} color={Colors.gold} />
                <Text style={styles.statValue}>₹{walletBalance.toFixed(0)}</Text>
                <Text style={styles.statLabel}>Wallet</Text>
              </LinearGradient>
            </View>

            <View style={styles.statCard}>
              <LinearGradient colors={['rgba(76, 175, 80, 0.15)', 'rgba(76, 175, 80, 0.05)']} style={styles.statGradient}>
                <Ionicons name="cash" size={28} color={Colors.greenLight} />
                <Text style={styles.statValue}>₹{user?.earnings?.toFixed(0) || 0}</Text>
                <Text style={styles.statLabel}>Earnings</Text>
              </LinearGradient>
            </View>
          </View>

          {/* Queue Status */}
          {queueStatus && dutyOn && (
            <View style={styles.queueCard}>
              <Text style={styles.queueTitle}>Queue Status</Text>
              <View style={styles.queueRow}>
                <View style={styles.queueItem}>
                  <Text style={styles.queueValue}>{queueStatus.continuous_trips_count || 0}</Text>
                  <Text style={styles.queueLabel}>Trips</Text>
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

          {/* Incoming Request Modal-Style Card */}
          {incomingRequest && tripStatus === 'assigned' && (
            <View style={styles.requestCard}>
              <LinearGradient colors={['#1B4D3E', '#0D2818']} style={styles.requestGradient}>
                <View style={styles.requestHeader}>
                  <View style={styles.requestBadge}>
                    <Ionicons name="car" size={16} color={Colors.white} />
                    <Text style={styles.requestBadgeText}>NEW RIDE</Text>
                  </View>
                  <Text style={styles.requestFare}>₹{incomingRequest.fare}</Text>
                </View>

                <View style={styles.locationRow}>
                  <View style={styles.locationIcon}>
                    <Ionicons name="location" size={16} color={Colors.gold} />
                  </View>
                  <Text style={styles.locationText} numberOfLines={2}>{incomingRequest.pickup.address}</Text>
                </View>

                <View style={styles.locationLine} />

                <View style={styles.locationRow}>
                  <View style={[styles.locationIcon, { backgroundColor: 'rgba(76, 175, 80, 0.2)' }]}>
                    <Ionicons name="flag" size={16} color={Colors.greenLight} />
                  </View>
                  <Text style={styles.locationText} numberOfLines={2}>{incomingRequest.drop.address}</Text>
                </View>

                <View style={styles.requestInfo}>
                  <Text style={styles.infoText}>{incomingRequest.distance} km</Text>
                  <Text style={styles.infoText}>Earn: ₹{incomingRequest.driver_earning}</Text>
                </View>

                <View style={styles.requestActions}>
                  <TouchableOpacity style={styles.acceptBtn} onPress={handleAcceptRide} disabled={loading}>
                    <LinearGradient colors={[Colors.greenLight, Colors.greenDark]} style={styles.actionBtnGradient}>
                      {loading ? <ActivityIndicator color={Colors.white} /> : (
                        <>
                          <Ionicons name="checkmark" size={24} color={Colors.white} />
                          <Text style={styles.actionBtnText}>ACCEPT</Text>
                        </>
                      )}
                    </LinearGradient>
                  </TouchableOpacity>

                  <TouchableOpacity style={styles.rejectBtn} onPress={handleRejectRide} disabled={loading}>
                    <View style={styles.rejectBtnInner}>
                      <Ionicons name="close" size={24} color={Colors.error} />
                      <Text style={styles.rejectBtnText}>REJECT</Text>
                    </View>
                  </TouchableOpacity>
                </View>
              </LinearGradient>
            </View>
          )}

          {/* Current Trip Card */}
          {currentTrip && (tripStatus === 'accepted' || tripStatus === 'ongoing') && (
            <View style={styles.tripCard}>
              <LinearGradient colors={['#2C2C2E', '#1C1C1E']} style={styles.tripGradient}>
                <View style={styles.tripHeader}>
                  <Text style={styles.tripTitle}>{tripStatus === 'accepted' ? 'Go to Pickup' : 'Trip Ongoing'}</Text>
                  <View style={[styles.tripBadge, tripStatus === 'ongoing' && styles.tripBadgeOngoing]}>
                    <Text style={styles.tripBadgeText}>{tripStatus === 'accepted' ? 'PICKUP' : 'IN PROGRESS'}</Text>
                  </View>
                </View>

                <View style={styles.locationRow}>
                  <View style={styles.locationIcon}>
                    <Ionicons name="location" size={16} color={Colors.gold} />
                  </View>
                  <Text style={styles.locationText} numberOfLines={2}>{currentTrip.pickup.address}</Text>
                </View>

                <View style={styles.locationLine} />

                <View style={styles.locationRow}>
                  <View style={[styles.locationIcon, { backgroundColor: 'rgba(76, 175, 80, 0.2)' }]}>
                    <Ionicons name="flag" size={16} color={Colors.greenLight} />
                  </View>
                  <Text style={styles.locationText} numberOfLines={2}>{currentTrip.drop.address}</Text>
                </View>

                <View style={styles.tripStats}>
                  <View style={styles.tripStatItem}>
                    <Text style={styles.tripStatLabel}>Distance</Text>
                    <Text style={styles.tripStatValue}>{currentTrip.distance} km</Text>
                  </View>
                  <View style={styles.tripStatItem}>
                    <Text style={styles.tripStatLabel}>Fare</Text>
                    <Text style={styles.tripStatValue}>₹{currentTrip.fare}</Text>
                  </View>
                  <View style={styles.tripStatItem}>
                    <Text style={styles.tripStatLabel}>Earning</Text>
                    <Text style={[styles.tripStatValue, { color: Colors.greenLight }]}>₹{currentTrip.driver_earning}</Text>
                  </View>
                </View>

                {tripStatus === 'accepted' && (
                  <Button title="Start Trip" onPress={handleStartTrip} loading={loading} variant="gold" />
                )}
                {tripStatus === 'ongoing' && (
                  <Button title="Complete Trip" onPress={handleCompleteTrip} loading={loading} variant="green" />
                )}
              </LinearGradient>
            </View>
          )}

          {/* Waiting for Rides */}
          {dutyOn && tripStatus === 'none' && walletBalance >= 1000 && (
            <View style={styles.waitingCard}>
              <Ionicons name="car-outline" size={48} color={Colors.gray} />
              <Text style={styles.waitingText}>Waiting for ride requests...</Text>
              <Text style={styles.waitingSubtext}>Pull down to refresh</Text>
            </View>
          )}

          <View style={{ height: 40 }} />
        </ScrollView>
      </LinearGradient>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  gradient: { flex: 1 },
  centerContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  pendingIcon: { width: 100, height: 100, borderRadius: 50, backgroundColor: 'rgba(255, 215, 0, 0.1)', alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  centerTitle: { fontSize: 24, fontWeight: 'bold', color: Colors.gold, marginBottom: 12 },
  centerText: { fontSize: 14, color: Colors.textLight, textAlign: 'center', lineHeight: 22 },
  refreshBtn: { marginTop: 32, minWidth: 200 },
  logoutBtnCenter: { marginTop: 12 },
  notificationBanner: { position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1000 },
  notificationGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, paddingTop: 50, gap: 8 },
  notificationText: { color: Colors.white, fontSize: 16, fontWeight: 'bold' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 60 },
  greeting: { fontSize: 24, fontWeight: 'bold', color: Colors.text },
  subtitle: { fontSize: 13, color: Colors.gold, marginTop: 4 },
  logoutButton: { padding: 10, backgroundColor: Colors.cardBackground, borderRadius: 12 },
  content: { flex: 1, paddingHorizontal: 16 },
  warningCard: { marginBottom: 16, borderRadius: 16, overflow: 'hidden' },
  warningGradient: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  warningText: { flex: 1 },
  warningTitle: { fontSize: 14, fontWeight: 'bold', color: Colors.white },
  warningSubtitle: { fontSize: 12, color: Colors.white, opacity: 0.9 },
  addMoneyBtnSmall: { backgroundColor: 'rgba(255,255,255,0.2)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  addMoneyTextSmall: { fontSize: 12, fontWeight: '600', color: Colors.white },
  dutyCard: { marginBottom: 16, borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: Colors.border },
  dutyGradient: { padding: 20 },
  dutyContent: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  dutyInfo: { flexDirection: 'row', alignItems: 'center' },
  dutyGlow: { position: 'absolute', width: 60, height: 60, borderRadius: 30, left: -5, top: -5 },
  dutyIndicator: { width: 50, height: 50, borderRadius: 25, backgroundColor: Colors.cardBackground, alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: Colors.border },
  dutyIndicatorOn: { borderColor: Colors.greenLight },
  dutyTextContainer: { marginLeft: 16 },
  dutyTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.text },
  dutySubtitle: { fontSize: 13, color: Colors.textLight, marginTop: 2 },
  dutySwitch: { transform: [{ scaleX: 1.3 }, { scaleY: 1.3 }] },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  statCard: { flex: 1, borderRadius: 16, overflow: 'hidden', borderWidth: 1, borderColor: Colors.border },
  statGradient: { padding: 20, alignItems: 'center' },
  statValue: { fontSize: 24, fontWeight: 'bold', color: Colors.text, marginTop: 8 },
  statLabel: { fontSize: 12, color: Colors.textLight, marginTop: 4 },
  queueCard: { backgroundColor: Colors.cardBackground, borderRadius: 16, padding: 16, marginBottom: 16, borderWidth: 1, borderColor: Colors.border },
  queueTitle: { fontSize: 14, fontWeight: 'bold', color: Colors.textLight, marginBottom: 12 },
  queueRow: { flexDirection: 'row', justifyContent: 'space-around' },
  queueItem: { alignItems: 'center' },
  queueValue: { fontSize: 20, fontWeight: 'bold', color: Colors.gold },
  queueLabel: { fontSize: 11, color: Colors.textLight, marginTop: 4 },
  queueDivider: { width: 1, backgroundColor: Colors.border },
  requestCard: { marginBottom: 16, borderRadius: 20, overflow: 'hidden', borderWidth: 2, borderColor: Colors.greenLight },
  requestGradient: { padding: 20 },
  requestHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  requestBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.greenLight, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, gap: 4 },
  requestBadgeText: { fontSize: 12, fontWeight: 'bold', color: Colors.white },
  requestFare: { fontSize: 28, fontWeight: 'bold', color: Colors.gold },
  locationRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginVertical: 6 },
  locationIcon: { width: 32, height: 32, borderRadius: 16, backgroundColor: 'rgba(255, 215, 0, 0.2)', alignItems: 'center', justifyContent: 'center' },
  locationText: { flex: 1, fontSize: 14, color: Colors.text },
  locationLine: { width: 2, height: 20, backgroundColor: Colors.border, marginLeft: 15, marginVertical: 2 },
  requestInfo: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.1)' },
  infoText: { fontSize: 13, color: Colors.textLight },
  requestActions: { flexDirection: 'row', gap: 12, marginTop: 16 },
  acceptBtn: { flex: 2, borderRadius: 14, overflow: 'hidden' },
  actionBtnGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 14, gap: 8 },
  actionBtnText: { fontSize: 16, fontWeight: 'bold', color: Colors.white },
  rejectBtn: { flex: 1, borderRadius: 14, borderWidth: 2, borderColor: Colors.error },
  rejectBtnInner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, gap: 4 },
  rejectBtnText: { fontSize: 14, fontWeight: 'bold', color: Colors.error },
  tripCard: { marginBottom: 16, borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: Colors.borderGold },
  tripGradient: { padding: 20 },
  tripHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  tripTitle: { fontSize: 18, fontWeight: 'bold', color: Colors.text },
  tripBadge: { backgroundColor: Colors.warning, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  tripBadgeOngoing: { backgroundColor: Colors.greenLight },
  tripBadgeText: { fontSize: 11, fontWeight: 'bold', color: Colors.white },
  tripStats: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 16, paddingVertical: 12, borderTopWidth: 1, borderBottomWidth: 1, borderColor: Colors.border },
  tripStatItem: { alignItems: 'center' },
  tripStatLabel: { fontSize: 11, color: Colors.textLight },
  tripStatValue: { fontSize: 16, fontWeight: 'bold', color: Colors.text, marginTop: 4 },
  waitingCard: { alignItems: 'center', paddingVertical: 40 },
  waitingText: { fontSize: 16, color: Colors.gray, marginTop: 16 },
  waitingSubtext: { fontSize: 12, color: Colors.gray, marginTop: 4 },
});
