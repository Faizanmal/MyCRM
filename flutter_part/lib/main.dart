import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'core/utils/api_client.dart';
import 'providers/auth_provider.dart';
import 'providers/contacts_provider.dart';
import 'providers/leads_provider.dart';
import 'providers/enterprise_providers.dart';
import 'screens/auth/login_screen.dart';
import 'screens/home/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Firebase.initializeApp();
  } catch (e) {
    debugPrint('Firebase init failed: $e');
  }
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiClient = ApiClient();
    
    return MultiProvider(
      providers: [
        // Core providers
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ContactsProvider()),
        ChangeNotifierProvider(create: (_) => LeadsProvider()),
        
        // Enterprise providers
        ChangeNotifierProvider(create: (_) => CustomerSuccessProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => GDPRProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => WhiteLabelProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => AIChatbotProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => DataEnrichmentProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => LeadRoutingProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => VoiceIntelligenceProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => EmailSequenceProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => MarketplaceProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => SocialInboxProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => ESGProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => ConversationIntelligenceProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => DocumentManagementProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => RealtimeCollaborationProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => CustomerPortalProvider(apiClient)),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, _) {
          return MaterialApp(
            title: AppConstants.appName,
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: ThemeMode.system,
            home: _getInitialScreen(authProvider),
          );
        },
      ),
    );
  }
  
  Widget _getInitialScreen(AuthProvider authProvider) {
    if (authProvider.isLoading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }
    
    if (authProvider.isAuthenticated) {
      return const HomeScreen();
    }
    
    return const LoginScreen();
  }
}
