import 'package:flutter/material.dart';

class HelpSupportScreen extends StatefulWidget {
  const HelpSupportScreen({super.key});

  @override
  State<HelpSupportScreen> createState() => _HelpSupportScreenState();
}

class _HelpSupportScreenState extends State<HelpSupportScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _searchController = TextEditingController();
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Help & Support'),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.indigo.shade700, Colors.blue.shade500],
            ),
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'FAQ', icon: Icon(Icons.help_outline)),
            Tab(text: 'Guides', icon: Icon(Icons.book)),
            Tab(text: 'Contact', icon: Icon(Icons.support_agent)),
            Tab(text: 'Status', icon: Icon(Icons.info)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildFAQTab(),
          _buildGuidesTab(),
          _buildContactTab(),
          _buildStatusTab(),
        ],
      ),
    );
  }

  Widget _buildFAQTab() {
    final faqs = [
      {
        'category': 'Getting Started',
        'questions': [
          {'q': 'How do I create my first contact?', 'a': 'Navigate to Contacts from the main menu and click the + button to add a new contact.'},
          {'q': 'How do I import existing data?', 'a': 'Go to Settings > Import/Export and upload your CSV file with contact information.'},
          {'q': 'Can I customize my dashboard?', 'a': 'Yes! Click the gear icon on the dashboard to add, remove, or rearrange widgets.'},
        ],
      },
      {
        'category': 'Sales & Leads',
        'questions': [
          {'q': 'How do I convert a lead to an opportunity?', 'a': 'Open the lead details and click "Convert to Opportunity" button.'},
          {'q': 'What are pipeline stages?', 'a': 'Pipeline stages represent the progress of a deal from initial contact to closed.'},
          {'q': 'How do I track my sales targets?', 'a': 'Use the Revenue Intelligence module to set and track your sales targets.'},
        ],
      },
      {
        'category': 'Automation',
        'questions': [
          {'q': 'How do I set up email sequences?', 'a': 'Go to Email Sequences, create a new sequence, and add your email steps.'},
          {'q': 'Can I automate task creation?', 'a': 'Yes, use the workflow automation feature to create triggers and actions.'},
        ],
      },
      {
        'category': 'Integrations',
        'questions': [
          {'q': 'What integrations are available?', 'a': 'We integrate with Gmail, Outlook, Slack, Zoom, HubSpot, Salesforce, and many more.'},
          {'q': 'How do I connect my email?', 'a': 'Go to Integration Hub and click on Email to connect your account.'},
        ],
      },
    ];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Search bar
        TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: 'Search FAQs...',
            prefixIcon: const Icon(Icons.search),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            filled: true,
            fillColor: Colors.grey.shade50,
          ),
        ),
        const SizedBox(height: 20),
        
        // FAQ categories
        ...faqs.map((category) => _buildFAQCategory(
          category['category'] as String,
          category['questions'] as List<Map<String, String>>,
        )),
      ],
    );
  }

  Widget _buildFAQCategory(String title, List<Map<String, String>> questions) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ExpansionTile(
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        children: questions.map((qa) => ExpansionTile(
          title: Text(qa['q']!, style: const TextStyle(fontSize: 14)),
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(qa['a']!, style: TextStyle(color: Colors.grey.shade700)),
            ),
          ],
        )).toList(),
      ),
    );
  }

  Widget _buildGuidesTab() {
    final guides = [
      {'title': 'Getting Started Guide', 'description': 'Learn the basics of CRM in 10 minutes', 'icon': Icons.rocket_launch, 'color': Colors.blue},
      {'title': 'Sales Pipeline Setup', 'description': 'Configure your perfect sales pipeline', 'icon': Icons.trending_up, 'color': Colors.green},
      {'title': 'Email Automation', 'description': 'Master email sequences and templates', 'icon': Icons.email, 'color': Colors.orange},
      {'title': 'Reporting & Analytics', 'description': 'Create insightful reports and dashboards', 'icon': Icons.analytics, 'color': Colors.purple},
      {'title': 'Team Collaboration', 'description': 'Work effectively with your team', 'icon': Icons.groups, 'color': Colors.teal},
      {'title': 'API Integration', 'description': 'Connect external tools via API', 'icon': Icons.code, 'color': Colors.indigo},
      {'title': 'Mobile App Guide', 'description': 'Use CRM on the go', 'icon': Icons.phone_android, 'color': Colors.pink},
      {'title': 'Security Best Practices', 'description': 'Keep your data safe', 'icon': Icons.security, 'color': Colors.red},
    ];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.indigo.shade700, Colors.blue.shade500],
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.play_circle, color: Colors.white, size: 32),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Video Tutorials',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Watch step-by-step video guides',
                      style: TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward, color: Colors.white),
            ],
          ),
        ),
        const SizedBox(height: 20),
        const Text(
          'Documentation',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.2,
          ),
          itemCount: guides.length,
          itemBuilder: (context, index) {
            final guide = guides[index];
            return Card(
              child: InkWell(
                onTap: () {},
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        guide['icon'] as IconData,
                        color: guide['color'] as Color,
                        size: 32,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        guide['title'] as String,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        guide['description'] as String,
                        style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                        textAlign: TextAlign.center,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildContactTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Live Chat
        Card(
          child: ListTile(
            leading: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.chat, color: Colors.green.shade700),
            ),
            title: const Text('Live Chat'),
            subtitle: const Text('Get instant support'),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.green,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'Online',
                style: TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
            onTap: () => _showLiveChat(),
          ),
        ),
        const SizedBox(height: 12),
        
        // Email Support
        Card(
          child: ListTile(
            leading: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.email, color: Colors.blue.shade700),
            ),
            title: const Text('Email Support'),
            subtitle: const Text('support@crm.com'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
        ),
        const SizedBox(height: 12),
        
        // Phone Support
        Card(
          child: ListTile(
            leading: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.phone, color: Colors.orange.shade700),
            ),
            title: const Text('Phone Support'),
            subtitle: const Text('+1 (800) 123-4567'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
        ),
        const SizedBox(height: 24),
        
        // Submit Ticket
        const Text(
          'Submit a Support Ticket',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Category',
                    border: OutlineInputBorder(),
                  ),
                  items: ['Technical Issue', 'Billing', 'Feature Request', 'General Inquiry']
                      .map((cat) => DropdownMenuItem(value: cat, child: Text(cat)))
                      .toList(),
                  onChanged: (v) {},
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Priority',
                    border: OutlineInputBorder(),
                  ),
                  items: ['Low', 'Medium', 'High', 'Critical']
                      .map((p) => DropdownMenuItem(value: p, child: Text(p)))
                      .toList(),
                  onChanged: (v) {},
                ),
                const SizedBox(height: 16),
                const TextField(
                  decoration: InputDecoration(
                    labelText: 'Subject',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                const TextField(
                  maxLines: 4,
                  decoration: InputDecoration(
                    labelText: 'Description',
                    border: OutlineInputBorder(),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.attach_file),
                  label: const Text('Attach Files'),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => _submitTicket(),
                    child: const Text('Submit Ticket'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusTab() {
    final services = [
      {'name': 'API Services', 'status': 'operational', 'uptime': '99.99%'},
      {'name': 'Web Application', 'status': 'operational', 'uptime': '99.98%'},
      {'name': 'Email Services', 'status': 'operational', 'uptime': '99.95%'},
      {'name': 'Database', 'status': 'operational', 'uptime': '99.99%'},
      {'name': 'File Storage', 'status': 'operational', 'uptime': '99.97%'},
      {'name': 'Authentication', 'status': 'operational', 'uptime': '99.99%'},
    ];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Overall Status
        Card(
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
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.check_circle, color: Colors.white, size: 32),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'All Systems Operational',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Last updated: 2 minutes ago',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        
        // Services Status
        const Text(
          'Service Status',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Card(
          child: Column(
            children: services.map((service) => ListTile(
              leading: Icon(
                service['status'] == 'operational' 
                    ? Icons.check_circle 
                    : Icons.warning,
                color: service['status'] == 'operational' 
                    ? Colors.green 
                    : Colors.orange,
              ),
              title: Text(service['name'] as String),
              subtitle: Text(
                service['status'] == 'operational' 
                    ? 'Operational' 
                    : 'Degraded',
              ),
              trailing: Text(
                service['uptime'] as String,
                style: TextStyle(
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
            )).toList(),
          ),
        ),
        const SizedBox(height: 20),
        
        // Incidents
        const Text(
          'Recent Incidents',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Icon(Icons.celebration, size: 48, color: Colors.green.shade300),
                const SizedBox(height: 12),
                const Text(
                  'No incidents in the last 30 days',
                  style: TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  'We\'re working hard to keep things running smoothly',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        
        // Subscribe to updates
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Subscribe to Status Updates',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  'Get notified about incidents and maintenance',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Enter your email',
                          border: OutlineInputBorder(),
                          isDense: true,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: () {},
                      child: const Text('Subscribe'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _showLiveChat() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.8,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.green.shade100,
                    child: const Icon(Icons.support_agent, color: Colors.green),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Support Agent', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text('Online', style: TextStyle(color: Colors.green, fontSize: 12)),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.all(16),
                children: [
                  _buildChatBubble('Hello! How can I help you today?', false),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: InputDecoration(
                        hintText: 'Type your message...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    backgroundColor: Colors.blue,
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: () {},
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChatBubble(String message, bool isUser) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser ? Colors.blue : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          message,
          style: TextStyle(
            color: isUser ? Colors.white : Colors.black,
          ),
        ),
      ),
    );
  }

  void _submitTicket() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Support ticket submitted successfully!'),
        backgroundColor: Colors.green,
      ),
    );
  }
}
