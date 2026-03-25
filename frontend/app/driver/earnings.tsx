import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../store/authStore';
import { Colors } from '../../utils/colors';
import { getDriverEarnings, withdrawMoney } from '../../utils/api';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Ionicons } from '@expo/vector-icons';

export default function EarningsScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [earnings, setEarnings] = useState<any>(null);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEarnings();
  }, []);

  const fetchEarnings = async () => {
    try {
      const response = await getDriverEarnings(user?.driver_id || '');
      setEarnings(response.data);
    } catch (error) {
      console.error('Failed to fetch earnings:', error);
    }
  };

  const handleWithdraw = async () => {
    const amount = parseFloat(withdrawAmount);
    if (isNaN(amount) || amount <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }

    if (amount > (earnings?.total_earnings || 0)) {
      Alert.alert('Error', 'Insufficient balance');
      return;
    }

    setLoading(true);
    try {
      await withdrawMoney(user?.driver_id || '', amount);
      Alert.alert('Success', 'Withdrawal request submitted');
      setWithdrawAmount('');
      fetchEarnings();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Withdrawal failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.white} />
        </TouchableOpacity>
        <Text style={styles.title}>Earnings</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Earnings Summary */}
        <View style={styles.summaryCard}>
          <View style={styles.summaryItem}>
            <Ionicons name="cash-outline" size={32} color={Colors.primary} />
            <Text style={styles.summaryLabel}>Total Earnings</Text>
            <Text style={styles.summaryAmount}>₹{earnings?.total_earnings || 0}</Text>
          </View>

          <View style={styles.divider} />

          <View style={styles.summaryItem}>
            <Ionicons name="car-sport-outline" size={32} color={Colors.secondary} />
            <Text style={styles.summaryLabel}>Total Rides</Text>
            <Text style={styles.summaryAmount}>{earnings?.total_rides || 0}</Text>
          </View>
        </View>

        {/* Wallet Balance */}
        <View style={styles.walletCard}>
          <Text style={styles.walletLabel}>Available Balance</Text>
          <Text style={styles.walletAmount}>₹{earnings?.wallet_balance || 0}</Text>
        </View>

        {/* Withdraw Section */}
        <View style={styles.withdrawSection}>
          <Text style={styles.sectionTitle}>Withdraw Money</Text>
          <Input
            placeholder="Enter amount"
            keyboardType="numeric"
            value={withdrawAmount}
            onChangeText={setWithdrawAmount}
          />

          <View style={styles.quickAmounts}>
            {[500, 1000, 2000, 5000].map((value) => (
              <TouchableOpacity
                key={value}
                style={styles.quickButton}
                onPress={() => setWithdrawAmount(value.toString())}
              >
                <Text style={styles.quickButtonText}>₹{value}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Button
            title="Request Withdrawal"
            onPress={handleWithdraw}
            loading={loading}
            variant="secondary"
          />

          <Text style={styles.withdrawNote}>
            Withdrawal requests are processed within 2-3 business days
          </Text>
        </View>

        {/* Stats */}
        <View style={styles.statsSection}>
          <Text style={styles.sectionTitle}>Statistics</Text>
          
          <View style={styles.statCard}>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Average per ride</Text>
              <Text style={styles.statValue}>
                ₹{earnings?.total_rides > 0
                  ? Math.round(earnings.total_earnings / earnings.total_rides)
                  : 0}
              </Text>
            </View>
          </View>
        </View>
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
    backgroundColor: Colors.secondary,
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.white,
  },
  placeholder: {
    width: 40,
  },
  content: {
    padding: 16,
  },
  summaryCard: {
    backgroundColor: Colors.white,
    borderRadius: 20,
    padding: 24,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  summaryItem: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  summaryLabel: {
    fontSize: 14,
    color: Colors.textLight,
    marginTop: 8,
  },
  summaryAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 4,
  },
  divider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 8,
  },
  walletCard: {
    backgroundColor: Colors.primary,
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
    marginBottom: 24,
  },
  walletLabel: {
    fontSize: 16,
    color: Colors.text,
  },
  walletAmount: {
    fontSize: 40,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  withdrawSection: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  quickAmounts: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  quickButton: {
    flex: 1,
    paddingVertical: 12,
    backgroundColor: Colors.lightGray,
    borderRadius: 12,
    alignItems: 'center',
  },
  quickButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.text,
  },
  withdrawNote: {
    fontSize: 12,
    color: Colors.gray,
    textAlign: 'center',
    marginTop: 12,
  },
  statsSection: {
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: Colors.lightGray,
    borderRadius: 12,
    padding: 16,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  statLabel: {
    fontSize: 14,
    color: Colors.textLight,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
  },
});