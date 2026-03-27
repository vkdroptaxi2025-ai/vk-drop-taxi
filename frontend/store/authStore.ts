import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Minimal user data - NO large objects like images/documents
interface User {
  user_id?: string;
  driver_id?: string;
  phone: string;
  name: string;
  role: 'customer' | 'driver' | 'admin';
  approval_status?: string;
  is_online?: boolean;
  vehicle_type?: string;
  vehicle_number?: string;
  earnings?: number;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: any) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
}

// Helper function to extract only minimal user data
// This prevents AsyncStorage quota exceeded errors
const extractMinimalUserData = (userData: any): User | null => {
  if (!userData) return null;
  
  // Extract ONLY essential fields - NO images, documents, or large objects
  return {
    user_id: userData.user_id || userData._id,
    driver_id: userData.driver_id,
    phone: userData.phone || userData.personal_details?.phone || '',
    name: userData.name || userData.full_name || userData.personal_details?.full_name || 'User',
    role: userData.role || 'customer',
    approval_status: userData.approval_status,
    is_online: userData.is_online || userData.duty_on || false,
    vehicle_type: userData.vehicle_type || userData.vehicle_details?.vehicle_type,
    vehicle_number: userData.vehicle_number || userData.vehicle_details?.vehicle_number,
    earnings: userData.earnings || 0,
  };
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  
  setUser: async (userData) => {
    try {
      // Extract ONLY minimal data - prevents quota exceeded error
      const minimalUser = extractMinimalUserData(userData);
      
      set({ user: minimalUser, isAuthenticated: !!minimalUser });
      
      if (minimalUser) {
        // Store only minimal data in AsyncStorage
        const dataToStore = JSON.stringify(minimalUser);
        console.log('[AuthStore] Storing user data, size:', dataToStore.length, 'bytes');
        await AsyncStorage.setItem('user', dataToStore);
      } else {
        await AsyncStorage.removeItem('user');
      }
    } catch (error: any) {
      console.error('[AuthStore] Failed to save user:', error.message);
      // If quota exceeded, try to clear and save again
      if (error.message?.includes('quota')) {
        console.log('[AuthStore] Quota exceeded, clearing old data...');
        await AsyncStorage.clear();
        const minimalUser = extractMinimalUserData(userData);
        if (minimalUser) {
          await AsyncStorage.setItem('user', JSON.stringify(minimalUser));
        }
        set({ user: minimalUser, isAuthenticated: !!minimalUser });
      }
    }
  },
  
  logout: async () => {
    try {
      await AsyncStorage.removeItem('user');
    } catch (error) {
      console.error('[AuthStore] Failed to remove user:', error);
    }
    set({ user: null, isAuthenticated: false });
  },
  
  loadUser: async () => {
    try {
      const userStr = await AsyncStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        console.log('[AuthStore] Loaded user:', user.name, user.driver_id);
        set({ user, isAuthenticated: true });
      }
    } catch (error) {
      console.error('[AuthStore] Failed to load user:', error);
    }
  },
}));
