import { Stack } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';

// Prevent the splash screen from auto-hiding
SplashScreen.preventAutoHideAsync().catch(() => {
  /* ignore - might not be supported on web */
});

export default function RootLayout() {
  const [appIsReady, setAppIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Add any initialization logic here (fonts, auth check, etc.)
        // For now, just a brief delay to ensure everything loads
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (e) {
        console.warn('App preparation error:', e);
      } finally {
        setAppIsReady(true);
        // Hide splash screen
        await SplashScreen.hideAsync().catch(() => {
          /* ignore - might not be supported on web */
        });
      }
    }

    prepare();
  }, []);

  if (!appIsReady) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FFD700" />
      </View>
    );
  }

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="auth/login" options={{ headerShown: false }} />
      <Stack.Screen name="auth/admin-login" options={{ headerShown: false }} />
      <Stack.Screen name="auth/driver-onboarding" options={{ headerShown: false }} />
      <Stack.Screen name="customer/home" options={{ headerShown: false }} />
      <Stack.Screen name="driver/dashboard" options={{ headerShown: false }} />
      <Stack.Screen name="driver/pending-approval" options={{ headerShown: false }} />
      <Stack.Screen name="admin/dashboard" options={{ headerShown: false }} />
    </Stack>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000000',
  },
});
