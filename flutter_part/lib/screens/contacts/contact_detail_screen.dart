import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';

class ContactDetailScreen extends StatefulWidget {
  final Contact contact;
  
  const ContactDetailScreen({super.key, required this.contact});
  
  @override
  State<ContactDetailScreen> createState() => _ContactDetailScreenState();
}

class _ContactDetailScreenState extends State<ContactDetailScreen> {
  late Contact _contact;
  bool _isEditing = false;
  
  // Form controllers
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _companyController;
  late TextEditingController _positionController;
  late TextEditingController _notesController;
  
  @override
  void initState() {
    super.initState();
    _contact = widget.contact;
    _initControllers();
  }
  
  void _initControllers() {
    _firstNameController = TextEditingController(text: _contact.firstName);
    _lastNameController = TextEditingController(text: _contact.lastName);
    _emailController = TextEditingController(text: _contact.email ?? '');
    _phoneController = TextEditingController(text: _contact.phone ?? '');
    _companyController = TextEditingController(text: _contact.company ?? '');
    _positionController = TextEditingController(text: _contact.position ?? '');
    _notesController = TextEditingController(text: _contact.notes ?? '');
  }
  
  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _companyController.dispose();
    _positionController.dispose();
    _notesController.dispose();
    super.dispose();
  }
  
  Future<void> _saveChanges() async {
    // Simulate API call
    setState(() => _isEditing = false);
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Contact updated successfully'),
        backgroundColor: AppColors.success,
      ),
    );
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
      Navigator.pop(context, true); // Return true to indicate deletion
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Contact deleted'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit Contact' : 'Contact Details'),
        actions: [
          if (_isEditing)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () {
                setState(() => _isEditing = false);
                _initControllers();
              },
            )
          else
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => setState(() => _isEditing = true),
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
            if (!_isEditing) ...[
              _buildQuickActions(),
              const SizedBox(height: AppSizes.paddingLg),
            ],
            
            // Contact Info
            _buildInfoSection(),
            
            if (_isEditing) ...[
              const SizedBox(height: AppSizes.paddingLg),
              _buildSaveButton(),
            ],
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
        if (!_isEditing)
          Text(
            _contact.fullName,
            style: const TextStyle(
              fontSize: AppSizes.fontXl,
              fontWeight: FontWeight.bold,
            ),
          )
        else
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _firstNameController,
                  decoration: const InputDecoration(
                    labelText: 'First Name',
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              const SizedBox(width: AppSizes.paddingSm),
              Expanded(
                child: TextField(
                  controller: _lastNameController,
                  decoration: const InputDecoration(
                    labelText: 'Last Name',
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
            ],
          ),
        if (_contact.company != null && !_isEditing) ...[
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
            
            if (_isEditing) ...[
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email),
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone',
                  prefixIcon: Icon(Icons.phone),
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _companyController,
                decoration: const InputDecoration(
                  labelText: 'Company',
                  prefixIcon: Icon(Icons.business),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _positionController,
                decoration: const InputDecoration(
                  labelText: 'Position',
                  prefixIcon: Icon(Icons.work),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _notesController,
                decoration: const InputDecoration(
                  labelText: 'Notes',
                  prefixIcon: Icon(Icons.note),
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ] else ...[
              _buildInfoRow(Icons.email, 'Email', _contact.email ?? 'Not set'),
              _buildInfoRow(Icons.phone, 'Phone', _contact.phone ?? 'Not set'),
              _buildInfoRow(Icons.business, 'Company', _contact.company ?? 'Not set'),
              _buildInfoRow(Icons.work, 'Position', _contact.position ?? 'Not set'),
              _buildInfoRow(Icons.label, 'Status', _contact.status ?? 'Unknown'),
              if (_contact.notes != null)
                _buildInfoRow(Icons.note, 'Notes', _contact.notes!),
            ],
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
  
  Widget _buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _saveChanges,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
          ),
        ),
        child: const Text(
          'Save Changes',
          style: TextStyle(
            fontSize: AppSizes.fontMd,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
