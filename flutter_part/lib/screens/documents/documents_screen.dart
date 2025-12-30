import 'package:flutter/material.dart';
import '../../widgets/common/app_drawer.dart';

class DocumentsScreen extends StatefulWidget {
  const DocumentsScreen({super.key});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _searchQuery = '';
  String _sortBy = 'modified';
  bool _isGridView = true;
  final List<Document> _documents = _getSampleDocuments();

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

  static List<Document> _getSampleDocuments() {
    return [
      Document(id: '1', name: 'Sales Proposal - Acme Corp.pdf', type: 'pdf', size: '2.4 MB', 
        folder: 'Proposals', modifiedAt: DateTime.now().subtract(const Duration(hours: 2)),
        owner: 'John Doe', sharedWith: ['Sarah', 'Mike']),
      Document(id: '2', name: 'Q4 Revenue Report.xlsx', type: 'excel', size: '1.8 MB', 
        folder: 'Reports', modifiedAt: DateTime.now().subtract(const Duration(days: 1)),
        owner: 'John Doe', sharedWith: []),
      Document(id: '3', name: 'Client Contract Template.docx', type: 'word', size: '856 KB', 
        folder: 'Templates', modifiedAt: DateTime.now().subtract(const Duration(days: 3)),
        owner: 'Sarah Johnson', sharedWith: ['John', 'Emily']),
      Document(id: '4', name: 'Product Demo.mp4', type: 'video', size: '45.2 MB', 
        folder: 'Media', modifiedAt: DateTime.now().subtract(const Duration(days: 5)),
        owner: 'Mike Chen', sharedWith: []),
      Document(id: '5', name: 'Meeting Notes - TechStart.pdf', type: 'pdf', size: '456 KB', 
        folder: 'Notes', modifiedAt: DateTime.now().subtract(const Duration(hours: 5)),
        owner: 'John Doe', sharedWith: ['Team']),
      Document(id: '6', name: 'Brand Guidelines.pdf', type: 'pdf', size: '8.2 MB', 
        folder: 'Marketing', modifiedAt: DateTime.now().subtract(const Duration(days: 10)),
        owner: 'Emily Davis', sharedWith: ['All']),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Documents'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF7C3AED), Color(0xFFA855F7)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(_isGridView ? Icons.list : Icons.grid_view),
            onPressed: () => setState(() => _isGridView = !_isGridView),
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            onSelected: (value) => setState(() => _sortBy = value),
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'name', child: Text('Sort by Name')),
              const PopupMenuItem(value: 'modified', child: Text('Sort by Modified')),
              const PopupMenuItem(value: 'size', child: Text('Sort by Size')),
              const PopupMenuItem(value: 'type', child: Text('Sort by Type')),
            ],
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'All', icon: Icon(Icons.folder)),
            Tab(text: 'Recent', icon: Icon(Icons.access_time)),
            Tab(text: 'Shared', icon: Icon(Icons.people)),
            Tab(text: 'Starred', icon: Icon(Icons.star)),
          ],
        ),
      ),
      drawer: const AppDrawer(),
      body: Column(
        children: [
          _buildSearchBar(),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildDocumentList(_documents),
                _buildDocumentList(_documents.where((d) => 
                  d.modifiedAt.isAfter(DateTime.now().subtract(const Duration(days: 7)))).toList()),
                _buildDocumentList(_documents.where((d) => d.sharedWith.isNotEmpty).toList()),
                _buildDocumentList(_documents.where((d) => d.isStarred).toList()),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showUploadDialog,
        icon: const Icon(Icons.upload_file),
        label: const Text('Upload'),
        backgroundColor: const Color(0xFF7C3AED),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: TextField(
        decoration: InputDecoration(
          hintText: 'Search documents...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchQuery.isNotEmpty
            ? IconButton(icon: const Icon(Icons.clear), onPressed: () => setState(() => _searchQuery = ''))
            : null,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.grey[100],
        ),
        onChanged: (value) => setState(() => _searchQuery = value),
      ),
    );
  }

  Widget _buildDocumentList(List<Document> documents) {
    final filteredDocs = documents.where((d) => 
      d.name.toLowerCase().contains(_searchQuery.toLowerCase())).toList();

    if (filteredDocs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.folder_open, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text('No documents found', style: TextStyle(color: Colors.grey[600], fontSize: 16)),
          ],
        ),
      );
    }

    if (_isGridView) {
      return GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 0.9,
        ),
        itemCount: filteredDocs.length,
        itemBuilder: (context, index) => _buildDocumentCard(filteredDocs[index]),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filteredDocs.length,
      itemBuilder: (context, index) => _buildDocumentListTile(filteredDocs[index]),
    );
  }

  Widget _buildDocumentCard(Document doc) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => _openDocument(doc),
        onLongPress: () => _showDocumentOptions(doc),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _getFileIcon(doc.type),
                  const Spacer(),
                  IconButton(
                    icon: Icon(doc.isStarred ? Icons.star : Icons.star_border,
                      color: doc.isStarred ? Colors.amber : Colors.grey),
                    onPressed: () => setState(() => doc.isStarred = !doc.isStarred),
                    iconSize: 20,
                    constraints: const BoxConstraints(),
                    padding: EdgeInsets.zero,
                  ),
                ],
              ),
              const Spacer(),
              Text(
                doc.name,
                style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                doc.size,
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  if (doc.sharedWith.isNotEmpty) ...[
                    Icon(Icons.people, size: 14, color: Colors.grey[500]),
                    const SizedBox(width: 4),
                    Text('${doc.sharedWith.length}', style: TextStyle(fontSize: 12, color: Colors.grey[500])),
                  ],
                  const Spacer(),
                  Text(_formatDate(doc.modifiedAt), style: TextStyle(fontSize: 10, color: Colors.grey[500])),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDocumentListTile(Document doc) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: _getFileIcon(doc.type),
        title: Text(doc.name, style: const TextStyle(fontWeight: FontWeight.w500)),
        subtitle: Text('${doc.size} • ${_formatDate(doc.modifiedAt)}'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (doc.sharedWith.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: Icon(Icons.people, size: 18, color: Colors.grey[500]),
              ),
            IconButton(
              icon: Icon(doc.isStarred ? Icons.star : Icons.star_border,
                color: doc.isStarred ? Colors.amber : Colors.grey),
              onPressed: () => setState(() => doc.isStarred = !doc.isStarred),
            ),
            PopupMenuButton<String>(
              onSelected: (value) => _handleDocumentAction(doc, value),
              itemBuilder: (context) => [
                const PopupMenuItem(value: 'open', child: ListTile(leading: Icon(Icons.open_in_new), title: Text('Open'))),
                const PopupMenuItem(value: 'download', child: ListTile(leading: Icon(Icons.download), title: Text('Download'))),
                const PopupMenuItem(value: 'share', child: ListTile(leading: Icon(Icons.share), title: Text('Share'))),
                const PopupMenuItem(value: 'rename', child: ListTile(leading: Icon(Icons.edit), title: Text('Rename'))),
                const PopupMenuItem(value: 'move', child: ListTile(leading: Icon(Icons.folder), title: Text('Move'))),
                const PopupMenuItem(value: 'delete', child: ListTile(leading: Icon(Icons.delete, color: Colors.red), title: Text('Delete', style: TextStyle(color: Colors.red)))),
              ],
            ),
          ],
        ),
        onTap: () => _openDocument(doc),
      ),
    );
  }

  Widget _getFileIcon(String type) {
    IconData icon;
    Color color;
    switch (type) {
      case 'pdf':
        icon = Icons.picture_as_pdf;
        color = Colors.red;
        break;
      case 'word':
        icon = Icons.description;
        color = Colors.blue;
        break;
      case 'excel':
        icon = Icons.table_chart;
        color = Colors.green;
        break;
      case 'video':
        icon = Icons.video_file;
        color = Colors.purple;
        break;
      case 'image':
        icon = Icons.image;
        color = Colors.orange;
        break;
      default:
        icon = Icons.insert_drive_file;
        color = Colors.grey;
    }
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(icon, color: color, size: 28),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.inHours < 1) return '${diff.inMinutes}m ago';
    if (diff.inDays < 1) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${date.day}/${date.month}/${date.year}';
  }

  void _openDocument(Document doc) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Opening ${doc.name}...')),
    );
  }

  void _showDocumentOptions(Document doc) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: _getFileIcon(doc.type),
              title: Text(doc.name, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${doc.size} • ${doc.folder}'),
            ),
            const Divider(),
            ListTile(leading: const Icon(Icons.open_in_new), title: const Text('Open'), onTap: () { Navigator.pop(context); _openDocument(doc); }),
            ListTile(leading: const Icon(Icons.download), title: const Text('Download'), onTap: () { Navigator.pop(context); }),
            ListTile(leading: const Icon(Icons.share), title: const Text('Share'), onTap: () { Navigator.pop(context); _showShareDialog(doc); }),
            ListTile(leading: const Icon(Icons.info), title: const Text('Details'), onTap: () { Navigator.pop(context); _showDetailsDialog(doc); }),
            ListTile(leading: const Icon(Icons.delete, color: Colors.red), title: const Text('Delete', style: TextStyle(color: Colors.red)), onTap: () { Navigator.pop(context); _deleteDocument(doc); }),
          ],
        ),
      ),
    );
  }

  void _handleDocumentAction(Document doc, String action) {
    switch (action) {
      case 'open':
        _openDocument(doc);
        break;
      case 'share':
        _showShareDialog(doc);
        break;
      case 'delete':
        _deleteDocument(doc);
        break;
    }
  }

  void _showUploadDialog() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Upload Document', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildUploadOption(Icons.photo_library, 'Gallery', Colors.green),
                _buildUploadOption(Icons.camera_alt, 'Camera', Colors.blue),
                _buildUploadOption(Icons.folder, 'Files', Colors.orange),
                _buildUploadOption(Icons.cloud, 'Cloud', Colors.purple),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildUploadOption(IconData icon, String label, Color color) {
    return InkWell(
      onTap: () {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Uploading from $label...')),
        );
      },
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 32),
          ),
          const SizedBox(height: 8),
          Text(label, style: TextStyle(color: Colors.grey[700])),
        ],
      ),
    );
  }

  void _showShareDialog(Document doc) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Share Document'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: 'Email or name',
                prefixIcon: Icon(Icons.person_add),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.link),
                  label: const Text('Copy Link'),
                )),
                const SizedBox(width: 8),
                Expanded(child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.email),
                  label: const Text('Email'),
                )),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(context), child: const Text('Share')),
        ],
      ),
    );
  }

  void _showDetailsDialog(Document doc) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Document Details'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow('Name', doc.name),
            _buildDetailRow('Size', doc.size),
            _buildDetailRow('Type', doc.type.toUpperCase()),
            _buildDetailRow('Folder', doc.folder),
            _buildDetailRow('Owner', doc.owner),
            _buildDetailRow('Modified', _formatDate(doc.modifiedAt)),
            if (doc.sharedWith.isNotEmpty)
              _buildDetailRow('Shared with', doc.sharedWith.join(', ')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 80, child: Text(label, style: TextStyle(color: Colors.grey[600]))),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500))),
        ],
      ),
    );
  }

  void _deleteDocument(Document doc) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Document'),
        content: Text('Are you sure you want to delete "${doc.name}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              setState(() => _documents.removeWhere((d) => d.id == doc.id));
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Document deleted')),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

class Document {
  final String id;
  final String name;
  final String type;
  final String size;
  final String folder;
  final DateTime modifiedAt;
  final String owner;
  final List<String> sharedWith;
  bool isStarred;

  Document({
    required this.id,
    required this.name,
    required this.type,
    required this.size,
    required this.folder,
    required this.modifiedAt,
    required this.owner,
    this.sharedWith = const [],
    this.isStarred = false,
  });
}
