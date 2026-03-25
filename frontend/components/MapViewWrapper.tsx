import React from 'react';
import { View, Text, StyleSheet, Platform } from 'react-native';
import { Colors } from '../utils/colors';

// Conditional import for native platforms only - use try/catch to prevent web bundler issues
let MapView: any = null;
let Marker: any = null;

try {
  if (Platform.OS !== 'web') {
    const RNMaps = require('react-native-maps');
    MapView = RNMaps.default;
    Marker = RNMaps.Marker;
  }
} catch (error) {
  // Silently fail on web
}

interface MapViewWrapperProps {
  initialRegion: {
    latitude: number;
    longitude: number;
    latitudeDelta: number;
    longitudeDelta: number;
  };
  style?: any;
  children?: React.ReactNode;
}

export const MapViewWrapper: React.FC<MapViewWrapperProps> = ({
  initialRegion,
  style,
  children,
}) => {
  if (Platform.OS === 'web' || !MapView) {
    // Web fallback - show placeholder
    return (
      <View style={[styles.webMapPlaceholder, style]}>
        <Text style={styles.webMapText}>📍 Map View</Text>
        <Text style={styles.webMapSubtext}>
          (Maps work on mobile app)
        </Text>
      </View>
    );
  }

  // Native platforms
  return (
    <MapView style={style} initialRegion={initialRegion}>
      {children}
    </MapView>
  );
};

interface MarkerWrapperProps {
  coordinate: {
    latitude: number;
    longitude: number;
  };
  title?: string;
  pinColor?: string;
}

export const MarkerWrapper: React.FC<MarkerWrapperProps> = ({
  coordinate,
  title,
  pinColor,
}) => {
  if (Platform.OS === 'web' || !Marker) {
    return null;
  }

  return <Marker coordinate={coordinate} title={title} pinColor={pinColor} />;
};

const styles = StyleSheet.create({
  webMapPlaceholder: {
    backgroundColor: Colors.lightGray,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 12,
  },
  webMapText: {
    fontSize: 24,
    color: Colors.text,
    marginBottom: 8,
  },
  webMapSubtext: {
    fontSize: 12,
    color: Colors.textLight,
  },
});
