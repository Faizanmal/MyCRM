import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _darkMode = false;
  bool _notifications = true;
  bool _emailNotifications = true;
  bool _pushNotifications = true;
  bool _biometricAuth = false;
  String _language = 'English';
  String _timezone = 'UTC';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.grey.shade700, Colors.grey.shade600],
            ),
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildProfileSection(),
          const SizedBox(height: 24),
          _buildAppearanceSection(),
          const SizedBox(height: 24),
          _buildNotificationsSection(),
          const SizedBox(height: 24),
          _buildSecuritySection(),
          const SizedBox(height: 24),
          _buildLocalizationSection(),
          const SizedBox(height: 24),
          _buildDataSection(),
          const SizedBox(height: 24),
          _buildAboutSection(),
          const SizedBox(height: 24),
          _buildLogoutButton(),
        ],
      ),
    );
  }

  Widget _buildProfileSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Profile',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: CircleAvatar(
                radius: 30,
                backgroundColor: Colors.blue.shade100,
                child: const Icon(Icons.person, size: 32, color: Colors.blue),
              ),
              title: const Text('John Doe'),
              subtitle: const Text('john.doe@company.com'),
              trailing: IconButton(
                icon: const Icon(Icons.edit),
                onPressed: () => _showEditProfileDialog(),
              ),
            ),
            const SizedBox(height: 8),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.business),
              title: const Text('Company'),
              subtitle: const Text('Acme Corporation'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.work),
              title: const Text('Role'),
              subtitle: const Text('Sales Manager'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppearanceSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Appearance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Dark Mode'),
              subtitle: const Text('Enable dark theme'),
              secondary: const Icon(Icons.dark_mode),
              value: _darkMode,
              onChanged: (value) {
                setState(() => _darkMode = value);
              },
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.color_lens),
              title: const Text('Theme Color'),
              subtitle: const Text('Blue'),
              trailing: Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.grey.shade300),
                ),
              ),
              onTap: () => _showThemeColorPicker(),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.format_size),
              title: const Text('Font Size'),
              subtitle: const Text('Medium'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Notifications',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Enable Notifications'),
              subtitle: const Text('Receive all notifications'),
              secondary: const Icon(Icons.notifications),
              value: _notifications,
              onChanged: (value) {
                setState(() => _notifications = value);
              },
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Email Notifications'),
              subtitle: const Text('Receive email updates'),
              secondary: const Icon(Icons.email),
              value: _emailNotifications,
              onChanged: _notifications ? (value) {
                setState(() => _emailNotifications = value);
              } : null,
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Push Notifications'),
              subtitle: const Text('Receive push notifications'),
              secondary: const Icon(Icons.phone_android),
              value: _pushNotifications,
              onChanged: _notifications ? (value) {
                setState(() => _pushNotifications = value);
              } : null,
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.schedule),
              title: const Text('Quiet Hours'),
              subtitle: const Text('10:00 PM - 7:00 AM'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSecuritySection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Security',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.lock),
              title: const Text('Change Password'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showChangePasswordDialog(),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Biometric Authentication'),
              subtitle: const Text('Use fingerprint or face ID'),
              secondary: const Icon(Icons.fingerprint),
              value: _biometricAuth,
              onChanged: (value) {
                setState(() => _biometricAuth = value);
              },
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.security),
              title: const Text('Two-Factor Authentication'),
              subtitle: const Text('Enabled'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.devices),
              title: const Text('Active Sessions'),
              subtitle: const Text('3 devices'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showActiveSessions(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocalizationSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Localization',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.language),
              title: const Text('Language'),
              subtitle: Text(_language),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showLanguagePicker(),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.access_time),
              title: const Text('Timezone'),
              subtitle: Text(_timezone),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showTimezonePicker(),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.calendar_today),
              title: const Text('Date Format'),
              subtitle: const Text('MM/DD/YYYY'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.attach_money),
              title: const Text('Currency'),
              subtitle: const Text('USD (\$)'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Data & Privacy',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.download),
              title: const Text('Export Data'),
              subtitle: const Text('Download your data'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showExportDataDialog(),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.sync),
              title: const Text('Sync Settings'),
              subtitle: const Text('Last sync: 2 minutes ago'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.storage),
              title: const Text('Cache'),
              subtitle: const Text('45 MB used'),
              trailing: TextButton(
                onPressed: () => _clearCache(),
                child: const Text('Clear'),
              ),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.privacy_tip),
              title: const Text('Privacy Policy'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(Icons.delete_forever, color: Colors.red.shade700),
              title: Text('Delete Account', style: TextStyle(color: Colors.red.shade700)),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showDeleteAccountDialog(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAboutSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'About',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.info),
              title: const Text('App Version'),
              subtitle: const Text('1.0.0 (Build 100)'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.update),
              title: const Text('Check for Updates'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.help),
              title: const Text('Help & Support'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.feedback),
              title: const Text('Send Feedback'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.description),
              title: const Text('Terms of Service'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLogoutButton() {
    return Card(
      color: Colors.red.shade50,
      child: ListTile(
        leading: Icon(Icons.logout, color: Colors.red.shade700),
        title: Text(
          'Logout',
          style: TextStyle(
            color: Colors.red.shade700,
            fontWeight: FontWeight.bold,
          ),
        ),
        onTap: () => _showLogoutDialog(),
      ),
    );
  }

  void _showEditProfileDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Profile'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: 'Full Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              decoration: const InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showThemeColorPicker() {
    final colors = [
      Colors.blue,
      Colors.indigo,
      Colors.purple,
      Colors.pink,
      Colors.red,
      Colors.orange,
      Colors.amber,
      Colors.green,
      Colors.teal,
      Colors.cyan,
    ];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Theme Color'),
        content: Wrap(
          spacing: 8,
          runSpacing: 8,
          children: colors.map((color) => InkWell(
            onTap: () => Navigator.pop(context),
            child: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
          )).toList(),
        ),
      ),
    );
  }

  void _showChangePasswordDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Change Password'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: const [
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Current Password',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'New Password',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Confirm New Password',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Change Password'),
          ),
        ],
      ),
    );
  }

  void _showActiveSessions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Active Sessions',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildSessionTile('iPhone 15 Pro', 'Current device', true),
            _buildSessionTile('MacBook Pro', 'Last active: 2 hours ago', false),
            _buildSessionTile('Windows PC', 'Last active: 1 day ago', false),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {},
                style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                child: const Text('Log Out All Other Devices'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionTile(String device, String status, bool isCurrent) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.devices),
      title: Text(device),
      subtitle: Text(status),
      trailing: isCurrent
          ? Chip(
              label: const Text('Current'),
              backgroundColor: Colors.green.shade100,
              labelStyle: const TextStyle(color: Colors.green),
            )
          : IconButton(
              icon: const Icon(Icons.logout),
              onPressed: () {},
            ),
    );
  }

  void _showLanguagePicker() {
    final languages = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese'];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Language'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: languages.map((lang) => ListTile(
            title: Text(lang),
            trailing: _language == lang ? const Icon(Icons.check, color: Colors.blue) : null,
            onTap: () {
              setState(() => _language = lang);
              Navigator.pop(context);
            },
          )).toList(),
        ),
      ),
    );
  }

  void _showTimezonePicker() {
    final timezones = ['UTC', 'EST', 'PST', 'GMT', 'CET', 'IST'];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Timezone'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: timezones.map((tz) => ListTile(
            title: Text(tz),
            trailing: _timezone == tz ? const Icon(Icons.check, color: Colors.blue) : null,
            onTap: () {
              setState(() => _timezone = tz);
              Navigator.pop(context);
            },
          )).toList(),
        ),
      ),
    );
  }

  void _showExportDataDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Export Data'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Select data to export:'),
            const SizedBox(height: 16),
            CheckboxListTile(
              value: true,
              onChanged: (v) {},
              title: const Text('Contacts'),
              controlAffinity: ListTileControlAffinity.leading,
            ),
            CheckboxListTile(
              value: true,
              onChanged: (v) {},
              title: const Text('Leads'),
              controlAffinity: ListTileControlAffinity.leading,
            ),
            CheckboxListTile(
              value: true,
              onChanged: (v) {},
              title: const Text('Opportunities'),
              controlAffinity: ListTileControlAffinity.leading,
            ),
            CheckboxListTile(
              value: false,
              onChanged: (v) {},
              title: const Text('Tasks'),
              controlAffinity: ListTileControlAffinity.leading,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Export started. You will receive an email when ready.')),
              );
            },
            child: const Text('Export'),
          ),
        ],
      ),
    );
  }

  void _clearCache() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Cache'),
        content: const Text('This will clear all cached data. Are you sure?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Cache cleared successfully')),
              );
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _showDeleteAccountDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Delete Account', style: TextStyle(color: Colors.red.shade700)),
        content: const Text(
          'This action cannot be undone. All your data will be permanently deleted. '
          'Are you absolutely sure you want to delete your account?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete Account'),
          ),
        ],
      ),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<AuthProvider>().logout();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}
