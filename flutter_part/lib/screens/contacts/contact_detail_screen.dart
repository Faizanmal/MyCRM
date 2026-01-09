import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';
import '../../providers/contacts_provider.dart';
import 'add_contact_screen.dart';

class ContactDetailScreen extends StatefulWidget {
  final Contact contact;
  
  const ContactDetailScreen({super.key, required this.contact});
  
  @override
  State<ContactDetailScreen> createState() => _ContactDetailScreenState();
}

class _ContactDetailScreenState extends State<ContactDetailScreen> {
  late Contact _contact;
  
  @override
  void initState() {
    super.initState();
    _contact = widget.contact;
  }
  
  void _editContact() async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => AddContactScreen(contact: _contact),
      ),
    );

    // Refresh local contact data from provider after return
    if (mounted) {
      final updatedContact = context.read<ContactsProvider>()
          .contacts.firstWhere((c) => c.id == _contact.id, orElse: () => _contact);
      setState(() {
        _contact = updatedContact;
      });
    }
  }
  
  Future<void> _callContact() async {
    if (_contact.phone != null) {
      final uri = Uri.parse('tel:${_contact.phone}');
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
    }
  }
  
  Future<void> _emailContact() async {
    if (_contact.email != null) {
      final uri = Uri.parse('mailto:${_contact.email}');
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
    }
  }
  
  Future<void> _deleteContact() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Contact'),
        content: Text('Are you sure you want to delete ${_contact.fullName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    
    if (confirmed == true && mounted) {
      final success = await context.read<ContactsProvider>().deleteContact(_contact.id!);

      if (mounted) {
        if (success) {
          Navigator.pop(context, true); // Return true to indicate deletion
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Contact deleted'),
              backgroundColor: AppColors.error,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to delete contact'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Contact Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: _editContact,
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'delete') {
                _deleteContact();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, color: AppColors.error),
                    SizedBox(width: 8),
                    Text('Delete', style: TextStyle(color: AppColors.error)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          children: [
            // Avatar and name header
            _buildHeader(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Quick actions
            _buildQuickActions(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Contact Info
            _buildInfoSection(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHeader() {
    return Column(
      children: [
        CircleAvatar(
          radius: 50,
          backgroundColor: AppColors.primary,
          child: Text(
            _contact.initials,
            style: const TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: AppSizes.paddingMd),
        Text(
          _contact.fullName,
          style: const TextStyle(
            fontSize: AppSizes.fontXl,
            fontWeight: FontWeight.bold,
          ),
        ),
        if (_contact.company != null) ...[
          const SizedBox(height: AppSizes.paddingSm),
          Text(
            '${_contact.company}${_contact.position != null ? ' • ${_contact.position}' : ''}',
            style: TextStyle(
              fontSize: AppSizes.fontMd,
              color: AppColors.grey600,
            ),
          ),
        ],
      ],
    );
  }
  
  Widget _buildQuickActions() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (_contact.phone != null)
          _buildActionButton(
            icon: Icons.phone,
            label: 'Call',
            color: AppColors.success,
            onTap: _callContact,
          ),
        const SizedBox(width: AppSizes.paddingMd),
        if (_contact.email != null)
          _buildActionButton(
            icon: Icons.email,
            label: 'Email',
            color: AppColors.primary,
            onTap: _emailContact,
          ),
        const SizedBox(width: AppSizes.paddingMd),
        _buildActionButton(
          icon: Icons.message,
          label: 'Message',
          color: AppColors.info,
          onTap: () {},
        ),
      ],
    );
  }
  
  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppSizes.radiusMd),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSizes.paddingMd,
          vertical: AppSizes.paddingSm,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(AppSizes.radiusMd),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildInfoSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Contact Information',
              style: TextStyle(
                fontSize: AppSizes.fontLg,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppSizes.paddingMd),
            
            _buildInfoRow(Icons.email, 'Email', _contact.email ?? 'Not set'),
            _buildInfoRow(Icons.phone, 'Phone', _contact.phone ?? 'Not set'),
            _buildInfoRow(Icons.business, 'Company', _contact.company ?? 'Not set'),
            _buildInfoRow(Icons.work, 'Position', _contact.position ?? 'Not set'),
            _buildInfoRow(Icons.label, 'Status', _contact.status ?? 'Unknown'),
            if (_contact.notes != null)
              _buildInfoRow(Icons.note, 'Notes', _contact.notes!),
          ],
        ),
      ),
    );
  }
  
  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingSm),
      child: Row(
        children: [
          Icon(icon, color: AppColors.grey500, size: 20),
          const SizedBox(width: AppSizes.paddingSm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: AppSizes.fontSm,
                    color: AppColors.grey500,
                  ),
                ),
                Text(
                  value,
                  style: const TextStyle(fontSize: AppSizes.fontMd),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
