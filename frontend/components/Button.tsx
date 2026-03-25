import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle, View } from 'react-native';
import { Colors } from '../utils/colors';
import { LinearGradient } from 'expo-linear-gradient';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'gold' | 'green';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
  style,
  textStyle,
  icon,
}) => {
  const isGradient = variant === 'gold' || variant === 'green' || variant === 'primary' || variant === 'secondary';
  
  const getGradientColors = (): [string, string] => {
    switch (variant) {
      case 'gold':
      case 'primary':
        return ['#FFD700', '#FF8C00'];
      case 'green':
      case 'secondary':
        return ['#4CAF50', '#2E7D32'];
      default:
        return ['#FFD700', '#FF8C00'];
    }
  };

  const buttonTextStyle = [
    styles.buttonText,
    (variant === 'primary' || variant === 'gold') && styles.goldText,
    (variant === 'secondary' || variant === 'green') && styles.greenText,
    variant === 'outline' && styles.outlineText,
    textStyle,
  ];

  if (variant === 'outline') {
    return (
      <TouchableOpacity
        style={[
          styles.button,
          styles.outlineButton,
          (disabled || loading) && styles.disabledButton,
          style,
        ]}
        onPress={onPress}
        disabled={disabled || loading}
        activeOpacity={0.7}
      >
        {loading ? (
          <ActivityIndicator color={Colors.gold} />
        ) : (
          <View style={styles.buttonContent}>
            {icon}
            <Text style={buttonTextStyle}>{title}</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      style={[
        styles.buttonWrapper,
        (disabled || loading) && styles.disabledButton,
        style,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={getGradientColors()}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={styles.gradientButton}
      >
        {loading ? (
          <ActivityIndicator color={Colors.black} />
        ) : (
          <View style={styles.buttonContent}>
            {icon}
            <Text style={buttonTextStyle}>{title}</Text>
          </View>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  buttonWrapper: {
    borderRadius: 14,
    overflow: 'hidden',
  },
  button: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 54,
  },
  gradientButton: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 54,
  },
  outlineButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: Colors.gold,
  },
  disabledButton: {
    opacity: 0.5,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  goldText: {
    color: Colors.black,
  },
  greenText: {
    color: Colors.white,
  },
  outlineText: {
    color: Colors.gold,
  },
});
