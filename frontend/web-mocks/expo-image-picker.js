// Web mock for expo-image-picker
// This provides web-compatible image picking functionality

export const MediaTypeOptions = {
  All: 'All',
  Images: 'Images',
  Videos: 'Videos',
};

export const requestMediaLibraryPermissionsAsync = async () => {
  console.log('[Web Mock] requestMediaLibraryPermissionsAsync called');
  return { status: 'granted', granted: true };
};

export const requestCameraPermissionsAsync = async () => {
  console.log('[Web Mock] requestCameraPermissionsAsync called');
  return { status: 'granted', granted: true };
};

export const launchImageLibraryAsync = async (options = {}) => {
  console.log('[Web Mock] launchImageLibraryAsync called with options:', options);
  
  return new Promise((resolve) => {
    // Create a hidden file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.style.display = 'none';
    
    input.onchange = (event) => {
      const file = event.target.files?.[0];
      if (file) {
        console.log('[Web Mock] File selected:', file.name);
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result;
          // Extract just the base64 data without the data URL prefix for consistency
          const base64Data = base64.toString().split(',')[1];
          console.log('[Web Mock] Image converted to base64, length:', base64Data?.length);
          resolve({
            canceled: false,
            assets: [{
              uri: base64.toString(),
              base64: base64Data,
              width: 800,
              height: 600,
              type: 'image',
              fileName: file.name,
              fileSize: file.size,
            }],
          });
        };
        reader.onerror = (error) => {
          console.error('[Web Mock] FileReader error:', error);
          resolve({ canceled: true, assets: [] });
        };
        reader.readAsDataURL(file);
      } else {
        console.log('[Web Mock] No file selected');
        resolve({ canceled: true, assets: [] });
      }
      document.body.removeChild(input);
    };
    
    input.oncancel = () => {
      console.log('[Web Mock] File picker cancelled');
      resolve({ canceled: true, assets: [] });
      document.body.removeChild(input);
    };
    
    document.body.appendChild(input);
    input.click();
  });
};

export const launchCameraAsync = async (options = {}) => {
  console.log('[Web Mock] launchCameraAsync called - redirecting to gallery on web');
  // On web, camera is not directly accessible, so we use file picker
  return launchImageLibraryAsync(options);
};

export default {
  MediaTypeOptions,
  requestMediaLibraryPermissionsAsync,
  requestCameraPermissionsAsync,
  launchImageLibraryAsync,
  launchCameraAsync,
};
