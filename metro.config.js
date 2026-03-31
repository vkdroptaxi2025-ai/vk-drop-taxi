// metro.config.js
const { getDefaultConfig } = require("expo/metro-config");
const path = require('path');
const { FileStore } = require('metro-cache');

const config = getDefaultConfig(__dirname);

// Use a stable on-disk store (shared across web/android)
const root = process.env.METRO_CACHE_ROOT || path.join(__dirname, '.metro-cache');
config.cacheStores = [
  new FileStore({ root: path.join(root, 'cache') }),
];

// Resolve native modules to empty mocks on web
config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (platform === 'web') {
    if (moduleName === 'react-native-maps') {
      return {
        filePath: path.join(__dirname, 'web-mocks/react-native-maps.js'),
        type: 'sourceFile',
      };
    }
    if (moduleName === 'expo-image-picker') {
      return {
        filePath: path.join(__dirname, 'web-mocks/expo-image-picker.js'),
        type: 'sourceFile',
      };
    }
    if (moduleName === 'expo-location') {
      return {
        filePath: path.join(__dirname, 'web-mocks/expo-location.js'),
        type: 'sourceFile',
      };
    }
  }
  return context.resolveRequest(context, moduleName, platform);
};

// Reduce the number of workers to decrease resource usage
config.maxWorkers = 2;

module.exports = config;
