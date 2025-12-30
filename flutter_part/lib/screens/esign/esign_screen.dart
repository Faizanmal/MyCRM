import 'package:flutter/material.dart';
import '../../widgets/common/app_drawer.dart';

class EsignScreen extends StatefulWidget {
  const EsignScreen({super.key});

  @override
  State<EsignScreen> createState() => _EsignScreenState();
}

class _EsignScreenState extends State<EsignScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final List<EsignDocument> _documents = _getSampleDocuments();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  static List<EsignDocument> _getSampleDocuments() {
    return [
      EsignDocument(
        id: '1',
        name: 'Sales Agreement - Acme Corp',
        status: EsignStatus.pending,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        expiresAt: DateTime.now().add(const Duration(days: 7)),
        signers: [
          Signer(name: 'John Smith', email: 'john@acme.com', status: SignerStatus.signed, signedAt: DateTime.now().subtract(const Duration(hours: 1))),
          Signer(name: 'Sarah Johnson', email: 'sarah@acme.com', status: SignerStatus.pending),
        ],
      ),
      EsignDocument(
        id: '2',
        name: 'NDA - TechStart Inc',
        status: EsignStatus.completed,
        createdAt: DateTime.now().subtract(const Duration(days: 3)),
        completedAt: DateTime.now().subtract(const Duration(days: 1)),
        signers: [
          Signer(name: 'Mike Chen', email: 'mike@techstart.com', status: SignerStatus.signed, signedAt: DateTime.now().subtract(const Duration(days: 2))),
          Signer(name: 'You', email: 'me@company.com', status: SignerStatus.signed, signedAt: DateTime.now().subtract(const Duration(days: 1))),
        ],
      ),
      EsignDocument(
        id: '3',
        name: 'Partnership Agreement',
        status: EsignStatus.draft,
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
        signers: [],
      ),
      EsignDocument(
        id: '4',
        name: 'Consulting Contract - Global Industries',
        status: EsignStatus.awaitingMe,
        createdAt: DateTime.now().subtract(const Duration(hours: 5)),
        expiresAt: DateTime.now().add(const Duration(days: 3)),
        signers: [
          Signer(name: 'Emily Davis', email: 'emily@global.com', status: SignerStatus.signed, signedAt: DateTime.now().subtract(const Duration(hours: 3))),
          Signer(name: 'You', email: 'me@company.com', status: SignerStatus.pending),
        ],
      ),
      EsignDocument(
        id: '5',
        name: 'Service Level Agreement',
        status: EsignStatus.expired,
        createdAt: DateTime.now().subtract(const Duration(days: 15)),
        expiresAt: DateTime.now().subtract(const Duration(days: 1)),
        signers: [
          Signer(name: 'David Wilson', email: 'david@client.com', status: SignerStatus.pending),
        ],
      ),
      EsignDocument(
        id: '6',
        name: 'Employment Offer - Jane Smith',
        status: EsignStatus.declined,
        createdAt: DateTime.now().subtract(const Duration(days: 5)),
        signers: [
          Signer(name: 'Jane Smith', email: 'jane@email.com', status: SignerStatus.declined),
        ],
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('E-Signatures'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF0D9488), Color(0xFF14B8A6)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {},
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'All', icon: Icon(Icons.folder)),
            Tab(text: 'Action', icon: Icon(Icons.pending_actions)),
            Tab(text: 'Sent', icon: Icon(Icons.send)),
            Tab(text: 'Completed', icon: Icon(Icons.check_circle)),
          ],
        ),
      ),
      drawer: const AppDrawer(),
      body: Column(
        children: [
          _buildQuickStats(),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildDocumentList(_documents),
                _buildDocumentList(_documents.where((d) => d.status == EsignStatus.awaitingMe).toList()),
                _buildDocumentList(_documents.where((d) => d.status == EsignStatus.pending).toList()),
                _buildDocumentList(_documents.where((d) => d.status == EsignStatus.completed).toList()),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCreateDocumentDialog,
        icon: const Icon(Icons.add),
        label: const Text('New Document'),
        backgroundColor: const Color(0xFF0D9488),
      ),
    );
  }

  Widget _buildQuickStats() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          _buildStatCard('Action Required', '${_documents.where((d) => d.status == EsignStatus.awaitingMe).length}', Colors.orange),
          _buildStatCard('Pending', '${_documents.where((d) => d.status == EsignStatus.pending).length}', Colors.blue),
          _buildStatCard('Completed', '${_documents.where((d) => d.status == EsignStatus.completed).length}', Colors.green),
          _buildStatCard('Expired', '${_documents.where((d) => d.status == EsignStatus.expired).length}', Colors.red),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, Color color) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color)),
              const SizedBox(height: 4),
              Text(label, style: TextStyle(fontSize: 10, color: Colors.grey[600]), textAlign: TextAlign.center),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDocumentList(List<EsignDocument> documents) {
    if (documents.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.draw, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text('No documents found', style: TextStyle(color: Colors.grey[600], fontSize: 16)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: documents.length,
      itemBuilder: (context, index) => _buildDocumentCard(documents[index]),
    );
  }

  Widget _buildDocumentCard(EsignDocument doc) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => _showDocumentDetails(doc),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: _getStatusColor(doc.status).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(Icons.description, color: _getStatusColor(doc.status)),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(doc.name, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                        const SizedBox(height: 4),
                        Text('Created ${_formatDate(doc.createdAt)}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                      ],
                    ),
                  ),
                  _buildStatusChip(doc.status),
                ],
              ),
              if (doc.signers.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Divider(height: 1),
                const SizedBox(height: 12),
                Text('Signers', style: TextStyle(color: Colors.grey[600], fontSize: 12, fontWeight: FontWeight.w500)),
                const SizedBox(height: 8),
                ...doc.signers.map((signer) => _buildSignerRow(signer)),
              ],
              if (doc.expiresAt != null && doc.status != EsignStatus.completed) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(
                      doc.expiresAt!.isBefore(DateTime.now()) ? Icons.error : Icons.schedule,
                      size: 14,
                      color: doc.expiresAt!.isBefore(DateTime.now()) ? Colors.red : Colors.orange,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      doc.expiresAt!.isBefore(DateTime.now()) 
                        ? 'Expired ${_formatDate(doc.expiresAt!)}'
                        : 'Expires ${_formatDate(doc.expiresAt!)}',
                      style: TextStyle(
                        color: doc.expiresAt!.isBefore(DateTime.now()) ? Colors.red : Colors.orange,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
              if (doc.status == EsignStatus.awaitingMe) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _signDocument(doc),
                        icon: const Icon(Icons.draw, size: 18),
                        label: const Text('Sign Now'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0D9488),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    OutlinedButton(
                      onPressed: () => _declineDocument(doc),
                      child: const Text('Decline'),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSignerRow(Signer signer) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          CircleAvatar(
            radius: 14,
            backgroundColor: _getSignerStatusColor(signer.status).withValues(alpha: 0.2),
            child: Icon(_getSignerStatusIcon(signer.status), size: 14, color: _getSignerStatusColor(signer.status)),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(signer.name, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                Text(signer.email, style: TextStyle(fontSize: 11, color: Colors.grey[600])),
              ],
            ),
          ),
          Text(
            _getSignerStatusText(signer),
            style: TextStyle(fontSize: 11, color: _getSignerStatusColor(signer.status)),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip(EsignStatus status) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: _getStatusColor(status).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        _getStatusText(status),
        style: TextStyle(color: _getStatusColor(status), fontSize: 12, fontWeight: FontWeight.w500),
      ),
    );
  }

  Color _getStatusColor(EsignStatus status) {
    switch (status) {
      case EsignStatus.draft:
        return Colors.grey;
      case EsignStatus.pending:
        return Colors.blue;
      case EsignStatus.awaitingMe:
        return Colors.orange;
      case EsignStatus.completed:
        return Colors.green;
      case EsignStatus.expired:
        return Colors.red;
      case EsignStatus.declined:
        return Colors.red;
    }
  }

  String _getStatusText(EsignStatus status) {
    switch (status) {
      case EsignStatus.draft:
        return 'Draft';
      case EsignStatus.pending:
        return 'Pending';
      case EsignStatus.awaitingMe:
        return 'Action Required';
      case EsignStatus.completed:
        return 'Completed';
      case EsignStatus.expired:
        return 'Expired';
      case EsignStatus.declined:
        return 'Declined';
    }
  }

  Color _getSignerStatusColor(SignerStatus status) {
    switch (status) {
      case SignerStatus.pending:
        return Colors.orange;
      case SignerStatus.signed:
        return Colors.green;
      case SignerStatus.declined:
        return Colors.red;
    }
  }

  IconData _getSignerStatusIcon(SignerStatus status) {
    switch (status) {
      case SignerStatus.pending:
        return Icons.pending;
      case SignerStatus.signed:
        return Icons.check;
      case SignerStatus.declined:
        return Icons.close;
    }
  }

  String _getSignerStatusText(Signer signer) {
    switch (signer.status) {
      case SignerStatus.pending:
        return 'Pending';
      case SignerStatus.signed:
        return 'Signed ${signer.signedAt != null ? _formatDate(signer.signedAt!) : ''}';
      case SignerStatus.declined:
        return 'Declined';
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.isNegative) {
      final futureDiff = date.difference(now);
      if (futureDiff.inDays < 1) return 'in ${futureDiff.inHours}h';
      return 'in ${futureDiff.inDays}d';
    }
    if (diff.inHours < 1) return '${diff.inMinutes}m ago';
    if (diff.inDays < 1) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${date.day}/${date.month}/${date.year}';
  }

  void _showDocumentDetails(EsignDocument doc) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey[300], borderRadius: BorderRadius.circular(2)))),
              const SizedBox(height: 16),
              Text(doc.name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              _buildStatusChip(doc.status),
              const SizedBox(height: 24),
              _buildDetailSection('Document Info', [
                _buildDetailItem('Created', _formatDate(doc.createdAt)),
                if (doc.expiresAt != null) _buildDetailItem('Expires', _formatDate(doc.expiresAt!)),
                if (doc.completedAt != null) _buildDetailItem('Completed', _formatDate(doc.completedAt!)),
              ]),
              const SizedBox(height: 16),
              if (doc.signers.isNotEmpty) ...[
                _buildDetailSection('Signers', doc.signers.map((s) => _buildSignerRow(s)).toList()),
              ],
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(child: OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.download), label: const Text('Download'))),
                  const SizedBox(width: 8),
                  Expanded(child: OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.share), label: const Text('Share'))),
                ],
              ),
              const SizedBox(height: 8),
              if (doc.status == EsignStatus.draft)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _sendForSignature(doc),
                    icon: const Icon(Icons.send),
                    label: const Text('Send for Signature'),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0D9488)),
                  ),
                ),
              if (doc.status == EsignStatus.awaitingMe)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _signDocument(doc),
                    icon: const Icon(Icons.draw),
                    label: const Text('Sign Document'),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0D9488)),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.grey)),
        const SizedBox(height: 8),
        ...children,
      ],
    );
  }

  Widget _buildDetailItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[600])),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  void _showCreateDocumentDialog() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (context) => Padding(
        padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(context).viewInsets.bottom + 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Create New Document', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            ListTile(
              leading: Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: Colors.blue.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.upload_file, color: Colors.blue)),
              title: const Text('Upload Document'),
              subtitle: const Text('PDF, DOC, DOCX'),
              onTap: () { Navigator.pop(context); },
            ),
            ListTile(
              leading: Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: Colors.green.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.dashboard, color: Colors.green)),
              title: const Text('Use Template'),
              subtitle: const Text('Start from a template'),
              onTap: () { Navigator.pop(context); },
            ),
            ListTile(
              leading: Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: Colors.purple.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.edit_document, color: Colors.purple)),
              title: const Text('Create from Scratch'),
              subtitle: const Text('Build a new document'),
              onTap: () { Navigator.pop(context); },
            ),
          ],
        ),
      ),
    );
  }

  void _signDocument(EsignDocument doc) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opening signature pad...')),
    );
  }

  void _declineDocument(EsignDocument doc) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Decline Document'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Please provide a reason for declining:'),
            const SizedBox(height: 12),
            const TextField(
              decoration: InputDecoration(labelText: 'Reason (optional)', border: OutlineInputBorder()),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Document declined'))); },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Decline'),
          ),
        ],
      ),
    );
  }

  void _sendForSignature(EsignDocument doc) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Document sent for signature')),
    );
  }
}

enum EsignStatus { draft, pending, awaitingMe, completed, expired, declined }
enum SignerStatus { pending, signed, declined }

class EsignDocument {
  final String id;
  final String name;
  final EsignStatus status;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final DateTime? completedAt;
  final List<Signer> signers;

  EsignDocument({
    required this.id,
    required this.name,
    required this.status,
    required this.createdAt,
    this.expiresAt,
    this.completedAt,
    required this.signers,
  });
}

class Signer {
  final String name;
  final String email;
  final SignerStatus status;
  final DateTime? signedAt;

  Signer({required this.name, required this.email, required this.status, this.signedAt});
}
