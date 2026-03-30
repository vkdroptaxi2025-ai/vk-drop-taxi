import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  Image,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Colors } from '../../utils/colors';
import {
  getAllDrivers,
  getDriverFullDetails,
  approveDriver,
  resetDriverStatus,
  deleteDriver,
  getAllCustomers,
  getAllBookings,
  getAdminStats,
  getTariffs,
  updateTariff,
  createSmartBooking,
  addWalletMoney,
} from '../../utils/api';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';

export default function AdminDashboard() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'stats' | 'drivers' | 'bookings' | 'dispatch'>('stats');
  const [stats, setStats] = useState<any>(null);
  const [drivers, setDrivers] = useState<any[]>([]);
  const [customers, setCustomers] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [tariffs, setTariffs] = useState<any[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingDriverDetails, setLoadingDriverDetails] = useState(false);
  const [fullDriverDetails, setFullDriverDetails] = useState<any>(null);

  // Manual Assignment State
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignmentMode, setAssignmentMode] = useState<'auto' | 'manual'>('auto');
  const [manualDriverId, setManualDriverId] = useState('');
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropAddress, setDropAddress] = useState('');
  const [vehicleType, setVehicleType] = useState<'sedan' | 'suv'>('sedan');
  const [customerId, setCustomerId] = useState('');

  // Wallet Add State
  const [showWalletModal, setShowWalletModal] = useState(false);
  const [walletDriverId, setWalletDriverId] = useState('');
  const [walletDriverName, setWalletDriverName] = useState('');
  const [walletAmount, setWalletAmount] = useState('');

  useEffect(() => {
    fetchStats();
    fetchDrivers();
    fetchTariffs();
    fetchCustomers();
  }, []);

  useEffect(() => {
    if (activeTab === 'bookings') fetchBookings();
  }, [activeTab]);

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchStats(), fetchDrivers(), fetchBookings()]);
    setRefreshing(false);
  };

  const fetchStats = async () => {
    try {
      const response = await getAdminStats();
      setStats(response.data.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchDrivers = async () => {
    try {
      const response = await getAllDrivers();
      setDrivers(response.data.drivers || []);
    } catch (error) {
      console.error('Failed to fetch drivers:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await getAllCustomers();
      setCustomers(response.data.customers || []);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await getAllBookings();
      setBookings(response.data.bookings || []);
    } catch (error) {
      console.error('Failed to fetch bookings:', error);
    } finally {
      setLoading(false);
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

  const handleApproveDriver = async (driverId: string, status: 'approved' | 'rejected', rejectionReason?: string) => {
    console.log('[Admin] Approving driver:', { driverId, status, rejectionReason });
    Alert.alert(
      status === 'approved' ? 'Approve Driver' : 'Reject Driver',
      status === 'approved' 
        ? 'Are you sure you want to approve this driver?' 
        : `Reject reason: ${rejectionReason || 'Not specified'}`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: status === 'approved' ? 'Approve' : 'Reject',
          style: status === 'rejected' ? 'destructive' : 'default',
          onPress: async () => {
            try {
              console.log('[Admin] Calling approveDriver API for:', driverId);
              setLoading(true);
              const response = await approveDriver(driverId, status, rejectionReason);
              console.log('[Admin] Approve response:', response.data);
              setLoading(false);
              
              // Close modal first
              setSelectedDriver(null);
              
              // Show success message
              Alert.alert(
                'Success!', 
                `Driver ${status === 'approved' ? 'approved' : 'rejected'} successfully!`,
                [{ text: 'OK', onPress: () => {
                  // Refresh data after alert is dismissed
                  fetchDrivers();
                  fetchStats();
                }}]
              );
            } catch (error: any) {
              setLoading(false);
              console.error('[Admin] Approve error:', error);
              const errorMessage = error.response?.data?.detail || error.message || 'Failed to update driver status';
              Alert.alert('Error', errorMessage);
              // Don't close modal on error so user can try again
            }
          }
        }
      ]
    );
  };

  // Add Wallet Balance Handler
  const handleAddWalletBalance = async () => {
    if (!walletAmount || parseInt(walletAmount) <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }
    try {
      const response = await addWalletMoney(walletDriverId, parseInt(walletAmount));
      console.log('Wallet response:', response.data);
      Alert.alert('Success', `₹${walletAmount} added to ${walletDriverName}'s wallet!`);
      setShowWalletModal(false);
      setWalletAmount('');
      fetchDrivers();
    } catch (error: any) {
      console.error('Wallet error:', error.response?.data || error.message);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to add wallet balance');
    }
  };

  const openWalletModal = (driverId: string, driverName: string) => {
    setWalletDriverId(driverId);
    setWalletDriverName(driverName);
    setWalletAmount('');
    setShowWalletModal(true);
  };

  // Reset Driver Status Handler
  const handleResetDriver = async (driverId: string) => {
    Alert.alert(
      'Reset Driver',
      'This will change driver status from APPROVED back to PENDING. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          onPress: async () => {
            try {
              await resetDriverStatus(driverId);
              Alert.alert('Success', 'Driver status reset to PENDING');
              setSelectedDriver(null);
              fetchDrivers();
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to reset driver');
            }
          }
        }
      ]
    );
  };

  // Delete Driver Handler
  const handleDeleteDriver = async (driverId: string) => {
    Alert.alert(
      'Delete Driver',
      'This will permanently delete the driver. This action cannot be undone. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteDriver(driverId);
              Alert.alert('Success', 'Driver deleted successfully');
              setSelectedDriver(null);
              fetchDrivers();
              fetchStats();
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to delete driver');
            }
          }
        }
      ]
    );
  };

  const handleManualAssignment = async () => {
    if (!pickupAddress || !dropAddress || !customerId) {
      Alert.alert('Error', 'Please fill all required fields');
      return;
    }

    if (assignmentMode === 'manual' && !manualDriverId) {
      Alert.alert('Error', 'Please select a driver for manual assignment');
      return;
    }

    setLoading(true);
    try {
      const response = await createSmartBooking({
        customer_id: customerId,
        pickup: {
          latitude: 12.97,
          longitude: 80.24,
          address: pickupAddress,
        },
        drop: {
          latitude: 13.08,
          longitude: 80.27,
          address: dropAddress,
        },
        vehicle_type: vehicleType,
        assignment_mode: assignmentMode,
        manual_driver_id: assignmentMode === 'manual' ? manualDriverId : undefined,
      });

      if (response.data.success) {
        Alert.alert(
          'Booking Created!',
          `ID: ${response.data.booking.booking_id.slice(0, 8)}\nDriver: ${response.data.booking.driver_name || 'Assigned'}\nFare: ₹${response.data.booking.fare}`
        );
        setShowAssignModal(false);
        setPickupAddress('');
        setDropAddress('');
        setCustomerId('');
        fetchBookings();
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  const getAvailableDrivers = () => {
    return drivers.filter(
      (d) =>
        d.approval_status === 'approved' &&
        d.duty_on &&
        d.is_online &&
        (d.driver_status === 'available' || d.driver_status === 'waiting')
    );
  };

  // Fetch full driver details when selecting a driver
  const handleSelectDriver = async (driver: any) => {
    console.log('[Admin] Selected driver from list:', JSON.stringify({
      driver_id: driver.driver_id,
      full_name: driver.full_name,
      phone: driver.phone,
      address: driver.address,
      vehicle_number: driver.vehicle_number,
    }));
    
    setSelectedDriver(driver); // Show basic info immediately
    setFullDriverDetails(null);
    setLoadingDriverDetails(true);
    
    try {
      const response = await getDriverFullDetails(driver.driver_id);
      console.log('[Admin] Full details API response success:', response.data.success);
      if (response.data.success) {
        console.log('[Admin] Full driver details loaded:', JSON.stringify({
          driver_id: response.data.driver.driver_id,
          full_name: response.data.driver.full_name,
          phone: response.data.driver.phone,
          has_driver_photo: !!response.data.driver.driver_photo,
        }));
        setFullDriverDetails(response.data.driver);
      }
    } catch (error) {
      console.error('[Admin] Failed to fetch full driver details:', error);
      // Keep showing basic driver info even if full fetch fails
    } finally {
      setLoadingDriverDetails(false);
    }
  };

  // Helper to get driver name
  const getDriverName = (driver: any) => {
    return driver?.full_name || driver?.personal_details?.full_name || driver?.name || 'Unknown';
  };

  const renderStats = () => (
    <View style={styles.statsContainer}>
      <View style={styles.statRow}>
        <View style={[styles.statCard, { backgroundColor: '#e8f5e9' }]}>
          <Ionicons name="people" size={28} color="#2e7d32" />
          <Text style={styles.statValue}>{stats?.total_customers || 0}</Text>
          <Text style={styles.statLabel}>Customers</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: '#fff3e0' }]}>
          <Ionicons name="car" size={28} color="#ef6c00" />
          <Text style={styles.statValue}>{stats?.total_drivers || 0}</Text>
          <Text style={styles.statLabel}>Drivers</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: '#ffebee' }]}>
          <Ionicons name="hourglass" size={28} color="#c62828" />
          <Text style={styles.statValue}>{stats?.pending_drivers || 0}</Text>
          <Text style={styles.statLabel}>Pending</Text>
        </View>
      </View>

      <View style={styles.statRow}>
        <View style={[styles.statCard, { backgroundColor: '#e3f2fd' }]}>
          <Ionicons name="receipt" size={28} color="#1565c0" />
          <Text style={styles.statValue}>{stats?.total_bookings || 0}</Text>
          <Text style={styles.statLabel}>Bookings</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: '#f3e5f5' }]}>
          <Ionicons name="checkmark-circle" size={28} color="#7b1fa2" />
          <Text style={styles.statValue}>{stats?.completed_bookings || 0}</Text>
          <Text style={styles.statLabel}>Completed</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: '#e8f5e9' }]}>
          <Ionicons name="cash" size={28} color="#2e7d32" />
          <Text style={styles.statValue}>₹{stats?.total_revenue || 0}</Text>
          <Text style={styles.statLabel}>Revenue</Text>
        </View>
      </View>

      {/* Tariffs */}
      <View style={styles.tariffsCard}>
        <Text style={styles.sectionTitle}>Current Tariffs</Text>
        {tariffs.map((tariff) => (
          <View key={tariff.vehicle_type} style={styles.tariffRow}>
            <Text style={styles.tariffType}>{tariff.vehicle_type.toUpperCase()}</Text>
            <Text style={styles.tariffRate}>₹{tariff.rate_per_km}/km</Text>
            <Text style={styles.tariffMin}>Min: ₹{tariff.minimum_fare}</Text>
          </View>
        ))}
      </View>
    </View>
  );

  const renderDrivers = () => (
    <ScrollView style={styles.listContainer}>
      {/* Available Drivers Section */}
      <Text style={styles.sectionTitle}>Available Drivers ({getAvailableDrivers().length})</Text>
      {getAvailableDrivers().map((driver) => (
        <View key={driver.driver_id} style={[styles.listItem, styles.availableDriver]}>
          <View style={styles.listItemHeader}>
            <View>
              <Text style={styles.listItemTitle}>
                {getDriverName(driver)}
              </Text>
              <Text style={styles.listItemSubtitle}>{driver.phone}</Text>
            </View>
            <View style={[styles.statusBadge, { backgroundColor: Colors.success }]}>
              <Text style={styles.statusText}>ONLINE</Text>
            </View>
          </View>
          <Text style={styles.listItemDetails}>
            {(driver.vehicle_type || '').toUpperCase()} • {driver.vehicle_number || 'N/A'}
          </Text>
        </View>
      ))}

      {/* All Drivers */}
      <Text style={[styles.sectionTitle, { marginTop: 24 }]}>All Drivers ({drivers.length})</Text>
      {drivers.map((driver) => (
        <TouchableOpacity
          key={driver.driver_id}
          style={styles.listItem}
          onPress={() => handleSelectDriver(driver)}
        >
          <View style={styles.listItemHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.listItemTitle}>
                {getDriverName(driver)}
              </Text>
              <Text style={styles.listItemSubtitle}>{driver.phone}</Text>
              <Text style={styles.driverIdText}>ID: {driver.driver_id}</Text>
            </View>
            <View
              style={[
                styles.statusBadge,
                {
                  backgroundColor:
                    driver.approval_status === 'approved'
                      ? Colors.success
                      : driver.approval_status === 'rejected'
                      ? Colors.error
                      : Colors.warning,
                },
              ]}
            >
              <Text style={styles.statusText}>{driver.approval_status?.toUpperCase()}</Text>
            </View>
          </View>
          <Text style={styles.listItemDetails}>
            {(driver.vehicle_type || '').toUpperCase()} • {driver.vehicle_number || 'N/A'}
          </Text>
          {driver.address && (
            <Text style={styles.addressText} numberOfLines={1}>
              {driver.address}
            </Text>
          )}
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  const renderBookings = () => (
    <ScrollView style={styles.listContainer}>
      {loading && bookings.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Loading bookings...</Text>
        </View>
      ) : bookings.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="receipt-outline" size={48} color={Colors.gray} />
          <Text style={styles.emptyText}>No bookings yet</Text>
          <Text style={styles.emptySubtext}>Bookings will appear here when customers make reservations</Text>
        </View>
      ) : (
        bookings.map((booking) => (
          <View key={booking.booking_id || booking._id} style={styles.listItem}>
            <View style={styles.listItemHeader}>
              <Text style={styles.listItemTitle}>#{(booking.booking_id || booking._id || '').slice(0, 12)}</Text>
              <View
                style={[
                  styles.statusBadge,
                  {
                    backgroundColor:
                      booking.status === 'completed'
                        ? Colors.success
                        : booking.status === 'cancelled'
                        ? Colors.error
                        : booking.status === 'ongoing'
                        ? Colors.warning
                        : Colors.primary,
                  },
                ]}
              >
                <Text style={styles.statusText}>{(booking.status || 'pending').toUpperCase()}</Text>
              </View>
            </View>
            <Text style={styles.listItemSubtitle} numberOfLines={1}>
              From: {booking.pickup?.address || 'N/A'}
            </Text>
            <Text style={styles.listItemSubtitle} numberOfLines={1}>
              To: {booking.drop?.address || 'N/A'}
            </Text>
            <View style={styles.bookingFooter}>
              <Text style={styles.listItemDetails}>
                {booking.distance || 0} km • {(booking.vehicle_type || 'sedan').toUpperCase()}
              </Text>
              <Text style={styles.fareText}>₹{booking.fare || 0}</Text>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );

  const renderDispatch = () => (
    <View style={styles.dispatchContainer}>
      <View style={styles.assignmentModeCard}>
        <Text style={styles.sectionTitle}>Assignment Mode</Text>
        <View style={styles.modeToggle}>
          <TouchableOpacity
            style={[styles.modeBtn, assignmentMode === 'auto' && styles.modeBtnActive]}
            onPress={() => setAssignmentMode('auto')}
          >
            <Ionicons
              name="flash"
              size={20}
              color={assignmentMode === 'auto' ? Colors.white : Colors.text}
            />
            <Text style={[styles.modeText, assignmentMode === 'auto' && styles.modeTextActive]}>
              Auto Assign
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.modeBtn, assignmentMode === 'manual' && styles.modeBtnActive]}
            onPress={() => setAssignmentMode('manual')}
          >
            <Ionicons
              name="hand-left"
              size={20}
              color={assignmentMode === 'manual' ? Colors.white : Colors.text}
            />
            <Text style={[styles.modeText, assignmentMode === 'manual' && styles.modeTextActive]}>
              Manual Assign
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <Button
        title="Create New Booking"
        onPress={() => setShowAssignModal(true)}
        variant="primary"
        style={styles.createBookingBtn}
      />

      {/* Available Drivers for Assignment */}
      <Text style={styles.sectionTitle}>Available for Assignment</Text>
      <ScrollView style={styles.driverList}>
        {getAvailableDrivers().length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="car-outline" size={48} color={Colors.gray} />
            <Text style={styles.emptyText}>No drivers available</Text>
          </View>
        ) : (
          getAvailableDrivers().map((driver) => (
            <View key={driver.driver_id} style={styles.dispatchDriverCard}>
              <View style={styles.driverCardLeft}>
                <View style={[styles.onlineIndicator, { backgroundColor: Colors.success }]} />
                <View>
                  <Text style={styles.driverName}>
                    {getDriverName(driver)}
                  </Text>
                  <Text style={styles.driverVehicle}>
                    {(driver.vehicle_type || '').toUpperCase()} • {driver.vehicle_number || 'N/A'}
                  </Text>
                </View>
              </View>
              <View style={styles.driverCardRight}>
                <Text style={styles.driverStatus}>{driver.driver_status || 'Available'}</Text>
                <Text style={styles.driverTrips}>
                  Trips: {driver.continuous_trips_count || 0}/2
                </Text>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>VK Drop Taxi</Text>
        <Text style={styles.headerSubtitle}>Admin Dashboard</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabs}>
        {[
          { key: 'stats', label: 'Stats', icon: 'stats-chart' },
          { key: 'drivers', label: 'Drivers', icon: 'car' },
          { key: 'bookings', label: 'Bookings', icon: 'receipt' },
          { key: 'dispatch', label: 'Dispatch', icon: 'navigate' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[styles.tab, activeTab === tab.key && styles.activeTab]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Ionicons
              name={tab.icon as any}
              size={20}
              color={activeTab === tab.key ? Colors.primary : Colors.gray}
            />
            <Text style={[styles.tabText, activeTab === tab.key && styles.activeTabText]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {activeTab === 'stats' && renderStats()}
        {activeTab === 'drivers' && renderDrivers()}
        {activeTab === 'bookings' && renderBookings()}
        {activeTab === 'dispatch' && renderDispatch()}
      </ScrollView>

      {/* Verify Button */}
      <TouchableOpacity
        style={styles.verifyFab}
        onPress={() => router.push('/admin/driver-verification')}
      >
        <Ionicons name="shield-checkmark" size={24} color={Colors.white} />
      </TouchableOpacity>

      {/* Manual Assignment Modal */}
      <Modal
        visible={showAssignModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowAssignModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Create Booking</Text>
              <TouchableOpacity onPress={() => setShowAssignModal(false)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            <ScrollView>
              <Text style={styles.inputLabel}>Customer</Text>
              <View style={styles.pickerContainer}>
                <Picker
                  selectedValue={customerId}
                  onValueChange={(value) => setCustomerId(value)}
                >
                  <Picker.Item label="Select Customer" value="" />
                  {customers.map((c) => (
                    <Picker.Item
                      key={c.user_id}
                      label={`${c.name} (${c.phone})`}
                      value={c.user_id}
                    />
                  ))}
                </Picker>
              </View>

              <Input
                label="Pickup Address"
                value={pickupAddress}
                onChangeText={setPickupAddress}
                placeholder="Enter pickup location"
              />

              <Input
                label="Drop Address"
                value={dropAddress}
                onChangeText={setDropAddress}
                placeholder="Enter drop location"
              />

              <Text style={styles.inputLabel}>Vehicle Type</Text>
              <View style={styles.vehicleRow}>
                <TouchableOpacity
                  style={[styles.vehicleBtn, vehicleType === 'sedan' && styles.vehicleBtnActive]}
                  onPress={() => setVehicleType('sedan')}
                >
                  <Text
                    style={[
                      styles.vehicleBtnText,
                      vehicleType === 'sedan' && styles.vehicleBtnTextActive,
                    ]}
                  >
                    Sedan
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.vehicleBtn, vehicleType === 'suv' && styles.vehicleBtnActive]}
                  onPress={() => setVehicleType('suv')}
                >
                  <Text
                    style={[
                      styles.vehicleBtnText,
                      vehicleType === 'suv' && styles.vehicleBtnTextActive,
                    ]}
                  >
                    SUV
                  </Text>
                </TouchableOpacity>
              </View>

              <Text style={styles.inputLabel}>Assignment Mode</Text>
              <View style={styles.modeToggle}>
                <TouchableOpacity
                  style={[styles.modeBtn, assignmentMode === 'auto' && styles.modeBtnActive]}
                  onPress={() => setAssignmentMode('auto')}
                >
                  <Text
                    style={[styles.modeText, assignmentMode === 'auto' && styles.modeTextActive]}
                  >
                    Auto
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modeBtn, assignmentMode === 'manual' && styles.modeBtnActive]}
                  onPress={() => setAssignmentMode('manual')}
                >
                  <Text
                    style={[styles.modeText, assignmentMode === 'manual' && styles.modeTextActive]}
                  >
                    Manual
                  </Text>
                </TouchableOpacity>
              </View>

              {assignmentMode === 'manual' && (
                <>
                  <Text style={styles.inputLabel}>Select Driver</Text>
                  <View style={styles.pickerContainer}>
                    <Picker
                      selectedValue={manualDriverId}
                      onValueChange={(value) => setManualDriverId(value)}
                    >
                      <Picker.Item label="Select Driver" value="" />
                      {getAvailableDrivers().map((d) => (
                        <Picker.Item
                          key={d.driver_id}
                          label={`${getDriverName(d)} (${d.vehicle_number || 'N/A'})`}
                          value={d.driver_id}
                        />
                      ))}
                    </Picker>
                  </View>
                </>
              )}

              <Button
                title="Create Booking"
                onPress={handleManualAssignment}
                variant="primary"
                loading={loading}
                style={{ marginTop: 16 }}
              />
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Driver Details Modal */}
      <Modal
        visible={!!selectedDriver}
        animationType="slide"
        transparent={true}
        onRequestClose={() => {
          setSelectedDriver(null);
          setFullDriverDetails(null);
        }}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxHeight: '90%' }]}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Driver Details</Text>
              <TouchableOpacity onPress={() => {
                setSelectedDriver(null);
                setFullDriverDetails(null);
              }}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            {selectedDriver && (
              <ScrollView showsVerticalScrollIndicator={false}>
                {/* Use full details if available, otherwise fall back to basic */}
                {(() => {
                  const driver = fullDriverDetails || selectedDriver;
                  const driverName = getDriverName(driver);
                  
                  // Debug log
                  console.log('[Admin Modal] Rendering driver:', {
                    driver_id: driver?.driver_id,
                    full_name: driver?.full_name,
                    phone: driver?.phone,
                    address: driver?.address,
                    isFullDetails: !!fullDriverDetails,
                  });
                  
                  return (
                    <>
                      {/* Basic Info */}
                      <View style={styles.detailSection}>
                        <Text style={styles.detailSectionTitle}>Basic Information</Text>
                        
                        {/* Driver Photo */}
                        {loadingDriverDetails ? (
                          <View style={styles.photoPlaceholder}>
                            <Text style={styles.photoPlaceholderText}>Loading photo...</Text>
                          </View>
                        ) : (driver?.driver_photos?.driver_photo || driver?.driver_photo) ? (
                          <View style={styles.driverPhotoContainer}>
                            <Image 
                              source={{ uri: driver?.driver_photos?.driver_photo || driver?.driver_photo }}
                              style={styles.driverPhoto}
                              resizeMode="cover"
                            />
                          </View>
                        ) : (
                          <View style={styles.photoPlaceholder}>
                            <Ionicons name="person-circle" size={80} color={Colors.gray} />
                          </View>
                        )}
                        
                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Driver ID</Text>
                          <Text style={styles.infoValue}>{driver?.driver_id || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Name</Text>
                          <Text style={styles.infoValue}>{driverName || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Phone</Text>
                          <Text style={styles.infoValue}>{driver?.phone || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Address</Text>
                          <Text style={styles.infoValue}>{driver?.address || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Aadhaar Number</Text>
                          <Text style={styles.infoValue}>{driver?.aadhaar_number || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>PAN Number</Text>
                          <Text style={styles.infoValue}>{driver?.pan_number || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Driving License</Text>
                          <Text style={styles.infoValue}>{driver?.driving_license_number || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Experience</Text>
                          <Text style={styles.infoValue}>{driver?.driving_experience_years || 0} years</Text>
                        </View>
                      </View>

                      {/* Vehicle Info */}
                      <View style={styles.detailSection}>
                        <Text style={styles.detailSectionTitle}>Vehicle Details</Text>
                        
                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Vehicle Type</Text>
                          <Text style={styles.infoValue}>{(driver?.vehicle_type || 'N/A').toUpperCase()}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Vehicle Number</Text>
                          <Text style={styles.infoValue}>{driver?.vehicle_number || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Vehicle Model</Text>
                          <Text style={styles.infoValue}>{driver?.vehicle_model || 'N/A'}</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Vehicle Year</Text>
                          <Text style={styles.infoValue}>{driver?.vehicle_year || 'N/A'}</Text>
                        </View>
                      </View>

                      {/* Documents Section */}
                      <View style={styles.detailSection}>
                        <Text style={styles.detailSectionTitle}>Documents</Text>
                        
                        {loadingDriverDetails ? (
                          <View style={styles.documentLoading}>
                            <ActivityIndicator size="small" color={Colors.secondary} />
                            <Text style={styles.documentLoadingText}>Loading documents...</Text>
                          </View>
                        ) : (
                          <>
                            {/* Driver with Vehicle Photo */}
                            {driver?.driver_with_vehicle_photo && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Driver with Vehicle</Text>
                                <Image 
                                  source={{ uri: driver.driver_with_vehicle_photo }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {/* Aadhaar */}
                            {driver?.aadhaar_front && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Aadhaar Front</Text>
                                <Image 
                                  source={{ uri: driver.aadhaar_front }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.aadhaar_back && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Aadhaar Back</Text>
                                <Image 
                                  source={{ uri: driver.aadhaar_back }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {/* License */}
                            {driver?.license_front && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>License Front</Text>
                                <Image 
                                  source={{ uri: driver.license_front }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.license_back && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>License Back</Text>
                                <Image 
                                  source={{ uri: driver.license_back }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {/* Vehicle Documents */}
                            {driver?.rc_front && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>RC Book Front</Text>
                                <Image 
                                  source={{ uri: driver.rc_front }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.rc_back && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>RC Book Back</Text>
                                <Image 
                                  source={{ uri: driver.rc_back }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.insurance && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Insurance</Text>
                                <Image 
                                  source={{ uri: driver.insurance }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.permit && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Permit</Text>
                                <Image 
                                  source={{ uri: driver.permit }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.pollution_certificate && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Pollution Certificate</Text>
                                <Image 
                                  source={{ uri: driver.pollution_certificate }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {/* Vehicle Photos */}
                            {driver?.vehicle_front_photo && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Vehicle Front</Text>
                                <Image 
                                  source={{ uri: driver.vehicle_front_photo }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.vehicle_back_photo && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Vehicle Back</Text>
                                <Image 
                                  source={{ uri: driver.vehicle_back_photo }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.vehicle_left_photo && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Vehicle Left</Text>
                                <Image 
                                  source={{ uri: driver.vehicle_left_photo }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {driver?.vehicle_right_photo && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Vehicle Right</Text>
                                <Image 
                                  source={{ uri: driver.vehicle_right_photo }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {/* Payment Screenshot */}
                            {driver?.payment_screenshot && (
                              <View style={styles.documentItem}>
                                <Text style={styles.documentLabel}>Payment Screenshot (₹{driver?.payment_amount || 500})</Text>
                                <Image 
                                  source={{ uri: driver.payment_screenshot }}
                                  style={styles.documentImage}
                                  resizeMode="contain"
                                />
                              </View>
                            )}

                            {!fullDriverDetails && !loadingDriverDetails && (
                              <Text style={styles.noDocumentsText}>
                                Tap to load full document details
                              </Text>
                            )}
                          </>
                        )}
                      </View>

                      {/* Status */}
                      <View style={styles.detailSection}>
                        <Text style={styles.detailSectionTitle}>Status</Text>
                        
                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Approval Status</Text>
                          <View style={[
                            styles.statusPill,
                            { 
                              backgroundColor: 
                                driver?.approval_status === 'approved' ? '#e8f5e9' :
                                driver?.approval_status === 'rejected' ? '#ffebee' : '#fff3e0'
                            }
                          ]}>
                            <Text style={[
                              styles.statusPillText,
                              {
                                color:
                                  driver?.approval_status === 'approved' ? '#2e7d32' :
                                  driver?.approval_status === 'rejected' ? '#c62828' : '#ef6c00'
                              }
                            ]}>
                              {(driver?.approval_status || 'pending').toUpperCase()}
                            </Text>
                          </View>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Online Status</Text>
                          <Text style={[
                            styles.infoValue, 
                            { color: driver?.is_online ? '#2e7d32' : '#c62828' }
                          ]}>
                            {driver?.is_online ? 'ONLINE' : 'OFFLINE'}
                          </Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Rating</Text>
                          <Text style={styles.infoValue}>{driver?.rating || 5.0} ⭐</Text>
                        </View>

                        <View style={styles.driverInfo}>
                          <Text style={styles.infoLabel}>Total Trips</Text>
                          <Text style={styles.infoValue}>{driver?.total_trips || 0}</Text>
                        </View>

                        {driver?.rejection_reason && (
                          <View style={styles.driverInfo}>
                            <Text style={styles.infoLabel}>Rejection Reason</Text>
                            <Text style={[styles.infoValue, { color: Colors.error }]}>
                              {driver.rejection_reason}
                            </Text>
                          </View>
                        )}

                        {driver?.approval_remarks && (
                          <View style={styles.driverInfo}>
                            <Text style={styles.infoLabel}>Remarks</Text>
                            <Text style={styles.infoValue}>{driver.approval_remarks}</Text>
                          </View>
                        )}
                      </View>

                      {/* Action Buttons for PENDING Drivers */}
                      {driver?.approval_status === 'pending' && (
                        <>
                          <View style={styles.actionButtons}>
                            <TouchableOpacity
                              style={[styles.actionBtn, styles.approveBtn]}
                              onPress={() => {
                                console.log('[Admin] Approve button pressed for:', driver?.driver_id);
                                handleApproveDriver(driver?.driver_id, 'approved');
                              }}
                            >
                              <Ionicons name="checkmark-circle" size={24} color="#fff" />
                              <Text style={styles.actionBtnText}>APPROVE</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                              style={[styles.actionBtn, styles.rejectBtn]}
                              onPress={() => {
                                console.log('[Admin] Reject button pressed for:', driver?.driver_id);
                                handleApproveDriver(driver?.driver_id, 'rejected', 'Documents not verified');
                              }}
                            >
                              <Ionicons name="close-circle" size={24} color="#fff" />
                              <Text style={styles.actionBtnText}>REJECT</Text>
                            </TouchableOpacity>
                          </View>
                          {/* Delete PENDING Driver */}
                          <TouchableOpacity
                            style={[styles.actionBtn, { backgroundColor: '#B71C1C', marginTop: 12 }]}
                            onPress={() => {
                              console.log('[Admin] Delete PENDING button pressed for:', driver?.driver_id);
                              handleDeleteDriver(driver?.driver_id);
                            }}
                          >
                            <Ionicons name="trash" size={24} color="#fff" />
                            <Text style={styles.actionBtnText}>DELETE PENDING DRIVER</Text>
                          </TouchableOpacity>
                        </>
                      )}

                      {/* Add Balance Button for Approved Drivers */}
                      {driver?.approval_status === 'approved' && (
                        <>
                          <TouchableOpacity
                            style={[styles.actionBtn, { backgroundColor: Colors.secondary, marginTop: 16 }]}
                            onPress={() => {
                              console.log('[Admin] Add Wallet button pressed for:', driver?.driver_id);
                              setSelectedDriver(null);
                              setFullDriverDetails(null);
                              openWalletModal(driver?.driver_id, driverName);
                            }}
                          >
                            <Ionicons name="wallet" size={24} color="#fff" />
                            <Text style={styles.actionBtnText}>ADD WALLET BALANCE</Text>
                          </TouchableOpacity>

                          {/* Reset Status Button */}
                          <TouchableOpacity
                            style={[styles.actionBtn, { backgroundColor: '#FF9800', marginTop: 12 }]}
                            onPress={() => {
                              console.log('[Admin] Reset button pressed for:', driver?.driver_id);
                              handleResetDriver(driver?.driver_id);
                            }}
                          >
                            <Ionicons name="refresh" size={24} color="#fff" />
                            <Text style={styles.actionBtnText}>RESET TO PENDING</Text>
                          </TouchableOpacity>
                        </>
                      )}

                      {/* Reject Approved Driver */}
                      {driver?.approval_status === 'approved' && (
                        <TouchableOpacity
                          style={[styles.actionBtn, styles.rejectBtn, { marginTop: 12 }]}
                          onPress={() => {
                            console.log('[Admin] Revoke approval button pressed for:', driver?.driver_id);
                            handleApproveDriver(driver?.driver_id, 'rejected', 'Approval revoked by admin');
                          }}
                        >
                          <Ionicons name="close-circle" size={24} color="#fff" />
                          <Text style={styles.actionBtnText}>REVOKE APPROVAL</Text>
                        </TouchableOpacity>
                      )}

                      {/* Delete Driver Button - Always visible */}
                      <TouchableOpacity
                        style={[styles.actionBtn, { backgroundColor: '#B71C1C', marginTop: 12 }]}
                        onPress={() => {
                          console.log('[Admin] Delete button pressed for:', driver?.driver_id);
                          handleDeleteDriver(driver?.driver_id);
                        }}
                      >
                        <Ionicons name="trash" size={24} color="#fff" />
                        <Text style={styles.actionBtnText}>DELETE DRIVER</Text>
                      </TouchableOpacity>

                      <View style={{ height: 20 }} />
                    </>
                  );
                })()}
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>

      {/* Wallet Add Balance Modal */}
      <Modal
        visible={showWalletModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowWalletModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxHeight: 400 }]}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add Wallet Balance</Text>
              <TouchableOpacity onPress={() => setShowWalletModal(false)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            <View style={{ padding: 16 }}>
              <Text style={{ fontSize: 16, color: Colors.textLight, marginBottom: 8 }}>
                Driver: <Text style={{ fontWeight: 'bold', color: Colors.text }}>{walletDriverName}</Text>
              </Text>

              <Text style={{ fontSize: 14, fontWeight: '600', color: Colors.text, marginTop: 16, marginBottom: 8 }}>
                Enter Amount (₹)
              </Text>
              <Input
                value={walletAmount}
                onChangeText={setWalletAmount}
                placeholder="Enter amount"
                keyboardType="numeric"
              />

              <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
                {[500, 1000, 2000, 5000].map((amt) => (
                  <TouchableOpacity
                    key={amt}
                    style={{
                      flex: 1,
                      paddingVertical: 10,
                      borderRadius: 8,
                      backgroundColor: walletAmount === String(amt) ? Colors.secondary : '#f0f0f0',
                      alignItems: 'center',
                    }}
                    onPress={() => setWalletAmount(String(amt))}
                  >
                    <Text style={{ fontWeight: '600', color: walletAmount === String(amt) ? '#fff' : Colors.text }}>
                      ₹{amt}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Button
                title={`Add ₹${walletAmount || '0'} to Wallet`}
                onPress={handleAddWalletBalance}
                variant="secondary"
                style={{ marginTop: 24 }}
              />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: Colors.primary,
    padding: 20,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
  },
  headerSubtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 4,
  },
  tabs: {
    flexDirection: 'row',
    backgroundColor: Colors.white,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    gap: 4,
  },
  activeTab: {
    borderBottomWidth: 3,
    borderBottomColor: Colors.primary,
  },
  tabText: {
    fontSize: 11,
    color: Colors.gray,
    fontWeight: '600',
  },
  activeTabText: {
    color: Colors.primary,
  },
  content: {
    flex: 1,
  },
  statsContainer: {
    padding: 16,
  },
  statRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  statLabel: {
    fontSize: 11,
    color: Colors.textLight,
    marginTop: 4,
  },
  tariffsCard: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 12,
  },
  tariffRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  tariffType: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  tariffRate: {
    fontSize: 14,
    color: Colors.secondary,
    fontWeight: 'bold',
  },
  tariffMin: {
    fontSize: 12,
    color: Colors.textLight,
  },
  listContainer: {
    padding: 16,
  },
  listItem: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  availableDriver: {
    borderLeftWidth: 4,
    borderLeftColor: Colors.success,
  },
  listItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  listItemTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: Colors.text,
  },
  listItemSubtitle: {
    fontSize: 13,
    color: Colors.textLight,
    marginTop: 2,
  },
  listItemDetails: {
    fontSize: 12,
    color: Colors.gray,
    marginTop: 4,
  },
  driverIdText: {
    fontSize: 11,
    color: Colors.secondary,
    marginTop: 2,
    fontWeight: '500',
  },
  addressText: {
    fontSize: 11,
    color: Colors.textLight,
    marginTop: 4,
    fontStyle: 'italic',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 10,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: Colors.white,
  },
  bookingFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  fareText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  dispatchContainer: {
    padding: 16,
  },
  assignmentModeCard: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  modeToggle: {
    flexDirection: 'row',
    gap: 12,
  },
  modeBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 8,
  },
  modeBtnActive: {
    backgroundColor: Colors.secondary,
    borderColor: Colors.secondary,
  },
  modeText: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  modeTextActive: {
    color: Colors.white,
  },
  createBookingBtn: {
    marginBottom: 16,
  },
  driverList: {
    maxHeight: 400,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    marginTop: 12,
    fontSize: 14,
    color: Colors.gray,
  },
  dispatchDriverCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.white,
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
  },
  driverCardLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  onlineIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  driverName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.text,
  },
  driverVehicle: {
    fontSize: 12,
    color: Colors.textLight,
    marginTop: 2,
  },
  driverCardRight: {
    alignItems: 'flex-end',
  },
  driverStatus: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.secondary,
  },
  driverTrips: {
    fontSize: 11,
    color: Colors.textLight,
    marginTop: 2,
  },
  verifyFab: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: Colors.secondary,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1A1A1A', // Dark text for white background
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A', // Dark text for white background
    marginBottom: 8,
    marginTop: 12,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 10,
    backgroundColor: Colors.white,
    marginBottom: 8,
  },
  vehicleRow: {
    flexDirection: 'row',
    gap: 12,
  },
  vehicleBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
  },
  vehicleBtnActive: {
    backgroundColor: Colors.secondary,
    borderColor: Colors.secondary,
  },
  vehicleBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
  },
  vehicleBtnTextActive: {
    color: Colors.white,
  },
  driverInfo: {
    marginBottom: 14,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666666', // Gray text for labels on white background
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 15,
    color: '#1A1A1A', // Dark text for values on white background
    fontWeight: '600',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 20,
  },
  approveButton: {
    flex: 1,
  },
  rejectButton: {
    flex: 1,
  },
  // New styles for document display
  detailSection: {
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  detailSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32', // Green - kept as accent color
    marginBottom: 12,
  },
  documentItem: {
    marginBottom: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 12,
  },
  documentLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A', // Dark text for white background
    marginBottom: 8,
  },
  documentImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    backgroundColor: '#e0e0e0',
  },
  documentNumber: {
    fontSize: 12,
    color: '#666666', // Gray text for white background
    marginTop: 8,
    textAlign: 'center',
  },
  documentLoading: {
    padding: 20,
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  documentLoadingText: {
    fontSize: 14,
    color: '#666666', // Gray text for white background
    marginTop: 8,
  },
  noDocumentsText: {
    fontSize: 14,
    color: '#666666', // Gray text for white background
    textAlign: 'center',
    padding: 20,
    fontStyle: 'italic',
  },
  driverPhotoContainer: {
    alignItems: 'center',
    marginBottom: 16,
  },
  driverPhoto: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    borderColor: '#2E7D32', // Green border
  },
  photoPlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
    marginBottom: 16,
  },
  photoPlaceholderText: {
    fontSize: 12,
    color: '#666666', // Gray text for white background
    textAlign: 'center',
  },
  statusPill: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusPillText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  actionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 10,
    gap: 8,
  },
  approveBtn: {
    backgroundColor: '#2e7d32',
  },
  rejectBtn: {
    backgroundColor: '#c62828',
  },
  actionBtnText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
  },
  emptySubtext: {
    fontSize: 12,
    color: Colors.gray,
    textAlign: 'center',
    marginTop: 8,
    paddingHorizontal: 20,
  },
});
