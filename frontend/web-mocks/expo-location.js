// Empty module for web compatibility
export default {};
export const requestForegroundPermissionsAsync = () => Promise.resolve({ status: 'granted' });
export const getCurrentPositionAsync = () => Promise.resolve({
  coords: {
    latitude: 19.0760,
    longitude: 72.8777,
  },
});
