import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class SecurityScreen extends StatefulWidget {
  const SecurityScreen({super.key});

  @override
  State<SecurityScreen> createState() => _SecurityScreenState();
}

class _SecurityScreenState extends State<SecurityScreen> {
  bool _twoFactorEnabled = true;
  bool _sessionTimeout = true;
  bool _ipWhitelisting = false;
  bool _auditLogging = true;
  int _sessionTimeoutMinutes = 30;
  int _passwordExpiryDays = 90;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Security Settings'),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.red.shade700, Colors.orange.shade600],
            ),
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildSecurityOverview(),
          const SizedBox(height: 24),
          _buildAuthenticationSection(),
          const SizedBox(height: 24),
          _buildSessionSection(),
          const SizedBox(height: 24),
          _buildAccessControlSection(),
          const SizedBox(height: 24),
          _buildAuditSection(),
          const SizedBox(height: 24),
          _buildPasswordPolicySection(),
          const SizedBox(height: 24),
          _buildDataProtectionSection(),
        ],
      ),
    );
  }

  Widget _buildSecurityOverview() {
    return Card(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.green.shade700, Colors.teal.shade500],
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.shield, color: Colors.white, size: 40),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Security Score',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const Text(
                    '85/100',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Text(
                    'Good - 2 recommendations',
                    style: TextStyle(color: Colors.white70),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAuthenticationSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lock, color: Colors.blue.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Authentication',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Two-Factor Authentication'),
              subtitle: const Text('Require 2FA for all users'),
              value: _twoFactorEnabled,
              onChanged: (value) {
                setState(() => _twoFactorEnabled = value);
              },
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('2FA Methods'),
              subtitle: const Text('Authenticator App, SMS, Email'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _show2FAMethodsDialog(),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('SSO Configuration'),
              subtitle: const Text('SAML 2.0, OAuth 2.0'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showSSOConfigDialog(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.timer, color: Colors.orange.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Session Management',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Session Timeout'),
              subtitle: Text('Automatically logout after $_sessionTimeoutMinutes minutes'),
              value: _sessionTimeout,
              onChanged: (value) {
                setState(() => _sessionTimeout = value);
              },
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Timeout Duration'),
              trailing: DropdownButton<int>(
                value: _sessionTimeoutMinutes,
                items: [15, 30, 60, 120].map((minutes) => DropdownMenuItem(
                  value: minutes,
                  child: Text('$minutes min'),
                )).toList(),
                onChanged: (value) {
                  if (value != null) setState(() => _sessionTimeoutMinutes = value);
                },
              ),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Active Sessions'),
              subtitle: const Text('View and manage active sessions'),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text('3 devices'),
                  ),
                  const SizedBox(width: 8),
                  const Icon(Icons.chevron_right),
                ],
              ),
              onTap: () => _showActiveSessionsDialog(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccessControlSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.admin_panel_settings, color: Colors.purple.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Access Control',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('IP Whitelisting'),
              subtitle: const Text('Restrict access to specific IP addresses'),
              value: _ipWhitelisting,
              onChanged: (value) {
                setState(() => _ipWhitelisting = value);
              },
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Role-Based Access'),
              subtitle: const Text('Configure user roles and permissions'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('API Access'),
              subtitle: const Text('Manage API keys and tokens'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAuditSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.history, color: Colors.teal.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Audit & Compliance',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Audit Logging'),
              subtitle: const Text('Log all user activities'),
              value: _auditLogging,
              onChanged: (value) {
                setState(() => _auditLogging = value);
              },
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('View Audit Logs'),
              subtitle: const Text('Last 30 days of activity'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Export Logs'),
              subtitle: const Text('Download audit logs as CSV'),
              trailing: const Icon(Icons.download),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPasswordPolicySection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.password, color: Colors.red.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Password Policy',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Minimum Length'),
              trailing: const Text('12 characters'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Complexity Requirements'),
              subtitle: const Text('Uppercase, lowercase, numbers, symbols'),
              trailing: const Icon(Icons.check_circle, color: Colors.green),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Password Expiry'),
              trailing: DropdownButton<int>(
                value: _passwordExpiryDays,
                items: [30, 60, 90, 180, 365].map((days) => DropdownMenuItem(
                  value: days,
                  child: Text('$days days'),
                )).toList(),
                onChanged: (value) {
                  if (value != null) setState(() => _passwordExpiryDays = value);
                },
              ),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Password History'),
              subtitle: const Text('Prevent reuse of last 5 passwords'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataProtectionSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.security, color: Colors.indigo.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Data Protection',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.enhanced_encryption, color: Colors.green),
              title: const Text('Encryption at Rest'),
              subtitle: const Text('AES-256 encryption enabled'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.lock, color: Colors.green),
              title: const Text('Encryption in Transit'),
              subtitle: const Text('TLS 1.3 enabled'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.backup, color: Colors.blue),
              title: const Text('Data Backup'),
              subtitle: const Text('Daily backups with 30-day retention'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Data Retention Policy'),
              subtitle: const Text('Configure retention periods'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  void _show2FAMethodsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('2FA Methods'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CheckboxListTile(
              value: true,
              onChanged: (v) {},
              title: const Text('Authenticator App'),
              subtitle: const Text('Google Authenticator, Authy, etc.'),
            ),
            CheckboxListTile(
              value: true,
              onChanged: (v) {},
              title: const Text('SMS'),
              subtitle: const Text('Text message verification'),
            ),
            CheckboxListTile(
              value: false,
              onChanged: (v) {},
              title: const Text('Email'),
              subtitle: const Text('Email verification code'),
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

  void _showSSOConfigDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('SSO Configuration'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.cloud),
              title: const Text('SAML 2.0'),
              subtitle: const Text('Not configured'),
              trailing: TextButton(
                onPressed: () {},
                child: const Text('Setup'),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.cloud),
              title: const Text('OAuth 2.0'),
              subtitle: const Text('Google, Microsoft'),
              trailing: TextButton(
                onPressed: () {},
                child: const Text('Edit'),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showActiveSessionsDialog() {
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
            _buildSessionItem('iPhone 15 Pro', 'Current session', 'San Francisco, US', true),
            _buildSessionItem('MacBook Pro', '2 hours ago', 'San Francisco, US', false),
            _buildSessionItem('Chrome on Windows', '1 day ago', 'New York, US', false),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {},
                style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                child: const Text('Terminate All Other Sessions'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionItem(String device, String time, String location, bool isCurrent) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.devices),
      title: Text(device),
      subtitle: Text('$time • $location'),
      trailing: isCurrent
          ? Chip(
              label: const Text('Current'),
              backgroundColor: Colors.green.shade100,
              labelStyle: const TextStyle(color: Colors.green, fontSize: 11),
            )
          : IconButton(
              icon: const Icon(Icons.close, color: Colors.red),
              onPressed: () {},
            ),
    );
  }
}
