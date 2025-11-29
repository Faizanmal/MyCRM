# MyCRM Flutter Application

A complete Flutter CRM (Customer Relationship Management) mobile application with modern UI and comprehensive features.

## Features

### 🔐 Authentication
- Login with username/email and password
- User registration
- Secure token-based authentication
- Auto-refresh tokens
- Persistent login sessions

### 📊 Dashboard
- Real-time statistics overview
- Key performance metrics
- Revenue tracking
- Conversion rate analytics
- Recent activity feed
- Beautiful gradient UI

### 👥 Contacts Management
- Complete contact CRUD operations
- Contact details with company info
- Status tracking (Active, Inactive, Prospect, Customer)
- Search and filter capabilities
- Contact avatar with initials

### 🎯 Leads Management
- Lead tracking and scoring
- Lead sources (Website, Referral, Social Media, etc.)
- Status management (New, Contacted, Qualified, Converted)
- Visual lead scoring (color-coded)
- Lead conversion tracking

### 💼 Opportunities
- Deal pipeline management
- Revenue forecasting
- Stage tracking (Prospecting, Qualification, Proposal, Negotiation, Won/Lost)
- Probability percentage
- Close date tracking
- Amount visualization

### ✅ Tasks
- Task management with priorities
- Status filtering (To Do, In Progress, Completed)
- Priority levels (Low, Medium, High, Urgent)
- Due date tracking
- Overdue task highlighting
- Task completion marking

## Technology Stack

- **Framework**: Flutter 3.8+
- **State Management**: Provider
- **HTTP Client**: Dio
- **Storage**: Shared Preferences, Hive
- **UI Components**: Material 3
- **Charts**: FL Chart, Syncfusion Charts
- **Forms**: Flutter Form Builder
- **Date/Time**: Intl, Timeago

## Project Structure

```
lib/
├── core/
│   ├── constants/
│   │   ├── api_constants.dart      # API endpoints
│   │   └── app_constants.dart      # App-wide constants & colors
│   ├── theme/
│   │   └── app_theme.dart          # Light & dark themes
│   └── utils/
│       ├── api_client.dart         # HTTP client wrapper
│       ├── date_formatter.dart     # Date/time utilities
│       └── validators.dart         # Form validators
├── models/
│   ├── user_model.dart             # User data model
│   └── crm_models.dart             # Contact, Lead, Opportunity, Task models
├── providers/
│   └── auth_provider.dart          # Authentication state management
├── screens/
│   ├── auth/
│   │   └── login_screen.dart       # Login & registration
│   ├── home/
│   │   └── home_screen.dart        # Main navigation
│   ├── dashboard/
│   │   └── dashboard_screen.dart   # Dashboard with stats
│   ├── contacts/
│   │   └── contacts_screen.dart    # Contacts list
│   ├── leads/
│   │   └── leads_screen.dart       # Leads list
│   ├── opportunities/
│   │   └── opportunities_screen.dart
│   └── tasks/
│       └── tasks_screen.dart       # Tasks with filters
├── services/
│   └── auth_service.dart           # Authentication API calls
└── main.dart                       # App entry point
```

## Getting Started

### Prerequisites

- Flutter SDK (3.8.1 or higher)
- Dart SDK
- Android Studio / VS Code with Flutter extensions
- iOS development tools (for iOS builds)

### Installation

1. **Clone the repository**
```bash
cd E:\SaaS_Tools\MyCRM\flutter_part
```

2. **Install dependencies**
```bash
flutter pub get
```

3. **Configure Backend URL**

Edit `lib/core/constants/api_constants.dart`:
```dart
static const String baseUrl = 'http://your-backend-url:8000';
```

For Android Emulator, use:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

For iOS Simulator, use:
```dart
static const String baseUrl = 'http://localhost:8000';
```

For Physical Device, use your machine's IP:
```dart
static const String baseUrl = 'http://192.168.x.x:8000';
```

4. **Run the app**
```bash
flutter run
```

## Configuration

### Theme Customization

Modify colors in `lib/core/constants/app_constants.dart`:
```dart
class AppColors {
  static const Color primary = Color(0xFF3B82F6);
  static const Color secondary = Color(0xFF8B5CF6);
  // ... more colors
}
```

### API Configuration

Update endpoints in `lib/core/constants/api_constants.dart`:
```dart
static const String login = '$apiVersion/auth/login/';
static const String contacts = '$apiVersion/contacts/';
// ... more endpoints
```

## Building for Production

### Android

```bash
flutter build apk --release
```

Or for app bundle:
```bash
flutter build appbundle --release
```

### iOS

```bash
flutter build ios --release
```

## Features Implementation Status

✅ Authentication (Login/Register)
✅ Dashboard with Statistics
✅ Contacts Management
✅ Leads Management
✅ Opportunities Tracking
✅ Tasks Management
✅ Pull-to-Refresh
✅ Dark/Light Theme Support
✅ Responsive Design
✅ Material 3 Design

## Future Enhancements

- [ ] Add/Edit forms for all entities
- [ ] Detail views for contacts, leads, opportunities
- [ ] Search functionality
- [ ] Advanced filtering
- [ ] Offline support with local storage
- [ ] Push notifications
- [ ] File attachments
- [ ] Email integration
- [ ] Calendar integration
- [ ] Export functionality
- [ ] Multi-language support

## API Integration

The app is designed to work with the Django REST API backend. Ensure your backend is running and accessible before using the app.

### Test Credentials

If your backend has test accounts, document them here:
```
Username: testuser
Password: testpass123
```

## Troubleshooting

### Common Issues

1. **Package conflicts**: Run `flutter pub upgrade --major-versions`
2. **Build errors**: Run `flutter clean` then `flutter pub get`
3. **API connection errors**: Check baseUrl configuration
4. **iOS pods issues**: Run `cd ios && pod install`

## Performance Tips

- Use `const` constructors where possible
- Implement pagination for large lists
- Cache images and data locally
- Use `ListView.builder` for long lists
- Profile with Flutter DevTools

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is part of the MyCRM system.

## Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Include Flutter doctor output for environment issues

## Credits

Developed as part of the MyCRM Modern CRM Solution project.
