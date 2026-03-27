import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for large image uploads
  headers: {
    'Content-Type': 'application/json',
  },
  maxContentLength: 50 * 1024 * 1024, // 50MB max
  maxBodyLength: 50 * 1024 * 1024, // 50MB max
});

// Auth APIs
export const sendOTP = (phone: string, role: string) =>
  api.post('/api/auth/send-otp', { phone, role });

export const verifyOTP = (phone: string, otp: string, role: string) =>
  api.post('/api/auth/verify-otp', { phone, otp, role });

export const registerCustomer = (data: any) =>
  api.post('/api/customer/register', data);

export const registerDriver = (data: any) =>
  api.post('/api/driver/register', data);

export const onboardDriver = (data: any) =>
  api.post('/api/driver/onboard', data, {
    timeout: 60000, // 60 second timeout for driver onboarding
  });

export const getDriverApprovalStatus = (driverId: string) =>
  api.get(`/api/driver/${driverId}/status`);

export const getDriverStatusByPhone = (phone: string) =>
  api.get(`/api/driver/phone/${phone}/status`);

// Customer APIs
export const getCustomerProfile = (customerId: string) =>
  api.get(`/api/customer/${customerId}/profile`);

export const getCustomerBookings = (customerId: string) =>
  api.get(`/api/customer/${customerId}/bookings`);

// Driver APIs
export const getDriverProfile = (driverId: string) =>
  api.get(`/api/driver/${driverId}/profile`);

export const updateDriverStatus = (driverId: string, isOnline: boolean) =>
  api.put(`/api/driver/${driverId}/status`, { is_online: isOnline });

export const getDriverRides = (driverId: string) =>
  api.get(`/api/driver/${driverId}/rides`);

export const getPendingRides = (driverId: string) =>
  api.get(`/api/driver/${driverId}/pending-rides`);

export const getDriverEarnings = (driverId: string) =>
  api.get(`/api/driver/${driverId}/earnings`);

// Booking APIs
export const createBooking = (data: any) =>
  api.post('/api/booking/create', data);

export const updateBooking = (data: any) =>
  api.put('/api/booking/update', data);

export const getBooking = (bookingId: string) =>
  api.get(`/api/booking/${bookingId}`);

// Wallet APIs
export const getWallet = (userId: string) =>
  api.get(`/api/wallet/${userId}`);

export const addMoney = (userId: string, amount: number) =>
  api.post('/api/wallet/add-money', { user_id: userId, amount });

export const withdrawMoney = (driverId: string, amount: number) =>
  api.post('/api/wallet/withdraw', { driver_id: driverId, amount });

// Admin APIs
export const getAllDrivers = () =>
  api.get('/api/admin/drivers');

export const approveDriver = async (driverId: string, status: string, rejectionReason?: string) => {
  const payload = { 
    driver_id: driverId, 
    approval_status: status,
    rejection_reason: rejectionReason 
  };
  
  try {
    // Try the new endpoint first
    return await api.put('/api/admin/driver/approve', payload);
  } catch (error: any) {
    // If 404, try the legacy endpoint
    if (error.response?.status === 404) {
      console.log('[API] Trying legacy approve-driver endpoint...');
      return await api.put('/api/admin/approve-driver', payload);
    }
    throw error;
  }
};

export const resetDriverStatus = (driverId: string) =>
  api.put(`/api/admin/driver/reset/${driverId}`);

export const deleteDriver = (driverId: string) =>
  api.delete(`/api/admin/driver/${driverId}`);

export const getAllCustomers = () =>
  api.get('/api/admin/customers');

export const getAllBookings = () =>
  api.get('/api/admin/bookings');

export const getAdminStats = () =>
  api.get('/api/admin/stats');

export const getTariffs = () =>
  api.get('/api/admin/tariffs');

export const updateTariff = (data: any) =>
  api.put('/api/admin/update-tariff', data);

// ==================== PHASE 2 & 3: DISPATCH APIs ====================

// Driver Duty APIs
export const updateDutyStatus = (driverId: string, data: {
  duty_on: boolean;
  is_online?: boolean;
  go_home_mode?: boolean;
  home_latitude?: number;
  home_longitude?: number;
  home_address?: string;
}) => api.put(`/api/driver/${driverId}/duty-status`, data);

export const updateDriverLocation = (driverId: string, data: {
  latitude: number;
  longitude: number;
  address: string;
}) => api.put(`/api/driver/${driverId}/location`, data);

export const getQueueStatus = (driverId: string) =>
  api.get(`/api/driver/${driverId}/queue-status`);

export const getDriverProfileComplete = (driverId: string) =>
  api.get(`/api/driver/${driverId}/profile-complete`);

// Smart Booking APIs
export const createSmartBooking = (data: {
  customer_id: string;
  pickup: { latitude: number; longitude: number; address: string };
  drop: { latitude: number; longitude: number; address: string };
  vehicle_type: string;
  assignment_mode?: string;
  manual_driver_id?: string;
}) => api.post('/api/booking/create-smart', data);

// Accept/Reject Booking
export const acceptRejectBooking = (data: {
  booking_id: string;
  driver_id: string;
  action: 'accept' | 'reject';
}) => api.post('/api/booking/accept-reject', data);

// Trip Lifecycle
export const startTrip = (bookingId: string) =>
  api.put(`/api/booking/${bookingId}/start-trip`);

export const completeTrip = (bookingId: string) =>
  api.put(`/api/booking/${bookingId}/complete-trip`);

// Admin Dispatch APIs
export const getPendingVerificationDrivers = () =>
  api.get('/api/admin/drivers/pending-verification');

export const getAvailableDriversForAssignment = () =>
  api.get('/api/admin/drivers');

// Wallet APIs
export const addWalletMoney = (userId: string, amount: number) =>
  api.post('/api/wallet/add-money', { user_id: userId, amount });

export const getWalletBalance = (userId: string) =>
  api.get(`/api/wallet/${userId}`);

export default api;