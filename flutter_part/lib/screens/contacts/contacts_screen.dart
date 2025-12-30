import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';
import 'contact_detail_screen.dart';
import 'add_contact_screen.dart';

class ContactsScreen extends StatefulWidget {
  const ContactsScreen({super.key});
  
  @override
  State<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends State<ContactsScreen> {
  List<Contact> _contacts = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadContacts();
  }
  
  Future<void> _loadContacts() async {
    setState(() => _isLoading = true);
    
    // Simulate API call with mock data
    await Future.delayed(const Duration(milliseconds: 800));
    
    setState(() {
      _contacts = [
        Contact(
          id: 1,
          firstName: 'John',
          lastName: 'Doe',
          email: 'john.doe@example.com',
          phone: '+1234567890',
          company: 'Acme Corp',
          position: 'CEO',
          status: 'Active',
        ),
        Contact(
          id: 2,
          firstName: 'Jane',
          lastName: 'Smith',
          email: 'jane.smith@example.com',
          phone: '+1234567891',
          company: 'Tech Solutions',
          position: 'CTO',
          status: 'Active',
        ),
        Contact(
          id: 3,
          firstName: 'Bob',
          lastName: 'Johnson',
          email: 'bob.j@example.com',
          phone: '+1234567892',
          company: 'Marketing Inc',
          position: 'Manager',
          status: 'Prospect',
        ),
      ];
      _isLoading = false;
    });
  }
  
  void _navigateToAddContact() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const AddContactScreen()),
    );
    
    if (result == true) {
      _loadContacts();
    }
  }
  
  void _navigateToContactDetail(Contact contact) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => ContactDetailScreen(contact: contact),
      ),
    );
    
    if (result == true) {
      _loadContacts();
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadContacts,
              child: _contacts.isEmpty
                  ? _buildEmptyState()
                  : ListView.separated(
                      padding: const EdgeInsets.all(AppSizes.paddingMd),
                      itemCount: _contacts.length,
                      separatorBuilder: (context, index) => const SizedBox(height: AppSizes.paddingSm),
                      itemBuilder: (context, index) {
                        final contact = _contacts[index];
                        return _buildContactCard(contact);
                      },
                    ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToAddContact,
        child: const Icon(Icons.add),
      ),
    );
  }
  
  Widget _buildContactCard(Contact contact) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppColors.primary,
          child: Text(
            contact.initials,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          contact.fullName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (contact.company != null)
              Text('${contact.company} ${contact.position != null ? '• ${contact.position}' : ''}'),
            if (contact.email != null)
              Text(
                contact.email!,
                style: const TextStyle(fontSize: AppSizes.fontSm),
              ),
            if (contact.phone != null)
              Text(
                contact.phone!,
                style: const TextStyle(fontSize: AppSizes.fontSm),
              ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSizes.paddingSm,
            vertical: 4,
          ),
          decoration: BoxDecoration(
            color: contact.status == 'Active' 
                ? AppColors.success.withValues(alpha: 0.1)
                : AppColors.warning.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AppSizes.radiusSm),
          ),
          child: Text(
            contact.status ?? 'Unknown',
            style: TextStyle(
              fontSize: AppSizes.fontXs,
              fontWeight: FontWeight.w600,
              color: contact.status == 'Active' 
                  ? AppColors.success
                  : AppColors.warning,
            ),
          ),
        ),
        isThreeLine: true,
        onTap: () => _navigateToContactDetail(contact),
      ),
    );
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.people_outline,
            size: 80,
            color: AppColors.grey400,
          ),
          const SizedBox(height: AppSizes.paddingMd),
          const Text(
            'No contacts yet',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: AppSizes.paddingSm),
          Text(
            'Add your first contact to get started',
            style: TextStyle(
              fontSize: AppSizes.fontMd,
              color: AppColors.grey600,
            ),
          ),
        ],
      ),
    );
  }
}
