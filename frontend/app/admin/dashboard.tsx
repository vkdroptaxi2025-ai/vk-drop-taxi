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
} from 'react-native';
import { Colors } from '../../utils/colors';
import {
  getAllDrivers,
  approveDriver,
  getAllCustomers,
  getAllBookings,
  getAdminStats,
} from '../../utils/api';
import { Button } from '../../components/Button';
import { Ionicons } from '@expo/vector-icons';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<'stats' | 'drivers' | 'customers' | 'bookings'>('stats');
  const [stats, setStats] = useState<any>(null);
  const [drivers, setDrivers] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    if (activeTab === 'drivers') fetchDrivers();
    else if (activeTab === 'customers') fetchCustomers();
    else if (activeTab === 'bookings') fetchBookings();
  }, [activeTab]);

  const fetchStats = async () => {
    try {
      const response = await getAdminStats();
      setStats(response.data.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchDrivers = async () => {
    setLoading(true);
    try {
      const response = await getAllDrivers();
      setDrivers(response.data.drivers);
    } catch (error) {
      console.error('Failed to fetch drivers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await getAllCustomers();
      setCustomers(response.data.customers);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await getAllBookings();
      setBookings(response.data.bookings);
    } catch (error) {
      console.error('Failed to fetch bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveDriver = async (driverId: string, status: 'approved' | 'rejected') => {
    try {
      await approveDriver(driverId, status);
      Alert.alert('Success', `Driver ${status}`);
      setSelectedDriver(null);
      fetchDrivers();
      fetchStats();
    } catch (error) {
      Alert.alert('Error', 'Failed to update driver status');
    }
  };

  const renderStats = () => (
    <View style={styles.statsContainer}>
      <View style={styles.statCard}>
        <Ionicons name="people" size={32} color={Colors.primary} />
        <Text style={styles.statValue}>{stats?.total_customers || 0}</Text>
        <Text style={styles.statLabel}>Total Customers</Text>
      </View>

      <View style={styles.statCard}>
        <Ionicons name="car" size={32} color={Colors.secondary} />
        <Text style={styles.statValue}>{stats?.total_drivers || 0}</Text>
        <Text style={styles.statLabel}>Total Drivers</Text>
      </View>

      <View style={styles.statCard}>
        <Ionicons name="hourglass" size={32} color={Colors.warning} />
        <Text style={styles.statValue}>{stats?.pending_drivers || 0}</Text>
        <Text style={styles.statLabel}>Pending Approvals</Text>
      </View>

      <View style={styles.statCard}>
        <Ionicons name="receipt" size={32} color={Colors.primary} />
        <Text style={styles.statValue}>{stats?.total_bookings || 0}</Text>
        <Text style={styles.statLabel}>Total Bookings</Text>
      </View>

      <View style={styles.statCard}>
        <Ionicons name="checkmark-circle" size={32} color={Colors.success} />
        <Text style={styles.statValue}>{stats?.completed_bookings || 0}</Text>
        <Text style={styles.statLabel}>Completed</Text>
      </View>

      <View style={styles.statCard}>
        <Ionicons name="cash" size={32} color={Colors.secondary} />
        <Text style={styles.statValue}>₹{stats?.total_revenue || 0}</Text>
        <Text style={styles.statLabel}>Total Revenue</Text>
      </View>

      <View style={styles.statCard}>
        <Ionicons name="trending-up" size={32} color={Colors.primary} />
        <Text style={styles.statValue}>₹{stats?.total_commission || 0}</Text>
        <Text style={styles.statLabel}>Commission (10%)</Text>
      </View>
    </View>
  );

  const renderDrivers = () => (
    <ScrollView style={styles.listContainer}>
      {drivers.map((driver: any) => (
        <TouchableOpacity
          key={driver.driver_id}
          style={styles.listItem}
          onPress={() => setSelectedDriver(driver)}
        >
          <View style={styles.listItemHeader}>
            <View>
              <Text style={styles.listItemTitle}>{driver.name}</Text>
              <Text style={styles.listItemSubtitle}>{driver.phone}</Text>
            </View>
            <View style={[
              styles.statusBadge,
              { backgroundColor:
                driver.approval_status === 'approved' ? Colors.success :
                driver.approval_status === 'rejected' ? Colors.error :
                Colors.warning
              }
            ]}>
              <Text style={styles.statusText}>
                {driver.approval_status.toUpperCase()}
              </Text>
            </View>
          </View>
          <Text style={styles.listItemDetails}>
            {driver.vehicle_type.toUpperCase()} • {driver.vehicle_number}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  const renderCustomers = () => (
    <ScrollView style={styles.listContainer}>
      {customers.map((customer: any) => (
        <View key={customer.user_id} style={styles.listItem}>
          <View style={styles.listItemHeader}>
            <View>
              <Text style={styles.listItemTitle}>{customer.name}</Text>
              <Text style={styles.listItemSubtitle}>{customer.phone}</Text>
            </View>
            <Ionicons name="person-circle" size={32} color={Colors.primary} />
          </View>
          <Text style={styles.listItemDetails}>
            Joined: {new Date(customer.created_at).toLocaleDateString()}
          </Text>
        </View>
      ))}
    </ScrollView>
  );

  const renderBookings = () => (
    <ScrollView style={styles.listContainer}>
      {bookings.map((booking: any) => (
        <View key={booking.booking_id} style={styles.listItem}>
          <View style={styles.listItemHeader}>
            <Text style={styles.listItemTitle}>
              #{booking.booking_id.slice(0, 8)}
            </Text>
            <View style={[
              styles.statusBadge,
              { backgroundColor:
                booking.status === 'completed' ? Colors.success :
                booking.status === 'cancelled' ? Colors.error :
                booking.status === 'ongoing' ? Colors.warning :
                Colors.primary
              }
            ]}>
              <Text style={styles.statusText}>{booking.status.toUpperCase()}</Text>
            </View>
          </View>
          <Text style={styles.listItemSubtitle} numberOfLines={1}>
            From: {booking.pickup.address}
          </Text>
          <Text style={styles.listItemSubtitle} numberOfLines={1}>
            To: {booking.drop.address}
          </Text>
          <View style={styles.bookingFooter}>
            <Text style={styles.listItemDetails}>
              {booking.distance} km • {booking.vehicle_type}
            </Text>
            <Text style={styles.fareText}>₹{booking.fare}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>VK Drop Taxi Admin</Text>
        <Text style={styles.headerSubtitle}>Dashboard</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabs}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'stats' && styles.activeTab]}
          onPress={() => setActiveTab('stats')}
        >
          <Ionicons name="stats-chart" size={20} color={activeTab === 'stats' ? Colors.primary : Colors.gray} />
          <Text style={[styles.tabText, activeTab === 'stats' && styles.activeTabText]}>
            Stats
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'drivers' && styles.activeTab]}
          onPress={() => setActiveTab('drivers')}
        >
          <Ionicons name="car" size={20} color={activeTab === 'drivers' ? Colors.primary : Colors.gray} />
          <Text style={[styles.tabText, activeTab === 'drivers' && styles.activeTabText]}>
            Drivers
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'customers' && styles.activeTab]}
          onPress={() => setActiveTab('customers')}
        >
          <Ionicons name="people" size={20} color={activeTab === 'customers' ? Colors.primary : Colors.gray} />
          <Text style={[styles.tabText, activeTab === 'customers' && styles.activeTabText]}>
            Customers
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'bookings' && styles.activeTab]}
          onPress={() => setActiveTab('bookings')}
        >
          <Ionicons name="receipt" size={20} color={activeTab === 'bookings' ? Colors.primary : Colors.gray} />
          <Text style={[styles.tabText, activeTab === 'bookings' && styles.activeTabText]}>
            Bookings
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.content}>
        {activeTab === 'stats' && renderStats()}
        {activeTab === 'drivers' && renderDrivers()}
        {activeTab === 'customers' && renderCustomers()}
        {activeTab === 'bookings' && renderBookings()}
      </ScrollView>

      {/* Driver Details Modal */}
      <Modal
        visible={!!selectedDriver}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setSelectedDriver(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Driver Details</Text>
              <TouchableOpacity onPress={() => setSelectedDriver(null)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            {selectedDriver && (
              <ScrollView>
                <View style={styles.driverInfo}>
                  <Text style={styles.infoLabel}>Name</Text>
                  <Text style={styles.infoValue}>{selectedDriver.name}</Text>
                </View>

                <View style={styles.driverInfo}>
                  <Text style={styles.infoLabel}>Phone</Text>
                  <Text style={styles.infoValue}>{selectedDriver.phone}</Text>
                </View>

                <View style={styles.driverInfo}>
                  <Text style={styles.infoLabel}>Vehicle Type</Text>
                  <Text style={styles.infoValue}>{selectedDriver.vehicle_type.toUpperCase()}</Text>
                </View>

                <View style={styles.driverInfo}>
                  <Text style={styles.infoLabel}>Vehicle Number</Text>
                  <Text style={styles.infoValue}>{selectedDriver.vehicle_number}</Text>
                </View>

                <View style={styles.driverInfo}>
                  <Text style={styles.infoLabel}>Status</Text>
                  <Text style={styles.infoValue}>{selectedDriver.approval_status.toUpperCase()}</Text>
                </View>

                {/* License Image */}
                <View style={styles.documentSection}>
                  <Text style={styles.documentLabel}>Driving License</Text>
                  <Image
                    source={{ uri: selectedDriver.license_image }}
                    style={styles.documentImage}
                  />
                </View>

                {/* RC Image */}
                <View style={styles.documentSection}>
                  <Text style={styles.documentLabel}>Vehicle RC</Text>
                  <Image
                    source={{ uri: selectedDriver.rc_image }}
                    style={styles.documentImage}
                  />
                </View>

                {selectedDriver.approval_status === 'pending' && (
                  <View style={styles.actionButtons}>
                    <Button
                      title="Approve"
                      onPress={() => handleApproveDriver(selectedDriver.driver_id, 'approved')}
                      variant="secondary"
                      style={styles.approveButton}
                    />
                    <Button
                      title="Reject"
                      onPress={() => handleApproveDriver(selectedDriver.driver_id, 'rejected')}
                      variant="outline"
                      style={styles.rejectButton}
                    />
                  </View>
                )}
              </ScrollView>
            )}
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
    backgroundColor: Colors.primary,
    padding: 24,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
  },
  headerSubtitle: {
    fontSize: 16,
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  activeTab: {
    borderBottomWidth: 3,
    borderBottomColor: Colors.primary,
  },
  tabText: {
    fontSize: 12,
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
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
  },
  statCard: {
    width: '50%',
    padding: 16,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textLight,
    marginTop: 4,
    textAlign: 'center',
  },
  listContainer: {
    padding: 16,
  },
  listItem: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  listItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  listItemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
  },
  listItemSubtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 4,
  },
  listItemDetails: {
    fontSize: 12,
    color: Colors.gray,
    marginTop: 4,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
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
  driverInfo: {
    marginBottom: 16,
  },
  infoLabel: {
    fontSize: 12,
    color: Colors.textLight,
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    color: Colors.text,
    fontWeight: '600',
  },
  documentSection: {
    marginTop: 16,
  },
  documentLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 8,
  },
  documentImage: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    backgroundColor: Colors.lightGray,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
  },
  approveButton: {
    flex: 1,
  },
  rejectButton: {
    flex: 1,
  },
});
