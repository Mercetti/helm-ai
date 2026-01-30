"""
Mobile App (React Native/Flutter) for Helm AI
==============================================

This module provides comprehensive mobile app capabilities:
- Cross-platform mobile app development
- React Native components and screens
- Flutter widgets and navigation
- Mobile-specific features (camera, GPS, notifications)
- Offline data synchronization
- Mobile analytics and tracking
- Push notification integration
- Mobile security and authentication
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("mobile_app")


class Platform(str, Enum):
    """Mobile platforms"""
    IOS = "ios"
    ANDROID = "android"
    BOTH = "both"


class ScreenType(str, Enum):
    """Mobile screen types"""
    HOME = "home"
    DASHBOARD = "dashboard"
    ANALYTICS = "analytics"
    PROFILE = "profile"
    SETTINGS = "settings"
    LOGIN = "login"
    REGISTER = "register"


class NotificationType(str, Enum):
    """Push notification types"""
    ALERT = "alert"
    UPDATE = "update"
    REMINDER = "reminder"
    MARKETING = "marketing"
    SECURITY = "security"


@dataclass
class MobileScreen:
    """Mobile screen configuration"""
    id: str
    name: str
    type: ScreenType
    component_path: str
    navigation_path: str
    requires_auth: bool = True
    platform: Platform = Platform.BOTH
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MobileFeature:
    """Mobile feature configuration"""
    id: str
    name: str
    description: str
    platform: Platform
    permissions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PushNotification:
    """Push notification configuration"""
    id: str
    title: str
    body: str
    type: NotificationType
    data: Dict[str, Any] = field(default_factory=dict)
    target_users: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class ReactNativeComponents:
    """React Native component templates"""
    
    @staticmethod
    def create_app_component() -> str:
        """Create main App component"""
        return '''
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';

import store, { persistor } from './src/store';
import { ThemeProvider } from './src/theme';
import { AuthProvider } from './src/auth';
import { NotificationProvider } from './src/notifications';
import { AnalyticsProvider } from './src/analytics';

import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createNativeStackNavigator();

const App = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ThemeProvider>
          <AuthProvider>
            <NotificationProvider>
              <AnalyticsProvider>
                <NavigationContainer>
                  <Stack.Navigator screenOptions={{ headerShown: false }}>
                    <Stack.Screen name="Login" component={LoginScreen} />
                    <Stack.Screen name="Home" component={HomeScreen} />
                    <Stack.Screen name="Dashboard" component={DashboardScreen} />
                    <Stack.Screen name="Analytics" component={AnalyticsScreen} />
                    <Stack.Screen name="Profile" component={ProfileScreen} />
                    <Stack.Screen name="Settings" component={SettingsScreen} />
                  </Stack.Navigator>
                </NavigationContainer>
              </AnalyticsProvider>
            </NotificationProvider>
          </AuthProvider>
        </ThemeProvider>
      </PersistGate>
    </Provider>
  );
};

export default App;
'''
    
    @staticmethod
    def create_home_screen() -> str:
        """Create Home screen component"""
        return '''
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '@react-navigation/native';

import { fetchDashboardData } from '../store/slices/dashboardSlice';
import { trackScreenView } from '../services/analytics';
import Card from '../components/Card';
import MetricCard from '../components/MetricCard';
import QuickActions from '../components/QuickActions';
import RecentActivity from '../components/RecentActivity';

const HomeScreen = ({ navigation }) => {
  const dispatch = useDispatch();
  const theme = useTheme();
  const { user } = useSelector(state => state.auth);
  const { data, loading, error } = useSelector(state => state.dashboard);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
    trackScreenView('Home');
  }, []);

  const loadData = async () => {
    try {
      await dispatch(fetchDashboardData());
    } catch (error) {
      Alert.alert('Error', 'Failed to load dashboard data');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const navigateToScreen = (screen) => {
    navigation.navigate(screen);
  };

  if (loading && !data) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={[styles.greeting, { color: theme.colors.text }]}>
          Welcome back, {user?.firstName}!
        </Text>
        <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
          Here\'s your overview for today
        </Text>
      </View>

      <View style={styles.metricsGrid}>
        <MetricCard
          title="Total Revenue"
          value={data?.totalRevenue || 0}
          change={data?.revenueChange || 0}
          icon="trending-up"
          color="#4CAF50"
          onPress={() => navigateToScreen('Analytics')}
        />
        <MetricCard
          title="Active Users"
          value={data?.activeUsers || 0}
          change={data?.usersChange || 0}
          icon="people"
          color="#2196F3"
          onPress={() => navigateToScreen('Analytics')}
        />
        <MetricCard
          title="Conversion Rate"
          value={`${data?.conversionRate || 0}%`}
          change={data?.conversionChange || 0}
          icon="percent"
          color="#FF9800"
          onPress={() => navigateToScreen('Analytics')}
        />
        <MetricCard
          title="Avg. Session"
          value={`${data?.avgSession || 0}m`}
          change={data?.sessionChange || 0}
          icon="timer"
          color="#9C27B0"
          onPress={() => navigateToScreen('Analytics')}
        />
      </View>

      <Card title="Quick Actions" style={styles.card}>
        <QuickActions navigation={navigation} />
      </Card>

      <Card title="Recent Activity" style={styles.card}>
        <RecentActivity activities={data?.recentActivity || []} />
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    fontWeight: '500',
  },
  header: {
    padding: 20,
    paddingTop: 40,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    justifyContent: 'space-between',
  },
  card: {
    margin: 16,
    marginTop: 0,
  },
});

export default HomeScreen;
'''
    
    @staticmethod
    def create_analytics_screen() -> str:
        """Create Analytics screen component"""
        return '''
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '@react-navigation/native';

import { fetchAnalyticsData } from '../store/slices/analyticsSlice';
import { trackScreenView } from '../services/analytics';
import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';
import PieChart from '../components/charts/PieChart';
import DateRangePicker from '../components/DateRangePicker';
import MetricCard from '../components/MetricCard';
import Card from '../components/Card';

const { width } = Dimensions.get('window');

const AnalyticsScreen = ({ navigation }) => {
  const dispatch = useDispatch();
  const theme = useTheme();
  const { data, loading, error } = useSelector(state => state.analytics);
  const [dateRange, setDateRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');

  useEffect(() => {
    loadData();
    trackScreenView('Analytics');
  }, [dateRange]);

  const loadData = async () => {
    try {
      await dispatch(fetchAnalyticsData({ dateRange }));
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    }
  };

  const metrics = [
    { key: 'revenue', label: 'Revenue', icon: 'attach-money' },
    { key: 'users', label: 'Users', icon: 'people' },
    { key: 'sessions', label: 'Sessions', icon: 'touch-app' },
    { key: 'conversions', label: 'Conversions', icon: 'shopping-cart' },
  ];

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: theme.colors.text }]}>Analytics</Text>
        <DateRangePicker
          selected={dateRange}
          onSelect={setDateRange}
          style={styles.datePicker}
        />
      </View>

      <View style={styles.metricsSelector}>
        {metrics.map((metric) => (
          <TouchableOpacity
            key={metric.key}
            style={[
              styles.metricButton,
              selectedMetric === metric.key && styles.selectedMetric,
              { borderColor: theme.colors.border },
            ]}
            onPress={() => setSelectedMetric(metric.key)}
          >
            <Icon
              name={metric.icon}
              size={20}
              color={
                selectedMetric === metric.key
                  ? theme.colors.primary
                  : theme.colors.textSecondary
              }
            />
            <Text
              style={[
                styles.metricButtonText,
                selectedMetric === metric.key && styles.selectedMetricText,
                { color: theme.colors.text },
              ]}
            >
              {metric.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.overviewCards}>
        <MetricCard
          title="Total Revenue"
          value={data?.totalRevenue || 0}
          change={data?.revenueChange || 0}
          icon="trending-up"
          color="#4CAF50"
          compact
        />
        <MetricCard
          title="Growth Rate"
          value={`${data?.growthRate || 0}%`}
          change={data?.growthChange || 0}
          icon="trending-up"
          color="#2196F3"
          compact
        />
      </View>

      <Card title="Revenue Trend" style={styles.chartCard}>
        <LineChart
          data={data?.revenueTrend || []}
          height={200}
          color={theme.colors.primary}
        />
      </Card>

      <Card title="User Activity" style={styles.chartCard}>
        <BarChart
          data={data?.userActivity || []}
          height={200}
          color={theme.colors.secondary}
        />
      </Card>

      <Card title="Device Distribution" style={styles.chartCard}>
        <PieChart
          data={data?.deviceDistribution || []}
          height={200}
        />
      </Card>

      <Card title="Top Pages" style={styles.chartCard}>
        {data?.topPages?.map((page, index) => (
          <View key={index} style={styles.pageRow}>
            <Text style={[styles.pageName, { color: theme.colors.text }]}>
              {page.name}
            </Text>
            <Text style={[styles.pageViews, { color: theme.colors.textSecondary }]}>
              {page.views} views
            </Text>
          </View>
        ))}
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  datePicker: {
    flex: 1,
    marginLeft: 16,
  },
  metricsSelector: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  metricButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    marginHorizontal: 4,
    borderRadius: 8,
    borderWidth: 1,
  },
  selectedMetric: {
    backgroundColor: '#E3F2FD',
  },
  selectedMetricText: {
    fontWeight: '600',
  },
  metricButtonText: {
    marginLeft: 4,
    fontSize: 12,
  },
  overviewCards: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  chartCard: {
    margin: 16,
    marginTop: 0,
  },
  pageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  pageName: {
    fontSize: 14,
  },
  pageViews: {
    fontSize: 14,
    fontWeight: '500',
  },
});

export default AnalyticsScreen;
'''
    
    @staticmethod
    def create_package_json() -> str:
        """Create package.json for React Native"""
        return '''
{
  "name": "helm-ai-mobile",
  "version": "1.0.0",
  "description": "Helm AI Mobile Application",
  "main": "index.js",
  "scripts": {
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "start": "react-native start",
    "test": "jest",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "build:android": "cd android && ./gradlew assembleRelease",
    "build:ios": "xcodebuild -workspace ios/HelmAI.xcworkspace -scheme HelmAI -configuration Release -destination generic/platform=iOS -archivePath ios/build/HelmAI.xcarchive archive"
  },
  "dependencies": {
    "@react-native-async-storage/async-storage": "^1.19.3",
    "@react-native-community/netinfo": "^9.4.1",
    "@react-native-firebase/app": "^18.6.1",
    "@react-native-firebase/messaging": "^18.6.1",
    "@react-native-firebase/analytics": "^18.6.1",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/native-stack": "^6.9.17",
    "@reduxjs/toolkit": "^1.9.7",
    "react": "18.2.0",
    "react-native": "0.72.6",
    "react-native-chart-kit": "^6.12.0",
    "react-native-device-info": "^10.11.0",
    "react-native-gesture-handler": "^2.13.4",
    "react-native-permissions": "^3.9.3",
    "react-native-reanimated": "^3.5.4",
    "react-native-safe-area-context": "^4.7.4",
    "react-native-screens": "^3.27.0",
    "react-native-svg": "^13.14.0",
    "react-native-vector-icons": "^10.0.2",
    "react-redux": "^8.1.3",
    "redux": "^4.2.1",
    "redux-persist": "^6.0.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@babel/preset-env": "^7.20.0",
    "@babel/runtime": "^7.20.0",
    "@react-native/eslint-config": "^0.72.2",
    "@react-native/metro-config": "^0.72.11",
    "@tsconfig/react-native": "^3.0.0",
    "@types/react": "^18.0.24",
    "@types/react-test-renderer": "^18.0.0",
    "babel-jest": "^29.2.1",
    "eslint": "^8.19.0",
    "jest": "^29.2.1",
    "metro-react-native-babel-preset": "0.76.8",
    "prettier": "^2.4.1",
    "react-test-renderer": "18.2.0",
    "typescript": "4.8.4"
  },
  "engines": {
    "node": ">=16"
  }
}
'''


class FlutterComponents:
    """Flutter widget templates"""
    
    @staticmethod
    def create_main_dart() -> str:
        """Create main.dart file"""
        return '''
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_analytics/firebase_analytics.dart';

import 'app/app.dart';
import 'app/bloc_observer.dart';
import 'core/theme/app_theme.dart';
import 'core/services/notification_service.dart';
import 'core/services/analytics_service.dart';
import 'core/services/storage_service.dart';
import 'features/auth/bloc/auth_bloc.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await Firebase.initializeApp();
  
  // Configure system UI
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
  
  // Initialize services
  await StorageService.init();
  await NotificationService.init();
  await AnalyticsService.init();
  
  // Set up BLoC observer
  Bloc.observer = AppBlocObserver();
  
  runApp(HelmAIApp());
}
'''
    
    @staticmethod
    def create_app_widget() -> str:
        """Create main app widget"""
        return '''
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'core/theme/app_theme.dart';
import 'core/services/notification_service.dart';
import 'core/routes/app_router.dart';
import 'features/auth/bloc/auth_bloc.dart';
import 'features/auth/presentation/screens/splash_screen.dart';
import 'features/analytics/presentation/bloc/analytics_bloc.dart';
import 'features/dashboard/presentation/bloc/dashboard_bloc.dart';

class HelmAIApp extends StatefulWidget {
  const HelmAIApp({Key? key}) : super(key: key);

  @override
  State<HelmAIApp> createState() => _HelmAIAppState();
}

class _HelmAIAppState extends State<HelmAIApp> {
  final AppRouter _appRouter = AppRouter();
  
  @override
  void initState() {
    super.initState();
    _setupFirebaseMessaging();
  }
  
  void _setupFirebaseMessaging() {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      NotificationService.showNotification(message);
    });
    
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      // Handle notification tap
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (context) => AuthBloc()),
        BlocProvider(create: (context) => DashboardBloc()),
        BlocProvider(create: (context) => AnalyticsBloc()),
      ],
      child: MaterialApp.router(
        title: 'Helm AI',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        routerConfig: _appRouter.config(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
'''
    
    @staticmethod
    def create_home_screen() -> str:
        """Create Home screen widget"""
        return '''
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

import '../../../../core/widgets/metric_card.dart';
import '../../../../core/widgets/quick_actions.dart';
import '../../../../core/widgets/recent_activity.dart';
import '../../../../core/widgets/loading_widget.dart';
import '../../../../core/widgets/error_widget.dart';
import '../bloc/home_bloc.dart';
import '../bloc/home_event.dart';
import '../bloc/home_state.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    context.read<HomeBloc>().add(LoadHomeData());
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocBuilder<HomeBloc, HomeState>(
        builder: (context, state) {
          if (state is HomeLoading) {
            return const LoadingWidget();
          }
          
          if (state is HomeError) {
            return CustomErrorWidget(
              message: state.message,
              onRetry: () => context.read<HomeBloc>().add(LoadHomeData()),
            );
          }
          
          if (state is HomeLoaded) {
            return _buildContent(state);
          }
          
          return const SizedBox.shrink();
        },
      ),
    );
  }
  
  Widget _buildContent(HomeLoaded state) {
    final user = state.user;
    final data = state.dashboardData;
    
    return RefreshIndicator(
      onRefresh: () async {
        context.read<HomeBloc>().add(LoadHomeData());
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 40),
            
            // Welcome Section
            Text(
              'Welcome back, ${user?.firstName ?? 'User'}!',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Here\'s your overview for today',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Theme.of(context).textTheme.bodyLarge?.color?.withOpacity(0.7),
              ),
            ),
            const SizedBox(height: 24),
            
            // Metrics Grid
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.5,
              children: [
                MetricCard(
                  title: 'Total Revenue',
                  value: '\$${(data.totalRevenue ?? 0).toStringAsFixed(2)}',
                  change: data.revenueChange ?? 0,
                  icon: FontAwesomeIcons.dollarSign,
                  color: Colors.green,
                  onTap: () => _navigateToAnalytics(),
                ),
                MetricCard(
                  title: 'Active Users',
                  value: (data.activeUsers ?? 0).toString(),
                  change: data.usersChange ?? 0,
                  icon: FontAwesomeIcons.users,
                  color: Colors.blue,
                  onTap: () => _navigateToAnalytics(),
                ),
                MetricCard(
                  title: 'Conversion Rate',
                  value: '${(data.conversionRate ?? 0).toStringAsFixed(1)}%',
                  change: data.conversionChange ?? 0,
                  icon: FontAwesomeIcons.chartLine,
                  color: Colors.orange,
                  onTap: () => _navigateToAnalytics(),
                ),
                MetricCard(
                  title: 'Avg. Session',
                  value: '${(data.avgSession ?? 0).toStringAsFixed(1)}m',
                  change: data.sessionChange ?? 0,
                  icon: FontAwesomeIcons.clock,
                  color: Colors.purple,
                  onTap: () => _navigateToAnalytics(),
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Quick Actions
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Quick Actions',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    QuickActions(
                      onActionSelected: _handleQuickAction,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // Recent Activity
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Recent Activity',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    RecentActivity(
                      activities: data.recentActivity ?? [],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  void _navigateToAnalytics() {
    // Navigate to analytics screen
  }
  
  void _handleQuickAction(String action) {
    // Handle quick action
  }
}
'''
    
    @staticmethod
    def create_pubspec_yaml() -> str:
        """Create pubspec.yaml for Flutter"""
        return '''
name: helm_ai_mobile
description: Helm AI Mobile Application
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  flutter_bloc: ^8.1.3
  equatable: ^2.0.5
  dio: ^5.3.2
  shared_preferences: ^2.2.2
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.9
  firebase_analytics: ^10.7.4
  firebase_auth: ^4.16.0
  cloud_firestore: ^4.14.0
  go_router: ^12.1.3
  font_awesome_flutter: ^10.6.0
  charts_flutter: ^0.12.0
  fl_chart: ^0.63.0
  permission_handler: ^11.0.1
  device_info_plus: ^9.1.1
  package_info_plus: ^4.2.0
  connectivity_plus: ^5.0.2
  image_picker: ^1.0.4
  cached_network_image: ^3.3.0
  shimmer: ^3.0.0
  lottie: ^2.7.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  build_runner: ^2.4.7
  mockito: ^5.4.2

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/animations/
    - assets/icons/
  
  fonts:
    - family: Inter
      fonts:
        - asset: assets/fonts/Inter-Regular.ttf
        - asset: assets/fonts/Inter-Medium.ttf
          weight: 500
        - asset: assets/fonts/Inter-SemiBold.ttf
          weight: 600
        - asset: assets/fonts/Inter-Bold.ttf
          weight: 700
'''


class MobileAppGenerator:
    """Mobile app generator and manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.screens: Dict[str, MobileScreen] = {}
        self.features: Dict[str, MobileFeature] = {}
        self.notifications: Dict[str, PushNotification] = {}
        
        logger.info("Mobile App Generator initialized")
    
    def create_react_native_app(self, app_name: str, output_path: str) -> bool:
        """Create React Native app structure"""
        try:
            # Create directory structure
            app_path = Path(output_path) / app_name
            app_path.mkdir(parents=True, exist_ok=True)
            
            # Create main directories
            directories = [
                'src',
                'src/components',
                'src/screens',
                'src/navigation',
                'src/store',
                'src/services',
                'src/theme',
                'src/utils',
                'src/assets',
                'android',
                'ios',
            ]
            
            for directory in directories:
                (app_path / directory).mkdir(parents=True, exist_ok=True)
            
            # Create main files
            files = {
                'App.tsx': ReactNativeComponents.create_app_component(),
                'package.json': ReactNativeComponents.create_package_json(),
                'src/screens/HomeScreen.tsx': ReactNativeComponents.create_home_screen(),
                'src/screens/AnalyticsScreen.tsx': ReactNativeComponents.create_analytics_screen(),
            }
            
            for file_path, content in files.items():
                (app_path / file_path).write_text(content)
            
            logger.info(f"React Native app created at {app_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create React Native app: {e}")
            return False
    
    def create_flutter_app(self, app_name: str, output_path: str) -> bool:
        """Create Flutter app structure"""
        try:
            # Create directory structure
            app_path = Path(output_path) / app_name
            app_path.mkdir(parents=True, exist_ok=True)
            
            # Create main directories
            directories = [
                'lib',
                'lib/app',
                'lib/core',
                'lib/core/theme',
                'lib/core/services',
                'lib/core/widgets',
                'lib/core/utils',
                'lib/features',
                'lib/features/auth',
                'lib/features/analytics',
                'lib/features/dashboard',
                'assets',
                'assets/images',
                'assets/animations',
                'assets/fonts',
                'android',
                'ios',
            ]
            
            for directory in directories:
                (app_path / directory).mkdir(parents=True, exist_ok=True)
            
            # Create main files
            files = {
                'lib/main.dart': FlutterComponents.create_main_dart(),
                'lib/app/app.dart': FlutterComponents.create_app_widget(),
                'lib/features/home/presentation/screens/home_screen.dart': FlutterComponents.create_home_screen(),
                'pubspec.yaml': FlutterComponents.create_pubspec_yaml(),
            }
            
            for file_path, content in files.items():
                (app_path / file_path).write_text(content)
            
            logger.info(f"Flutter app created at {app_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Flutter app: {e}")
            return False
    
    def add_screen(self, screen: MobileScreen) -> bool:
        """Add a mobile screen"""
        try:
            self.screens[screen.id] = screen
            logger.info(f"Mobile screen added: {screen.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add screen: {e}")
            return False
    
    def add_feature(self, feature: MobileFeature) -> bool:
        """Add a mobile feature"""
        try:
            self.features[feature.id] = feature
            logger.info(f"Mobile feature added: {feature.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add feature: {e}")
            return False
    
    def create_push_notification(self, notification: PushNotification) -> bool:
        """Create push notification"""
        try:
            self.notifications[notification.id] = notification
            logger.info(f"Push notification created: {notification.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return False
    
    def get_app_metrics(self) -> Dict[str, Any]:
        """Get mobile app metrics"""
        return {
            "total_screens": len(self.screens),
            "total_features": len(self.features),
            "total_notifications": len(self.notifications),
            "supported_platforms": ["ios", "android"],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
MOBILE_APP_CONFIG = {
    "output_path": "./mobile_apps",
    "react_native": {
        "version": "0.72.6",
        "template": "typescript"
    },
    "flutter": {
        "version": "3.10.0",
        "template": "counter"
    }
}


# Initialize mobile app generator
mobile_app_generator = MobileAppGenerator(MOBILE_APP_CONFIG)

# Export main components
__all__ = [
    'MobileAppGenerator',
    'ReactNativeComponents',
    'FlutterComponents',
    'MobileScreen',
    'MobileFeature',
    'PushNotification',
    'Platform',
    'ScreenType',
    'NotificationType',
    'mobile_app_generator'
]
