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
import { getWallet, addMoney } from '../../utils/api';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { Ionicons } from '@expo/vector-icons';

export default function WalletScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [wallet, setWallet] = useState<any>(null);
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchWallet();
  }, []);

  const fetchWallet = async () => {
    try {
      const response = await getWallet(user?.user_id || '');
      setWallet(response.data.wallet);
    } catch (error) {
      console.error('Failed to fetch wallet:', error);
    }
  };

  const handleAddMoney = async () => {
    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }

    setLoading(true);
    try {
      await addMoney(user?.user_id || '', amountNum);
      Alert.alert('Success', `₹${amountNum} added to wallet`);
      setAmount('');
      fetchWallet();
    } catch (error) {
      Alert.alert('Error', 'Failed to add money');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={styles.title}>Wallet</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Balance Card */}
        <View style={styles.balanceCard}>
          <Ionicons name="wallet" size={40} color={Colors.primary} />
          <Text style={styles.balanceLabel}>Current Balance</Text>
          <Text style={styles.balanceAmount}>₹{wallet?.balance || 0}</Text>
        </View>

        {/* Add Money Section */}
        <View style={styles.addMoneySection}>
          <Text style={styles.sectionTitle}>Add Money</Text>
          <Input
            placeholder="Enter amount"
            keyboardType="numeric"
            value={amount}
            onChangeText={setAmount}
          />

          <View style={styles.quickAmounts}>
            {[100, 200, 500, 1000].map((value) => (
              <TouchableOpacity
                key={value}
                style={styles.quickButton}
                onPress={() => setAmount(value.toString())}
              >
                <Text style={styles.quickButtonText}>₹{value}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Button
            title="Add Money (Mock Payment)"
            onPress={handleAddMoney}
            loading={loading}
            variant="primary"
          />
        </View>

        {/* Transactions */}
        <View style={styles.transactionsSection}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
          {wallet?.transactions && wallet.transactions.length > 0 ? (
            wallet.transactions.slice(0, 10).map((txn: any) => (
              <View key={txn.transaction_id} style={styles.transactionItem}>
                <View>
                  <Text style={styles.transactionDesc}>{txn.description}</Text>
                  <Text style={styles.transactionDate}>
                    {new Date(txn.timestamp).toLocaleString()}
                  </Text>
                </View>
                <Text
                  style={[
                    styles.transactionAmount,
                    { color: txn.type === 'credit' ? Colors.success : Colors.error },
                  ]}
                >
                  {txn.type === 'credit' ? '+' : '-'}₹{txn.amount}
                </Text>
              </View>
            ))
          ) : (
            <Text style={styles.noTransactions}>No transactions yet</Text>
          )}
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
    backgroundColor: Colors.white,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  placeholder: {
    width: 40,
  },
  content: {
    padding: 16,
  },
  balanceCard: {
    backgroundColor: Colors.primary,
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
    marginBottom: 24,
  },
  balanceLabel: {
    fontSize: 16,
    color: Colors.text,
    marginTop: 12,
  },
  balanceAmount: {
    fontSize: 40,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
  },
  addMoneySection: {
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
  transactionsSection: {
    marginBottom: 24,
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  transactionDesc: {
    fontSize: 14,
    color: Colors.text,
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 12,
    color: Colors.gray,
  },
  transactionAmount: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  noTransactions: {
    fontSize: 14,
    color: Colors.gray,
    textAlign: 'center',
    paddingVertical: 24,
  },
});