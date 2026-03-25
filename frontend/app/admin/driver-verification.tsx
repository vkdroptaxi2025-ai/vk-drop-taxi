import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Modal,
  ScrollView,
  Alert,
  Image,
  RefreshControl,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Colors } from '../../utils/colors';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import axios from 'axios';

export default function AdminDriverVerification() {
  const router = useRouter();
  const [pendingDrivers, setPendingDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    fetchPendingDrivers();
  }, []);

  const fetchPendingDrivers = async () => {
    setLoading(true);
    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
      const response = await axios.get(`${API_URL}/api/admin/drivers/pending-verification`);
      setPendingDrivers(response.data.pending_drivers || []);
    } catch (error) {
      console.error('Error fetching pending drivers:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewDriverDetails = async (driverId: string) => {
    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
      const response = await axios.get(`${API_URL}/api/admin/driver/${driverId}/verification-view`);
      setSelectedDriver(response.data.driver);
      setShowModal(true);
    } catch (error) {
      Alert.alert('Error', 'Failed to load driver details');
    }
  };

  const handleApprove = async () => {
    if (!selectedDriver) return;

    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
      await axios.put(`${API_URL}/api/admin/driver/approve`, {
        driver_id: selectedDriver.driver_id,
        approval_status: 'approved',
        rejection_reason: null,
      });

      Alert.alert('Success', 'Driver approved successfully!');
      setShowModal(false);
      setSelectedDriver(null);
      fetchPendingDrivers();
    } catch (error) {
      Alert.alert('Error', 'Failed to approve driver');
    }
  };

  const handleReject = async () => {
    if (!selectedDriver) return;

    if (!rejectionReason.trim()) {
      Alert.alert('Error', 'Please enter rejection reason');
      return;
    }

    try {
      const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
      await axios.put(`${API_URL}/api/admin/driver/approve`, {
        driver_id: selectedDriver.driver_id,
        approval_status: 'rejected',
        rejection_reason: rejectionReason,
      });

      Alert.alert('Success', 'Driver application rejected');
      setShowModal(false);
      setSelectedDriver(null);
      setRejectionReason('');
      fetchPendingDrivers();
    } catch (error) {
      Alert.alert('Error', 'Failed to reject driver');
    }
  };

  const renderDriverCard = ({ item }: any) => {
    const hasExpiredDocs = item.expiry_alerts?.has_expired_documents || false;
    const hasExpiringDocs = item.expiry_alerts?.has_expiring_documents || false;

    return (
      <TouchableOpacity
        style={styles.driverCard}
        onPress={() => viewDriverDetails(item.driver_id)}
      >
        <View style={styles.cardHeader}>
          <View style={styles.driverInfo}>
            <Text style={styles.driverName}>
              {item.personal_details?.full_name || 'N/A'}
            </Text>
            <Text style={styles.driverPhone}>{item.phone}</Text>
            <Text style={styles.driverVehicle}>
              {item.vehicle_details?.vehicle_type?.toUpperCase()} • {item.vehicle_details?.vehicle_number}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color={Colors.gray} />
        </View>

        {(hasExpiredDocs || hasExpiringDocs) && (
          <View style={styles.alertBanner}>
            <Ionicons
              name="warning"
              size={16}
              color={hasExpiredDocs ? Colors.error : Colors.warning}
            />
            <Text style={styles.alertText}>
              {hasExpiredDocs ? 'Has expired documents' : 'Documents expiring soon'}
            </Text>
          </View>
        )}

        <View style={styles.cardFooter}>
          <Text style={styles.registeredDate}>
            Registered: {new Date(item.created_at).toLocaleDateString()}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  const renderDocumentImage = (label: string, imageData: any) => {
    if (!imageData) return null;

    return (
      <View style={styles.documentSection}>
        <Text style={styles.documentLabel}>{label}</Text>
        {imageData.front_image && (
          <Image
            source={{ uri: imageData.front_image }}
            style={styles.documentImage}
          />
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.white} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>Driver Verification</Text>
          <Text style={styles.headerSubtitle}>
            {pendingDrivers.length} Pending Approval{pendingDrivers.length !== 1 ? 's' : ''}
          </Text>
        </View>
      </View>

      <FlatList
        data={pendingDrivers}
        renderItem={renderDriverCard}
        keyExtractor={(item) => item.driver_id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={fetchPendingDrivers} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="checkmark-circle" size={60} color={Colors.success} />
            <Text style={styles.emptyText}>No pending verifications</Text>
          </View>
        }
      />

      {/* Driver Details Modal */}
      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Driver Details</Text>
              <TouchableOpacity onPress={() => setShowModal(false)}>
                <Ionicons name="close" size={28} color={Colors.text} />
              </TouchableOpacity>
            </View>

            {selectedDriver && (
              <ScrollView style={styles.modalScroll}>
                {/* Personal Details */}
                <Text style={styles.sectionTitle}>Personal Details</Text>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Full Name:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.full_name}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Phone:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.mobile_number}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Address:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.full_address}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Aadhaar:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.aadhaar_number}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>PAN:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.pan_number}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>License:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.driving_license_number}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Experience:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.personal_details?.driving_experience_years} years</Text>
                </View>

                {/* Bank Details */}
                <Text style={[styles.sectionTitle, { marginTop: 16 }]}>Bank Details</Text>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Account Holder:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.bank_details?.account_holder_name}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Bank:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.bank_details?.bank_name}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Account Number:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.bank_details?.account_number}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>IFSC:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.bank_details?.ifsc_code}</Text>
                </View>

                {/* Vehicle Details */}
                <Text style={[styles.sectionTitle, { marginTop: 16 }]}>Vehicle Details</Text>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Type:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.vehicle_details?.vehicle_type?.toUpperCase()}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Number:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.vehicle_details?.vehicle_number}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Model:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.vehicle_details?.vehicle_model}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Year:</Text>
                  <Text style={styles.detailValue}>{selectedDriver.vehicle_details?.vehicle_year}</Text>
                </View>

                {/* Documents */}
                <Text style={[styles.sectionTitle, { marginTop: 16 }]}>Documents</Text>
                {renderDocumentImage('Aadhaar Card', selectedDriver.documents?.aadhaar_card)}
                {renderDocumentImage('PAN Card', selectedDriver.documents?.pan_card)}
                {renderDocumentImage('Driving License', selectedDriver.documents?.driving_license)}
                {renderDocumentImage('RC Book', selectedDriver.documents?.rc_book)}
                {renderDocumentImage('Insurance', selectedDriver.documents?.insurance)}
                {renderDocumentImage('Fitness Certificate', selectedDriver.documents?.fitness_certificate)}
                {renderDocumentImage('Permit', selectedDriver.documents?.permit)}
                {renderDocumentImage('Pollution Certificate', selectedDriver.documents?.pollution_certificate)}

                {/* Driver + Vehicle Photo */}
                <Text style={[styles.sectionTitle, { marginTop: 16 }]}>Driver + Vehicle Photo</Text>
                <Image
                  source={{ uri: selectedDriver.driver_vehicle_photo }}
                  style={[styles.documentImage, { height: 250 }]}
                />

                {/* Expiry Alerts */}
                {selectedDriver.expiry_alerts?.critical_alerts?.length > 0 && (
                  <View style={styles.alertsSection}>
                    <Text style={styles.sectionTitle}>Expiry Alerts</Text>
                    {selectedDriver.expiry_alerts.critical_alerts.map((alert: any, index: number) => (
                      <View
                        key={index}
                        style={[
                          styles.alertItem,
                          { backgroundColor: alert.alert_level === 'critical' ? '#fee' : '#ffc' },
                        ]}
                      >
                        <Text style={styles.alertItemText}>
                          {alert.document.replace('_', ' ').toUpperCase()}: {alert.message}
                        </Text>
                      </View>
                    ))}
                  </View>
                )}

                {/* Rejection Reason Input */}
                <Input
                  label="Rejection Reason (if rejecting)"
                  placeholder="Enter reason for rejection"
                  value={rejectionReason}
                  onChangeText={setRejectionReason}
                  multiline
                />

                {/* Action Buttons */}
                <View style={styles.actionButtons}>
                  <Button
                    title="Approve Driver"
                    onPress={handleApprove}
                    variant="secondary"
                    style={styles.approveButton}
                  />
                  <Button
                    title="Reject"
                    onPress={handleReject}
                    variant="outline"
                    style={styles.rejectButton}
                  />
                </View>
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
    padding: 16,
    paddingTop: 60,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  headerSubtitle: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 4,
  },
  listContent: {
    padding: 16,
  },
  driverCard: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderLeftWidth: 4,
    borderLeftColor: Colors.warning,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  driverInfo: {
    flex: 1,
  },
  driverName: {
    fontSize: 16,
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
  alertBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.lightGray,
    padding: 8,
    borderRadius: 8,
    marginTop: 12,
    gap: 8,
  },
  alertText: {
    fontSize: 12,
    color: Colors.error,
    fontWeight: '600',
  },
  cardFooter: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  registeredDate: {
    fontSize: 12,
    color: Colors.gray,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 60,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
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
    maxHeight: '95%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  modalScroll: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.lightGray,
  },
  detailLabel: {
    fontSize: 14,
    color: Colors.textLight,
    flex: 1,
  },
  detailValue: {
    fontSize: 14,
    color: Colors.text,
    fontWeight: '600',
    flex: 1,
    textAlign: 'right',
  },
  documentSection: {
    marginBottom: 16,
  },
  documentLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: 8,
  },
  documentImage: {
    width: '100%',
    height: 150,
    borderRadius: 8,
    backgroundColor: Colors.lightGray,
  },
  alertsSection: {
    marginTop: 16,
  },
  alertItem: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  alertItemText: {
    fontSize: 12,
    color: Colors.text,
    fontWeight: '600',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
    marginBottom: 40,
  },
  approveButton: {
    flex: 1,
  },
  rejectButton: {
    flex: 1,
  },
});
