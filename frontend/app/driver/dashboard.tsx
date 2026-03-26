import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../store/authStore';
import { Ionicons } from '@expo/vector-icons';

// API imports
import {
  getDriverProfileComplete,
  getWallet,
  updateDutyStatus,
  getDriverRides,
} from '../../utils/api';

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
  offline: '#9E9E9E',
  online: '#4CAF50',
};

export default function DriverDashboard() {
  const router = useRouter();
  const { user, logout, setUser } = useAuthStore();
  
  // State
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [driverData, setDriverData] = useState<any>(null);
  const [isOnline, setIsOnline] = useState(false);
  const [walletBalance, setWalletBalance] = useState(0);
  const [todayEarnings, setTodayEarnings] = useState(0);
  const [availableRides, setAvailableRides] = useState<any[]>([]);
  const [ongoingTrip, setOngoingTrip] = useState<any>(null);
  const [completedTrips, setCompletedTrips] = useState<any[]>([]);
  const [toggleLoading, setToggleLoading] = useState(false);

  const driverId = user?.driver_id || '';
  const approvalStatus = user?.approval_status || driverData?.approval_status || 'pending';

  // Fetch all driver data
  const fetchDriverData = useCallback(async () => {
    if (!driverId) return;
    
    try {
      console.log('[Driver] Fetching data for:', driverId);
      
      // Get driver profile
      const profileRes = await getDriverProfileComplete(driverId);
      const driver = profileRes.data.driver;
      console.log('[Driver] Profile loaded:', driver?.full_name);
      setDriverData(driver);
      setIsOnline(driver?.duty_on || driver?.is_online || false);
      
      // Update auth store
      setUser({
        ...user,
        ...driver,
        approval_status: driver.approval_status,
      });

      // Get wallet balance
      try {
        const walletRes = await getWallet(driverId);
        setWalletBalance(walletRes.data.wallet?.balance || 0);
      } catch (e) {
        console.log('[Driver] Wallet fetch failed, using 0');
        setWalletBalance(0);
      }

      // Get rides
      try {
        const ridesRes = await getDriverRides(driverId);
        const rides = ridesRes.data.rides || [];
        
        // Filter rides by status
        const available = rides.filter((r: any) => r.status === 'requested' || r.status === 'assigned');
        const ongoing = rides.find((r: any) => r.status === 'accepted' || r.status === 'ongoing');
        const completed = rides.filter((r: any) => r.status === 'completed');
        
        setAvailableRides(available);
        setOngoingTrip(ongoing || null);
        setCompletedTrips(completed);
        
        // Calculate today's earnings
        const today = new Date().toDateString();
        const todayCompleted = completed.filter((r: any) => {
          const rideDate = new Date(r.completed_at || r.created_at).toDateString();
          return rideDate === today;
        });
        const earnings = todayCompleted.reduce((sum: number, r: any) => sum + (r.driver_earning || 0), 0);
        setTodayEarnings(earnings);
      } catch (e) {
        console.log('[Driver] Rides fetch failed');
        setAvailableRides([]);
        setOngoingTrip(null);
        setCompletedTrips([]);
        setTodayEarnings(0);
      }

    } catch (error) {
      console.error('[Driver] Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  }, [driverId]);

  useEffect(() => {
    fetchDriverData();
  }, [fetchDriverData]);

  // Pull to refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchDriverData();
    setRefreshing(false);
  }, [fetchDriverData]);

  // Toggle Online/Offline
  const handleToggleOnline = async () => {
    if (walletBalance < 1000 && !isOnline) {
      Alert.alert(
        'Low Balance',
        'Minimum ₹1000 wallet balance required to go online. Please contact admin to add balance.'
      );
      return;
    }

    setToggleLoading(true);
    try {
      const newStatus = !isOnline;
      console.log('[Driver] Toggling online status to:', newStatus);
      
      await updateDutyStatus(driverId, { 
        duty_on: newStatus, 
        is_online: newStatus,
        go_home_mode: false 
      });
      
      setIsOnline(newStatus);
      Alert.alert(
        newStatus ? 'You\'re Online!' : 'You\'re Offline',
        newStatus ? 'You will now receive ride requests.' : 'You won\'t receive ride requests.'
      );
    } catch (error: any) {
      console.error('[Driver] Toggle failed:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update status');
    } finally {
      setToggleLoading(false);
    }
  };

  // Logout handler
  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: () => logout() }
    ]);
  };

  // Get driver info
  const driverName = driverData?.full_name || driverData?.personal_details?.full_name || user?.name || 'Driver';
  const driverPhoto = driverData?.driver_photos?.driver_photo || driverData?.documents?.driver_photo || null;

  // Loading state
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // PENDING APPROVAL SCREEN
  if (approvalStatus === 'pending') {
    return (
      <View style={styles.container}>
        <View style={styles.pendingContainer}>
          <View style={styles.pendingIcon}>
            <Ionicons name="time-outline" size={80} color={COLORS.warning} />
          </View>
          <Text style={styles.pendingTitle}>Waiting for Admin Approval</Text>
          <Text style={styles.pendingMessage}>
            Your registration is under review.{'\n'}
            Admin will verify your documents and approve your account.
          </Text>
          <Text style={styles.pendingDriverId}>Driver ID: {driverId}</Text>
          
          <TouchableOpacity style={styles.refreshBtn} onPress={onRefresh}>
            <Ionicons name="refresh" size={20} color={COLORS.secondary} />
            <Text style={styles.refreshBtnText}>Check Status</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.logoutBtnSecondary} onPress={handleLogout}>
            <Text style={styles.logoutBtnText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // REJECTED SCREEN
  if (approvalStatus === 'rejected') {
    return (
      <View style={styles.container}>
        <View style={styles.pendingContainer}>
          <View style={[styles.pendingIcon, { backgroundColor: 'rgba(220, 53, 69, 0.1)' }]}>
            <Ionicons name="close-circle-outline" size={80} color={COLORS.error} />
          </View>
          <Text style={[styles.pendingTitle, { color: COLORS.error }]}>Application Rejected</Text>
          <Text style={styles.pendingMessage}>
            Unfortunately, your application was not approved.{'\n'}
            Please contact support for more information.
          </Text>
          
          <TouchableOpacity style={styles.logoutBtnSecondary} onPress={handleLogout}>
            <Text style={styles.logoutBtnText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // APPROVED - DRIVER HOME SCREEN
  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.profileSection}>
          {driverPhoto ? (
            <Image source={{ uri: driverPhoto }} style={styles.profilePhoto} />
          ) : (
            <View style={styles.profilePhotoPlaceholder}>
              <Ionicons name="person" size={32} color={COLORS.textLight} />
            </View>
          )}
          <View style={styles.profileInfo}>
            <Text style={styles.welcomeText}>Welcome back,</Text>
            <Text style={styles.driverName}>{driverName}</Text>
          </View>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutIcon}>
          <Ionicons name="log-out-outline" size={24} color={COLORS.text} />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[COLORS.secondary]} />
        }
      >
        {/* Online/Offline Status Card */}
        <View style={[styles.statusCard, isOnline && styles.statusCardOnline]}>
          <View style={styles.statusInfo}>
            <View style={[styles.statusDot, isOnline && styles.statusDotOnline]} />
            <View>
              <Text style={styles.statusTitle}>
                {isOnline ? "You're Online" : "You're Offline"}
              </Text>
              <Text style={styles.statusSubtitle}>
                {isOnline ? 'Accepting ride requests' : 'Go online to receive rides'}
              </Text>
            </View>
          </View>
          
          <TouchableOpacity
            style={[styles.toggleBtn, isOnline && styles.toggleBtnOffline]}
            onPress={handleToggleOnline}
            disabled={toggleLoading}
          >
            {toggleLoading ? (
              <ActivityIndicator size="small" color={isOnline ? COLORS.error : COLORS.background} />
            ) : (
              <Text style={[styles.toggleBtnText, isOnline && styles.toggleBtnTextOffline]}>
                {isOnline ? 'Go Offline' : 'Go Online'}
              </Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Wallet Balance Warning */}
        {walletBalance < 1000 && (
          <View style={styles.warningCard}>
            <Ionicons name="warning" size={20} color={COLORS.error} />
            <Text style={styles.warningText}>
              Low balance! Min ₹1000 required to go online. Current: ₹{walletBalance}
            </Text>
          </View>
        )}

        {/* Wallet & Earnings */}
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Ionicons name="wallet-outline" size={28} color={COLORS.primary} />
            <Text style={styles.statValue}>₹{walletBalance.toFixed(0)}</Text>
            <Text style={styles.statLabel}>Wallet Balance</Text>
          </View>
          
          <View style={styles.statCard}>
            <Ionicons name="cash-outline" size={28} color={COLORS.success} />
            <Text style={styles.statValue}>₹{todayEarnings.toFixed(0)}</Text>
            <Text style={styles.statLabel}>Today's Earnings</Text>
          </View>
        </View>

        {/* Available Rides Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Available Rides</Text>
          {availableRides.length === 0 ? (
            <View style={styles.emptyCard}>
              <Ionicons name="car-outline" size={40} color={COLORS.border} />
              <Text style={styles.emptyText}>No available rides</Text>
              <Text style={styles.emptySubtext}>
                {isOnline ? 'Waiting for ride requests...' : 'Go online to receive rides'}
              </Text>
            </View>
          ) : (
            availableRides.map((ride, index) => (
              <View key={ride.booking_id || index} style={styles.rideCard}>
                <View style={styles.rideHeader}>
                  <Text style={styles.rideId}>#{ride.booking_id?.slice(0, 10)}</Text>
                  <Text style={styles.rideFare}>₹{ride.fare || 0}</Text>
                </View>
                <View style={styles.rideLocation}>
                  <View style={styles.locationDot} />
                  <Text style={styles.locationText} numberOfLines={1}>{ride.pickup?.address || 'N/A'}</Text>
                </View>
                <View style={styles.rideLocation}>
                  <View style={[styles.locationDot, { backgroundColor: COLORS.success }]} />
                  <Text style={styles.locationText} numberOfLines={1}>{ride.drop?.address || 'N/A'}</Text>
                </View>
              </View>
            ))
          )}
        </View>

        {/* Ongoing Trip Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Ongoing Trip</Text>
          {!ongoingTrip ? (
            <View style={styles.emptyCard}>
              <Ionicons name="navigate-outline" size={40} color={COLORS.border} />
              <Text style={styles.emptyText}>No ongoing trip</Text>
              <Text style={styles.emptySubtext}>Your active trip will appear here</Text>
            </View>
          ) : (
            <View style={[styles.rideCard, styles.ongoingCard]}>
              <View style={styles.rideHeader}>
                <View style={styles.ongoingBadge}>
                  <Text style={styles.ongoingBadgeText}>IN PROGRESS</Text>
                </View>
                <Text style={styles.rideFare}>₹{ongoingTrip.fare || 0}</Text>
              </View>
              <View style={styles.rideLocation}>
                <View style={styles.locationDot} />
                <Text style={styles.locationText} numberOfLines={1}>{ongoingTrip.pickup?.address || 'N/A'}</Text>
              </View>
              <View style={styles.rideLocation}>
                <View style={[styles.locationDot, { backgroundColor: COLORS.success }]} />
                <Text style={styles.locationText} numberOfLines={1}>{ongoingTrip.drop?.address || 'N/A'}</Text>
              </View>
            </View>
          )}
        </View>

        {/* Completed Trips Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Completed Trips ({completedTrips.length})</Text>
          {completedTrips.length === 0 ? (
            <View style={styles.emptyCard}>
              <Ionicons name="checkmark-circle-outline" size={40} color={COLORS.border} />
              <Text style={styles.emptyText}>No completed trips</Text>
              <Text style={styles.emptySubtext}>Your completed trips will appear here</Text>
            </View>
          ) : (
            completedTrips.slice(0, 3).map((ride, index) => (
              <View key={ride.booking_id || index} style={styles.completedCard}>
                <View style={styles.completedInfo}>
                  <Text style={styles.completedId}>#{ride.booking_id?.slice(0, 10)}</Text>
                  <Text style={styles.completedLocation} numberOfLines={1}>
                    {ride.pickup?.address?.slice(0, 20)}... → {ride.drop?.address?.slice(0, 20)}...
                  </Text>
                </View>
                <Text style={styles.completedEarning}>+₹{ride.driver_earning || 0}</Text>
              </View>
            ))
          )}
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: COLORS.textLight,
  },
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
  profileSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profilePhoto: {
    width: 50,
    height: 50,
    borderRadius: 25,
    borderWidth: 2,
    borderColor: COLORS.background,
  },
  profilePhotoPlaceholder: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: COLORS.card,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.background,
  },
  profileInfo: {
    marginLeft: 12,
  },
  welcomeText: {
    fontSize: 12,
    color: COLORS.textLight,
  },
  driverName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  logoutIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  // Content
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  // Status Card
  statusCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: COLORS.offline,
  },
  statusCardOnline: {
    borderColor: COLORS.online,
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
  },
  statusInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: COLORS.offline,
    marginRight: 12,
  },
  statusDotOnline: {
    backgroundColor: COLORS.online,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  statusSubtitle: {
    fontSize: 12,
    color: COLORS.textLight,
    marginTop: 2,
  },
  toggleBtn: {
    backgroundColor: COLORS.secondary,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    minWidth: 100,
    alignItems: 'center',
  },
  toggleBtnOffline: {
    backgroundColor: COLORS.card,
    borderWidth: 2,
    borderColor: COLORS.error,
  },
  toggleBtnText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.background,
  },
  toggleBtnTextOffline: {
    color: COLORS.error,
  },
  // Warning Card
  warningCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFEBEE',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    gap: 10,
    borderWidth: 1,
    borderColor: COLORS.error,
  },
  warningText: {
    flex: 1,
    fontSize: 13,
    color: COLORS.error,
  },
  // Stats Row
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  statValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: COLORS.text,
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.textLight,
    marginTop: 4,
  },
  // Section
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 12,
  },
  // Empty Card
  emptyCard: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  emptyText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.textLight,
    marginTop: 12,
  },
  emptySubtext: {
    fontSize: 12,
    color: COLORS.border,
    marginTop: 4,
    textAlign: 'center',
  },
  // Ride Card
  rideCard: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  rideHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  rideId: {
    fontSize: 12,
    color: COLORS.textLight,
    fontWeight: '600',
  },
  rideFare: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.secondary,
  },
  rideLocation: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  locationDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.primary,
    marginRight: 10,
  },
  locationText: {
    flex: 1,
    fontSize: 13,
    color: COLORS.text,
  },
  // Ongoing Card
  ongoingCard: {
    borderColor: COLORS.warning,
    backgroundColor: 'rgba(255, 152, 0, 0.1)',
  },
  ongoingBadge: {
    backgroundColor: COLORS.warning,
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 10,
  },
  ongoingBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: COLORS.background,
  },
  // Completed Card
  completedCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  completedInfo: {
    flex: 1,
  },
  completedId: {
    fontSize: 12,
    color: COLORS.textLight,
    fontWeight: '600',
  },
  completedLocation: {
    fontSize: 12,
    color: COLORS.text,
    marginTop: 4,
  },
  completedEarning: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.success,
  },
  // Pending Screen
  pendingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  pendingIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 152, 0, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  pendingTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: COLORS.warning,
    marginBottom: 12,
    textAlign: 'center',
  },
  pendingMessage: {
    fontSize: 14,
    color: COLORS.textLight,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 16,
  },
  pendingDriverId: {
    fontSize: 14,
    color: COLORS.secondary,
    fontWeight: '600',
    marginBottom: 32,
  },
  refreshBtn: {
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
  refreshBtnText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.secondary,
  },
  logoutBtnSecondary: {
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  logoutBtnText: {
    fontSize: 14,
    color: COLORS.textLight,
  },
});
