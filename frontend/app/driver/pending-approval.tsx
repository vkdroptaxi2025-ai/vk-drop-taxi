import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';
import { getDriverApprovalStatus } from '../../utils/api';

// Yellow + Green theme colors
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
  warning: '#FFC107',
};

export default function PendingApprovalScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>('pending');
  const [rejectionReason, setRejectionReason] = useState<string | null>(null);

  useEffect(() => {
    if (user?.driver_id) {
      checkStatus();
    }
  }, []);

  const checkStatus = async () => {
    if (!user?.driver_id) return;

    setLoading(true);
    try {
      const response = await getDriverApprovalStatus(user.driver_id);
      if (response.data.success) {
        setStatus(response.data.approval_status);
        setRejectionReason(response.data.rejection_reason);

        // If approved, redirect to dashboard
        if (response.data.approval_status === 'approved') {
          Alert.alert('Congratulations!', 'Your account has been approved!', [
            { text: 'Go to Dashboard', onPress: () => router.replace('/driver/dashboard') }
          ]);
        }
      }
    } catch (error) {
      console.error('Error checking status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/');
  };

  const getStatusConfig = () => {
    switch (status) {
      case 'approved':
        return {
          icon: 'checkmark-circle',
          color: COLORS.success,
          title: 'Account Approved!',
          message: 'Your account has been approved. You can now start accepting rides.',
          showDashboardButton: true,
        };
      case 'rejected':
        return {
          icon: 'close-circle',
          color: COLORS.error,
          title: 'Application Rejected',
          message: rejectionReason || 'Your application has been rejected. Please contact support for more information.',
          showDashboardButton: false,
        };
      default:
        return {
          icon: 'time',
          color: COLORS.warning,
          title: 'Approval Pending',
          message: 'Your application is under review. Admin will verify your documents and approve your account.',
          showDashboardButton: false,
        };
    }
  };

  const config = getStatusConfig();

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>VK Drop Taxi</Text>
        <Text style={styles.headerSubtitle}>Driver Panel</Text>
      </View>

      {/* Status Card */}
      <View style={styles.content}>
        <View style={[styles.statusIconContainer, { backgroundColor: `${config.color}20` }]}>
          <Ionicons name={config.icon as any} size={80} color={config.color} />
        </View>

        <Text style={styles.statusTitle}>{config.title}</Text>
        <Text style={styles.statusMessage}>{config.message}</Text>

        {/* Status Badge */}
        <View style={[styles.statusBadge, { borderColor: config.color }]}>
          <View style={[styles.statusDot, { backgroundColor: config.color }]} />
          <Text style={[styles.statusBadgeText, { color: config.color }]}>
            {status.toUpperCase()}
          </Text>
        </View>

        {/* Refresh Button */}
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={checkStatus}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={COLORS.secondary} />
          ) : (
            <>
              <Ionicons name="refresh" size={20} color={COLORS.secondary} />
              <Text style={styles.refreshButtonText}>Refresh Status</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Dashboard Button (if approved) */}
        {config.showDashboardButton && (
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => router.replace('/driver/dashboard')}
          >
            <Text style={styles.primaryButtonText}>Go to Dashboard</Text>
            <Ionicons name="arrow-forward" size={20} color={COLORS.text} />
          </TouchableOpacity>
        )}

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color={COLORS.secondary} />
          <View style={styles.infoTextContainer}>
            <Text style={styles.infoTitle}>What happens next?</Text>
            <Text style={styles.infoText}>
              • Admin will verify your documents{'\n'}
              • You'll be notified once approved{'\n'}
              • After approval, you can start taking rides
            </Text>
          </View>
        </View>

        {/* Logout Button */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Ionicons name="log-out-outline" size={20} color={COLORS.error} />
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    backgroundColor: COLORS.primary,
    paddingTop: 60,
    paddingBottom: 24,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  headerSubtitle: {
    fontSize: 14,
    color: COLORS.textLight,
    marginTop: 4,
  },
  content: {
    flex: 1,
    padding: 24,
    alignItems: 'center',
  },
  statusIconContainer: {
    width: 140,
    height: 140,
    borderRadius: 70,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
    marginBottom: 24,
  },
  statusTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 12,
    textAlign: 'center',
  },
  statusMessage: {
    fontSize: 16,
    color: COLORS.textLight,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
    paddingHorizontal: 16,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    borderWidth: 2,
    marginBottom: 24,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  statusBadgeText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: COLORS.secondary,
    marginBottom: 16,
    gap: 8,
  },
  refreshButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.secondary,
  },
  primaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    marginBottom: 24,
    gap: 8,
    width: '100%',
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.card,
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.secondary,
    width: '100%',
  },
  infoTextContainer: {
    flex: 1,
    marginLeft: 12,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: COLORS.textLight,
    lineHeight: 22,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    gap: 8,
  },
  logoutButtonText: {
    fontSize: 16,
    color: COLORS.error,
    fontWeight: '600',
  },
});
