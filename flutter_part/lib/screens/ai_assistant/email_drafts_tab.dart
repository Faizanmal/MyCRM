import 'package:flutter/material.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/empty_state.dart';

class EmailDraftsTab extends StatelessWidget {
  final AISalesAssistantProvider provider;

  const EmailDraftsTab({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    if (provider.emailDrafts.isEmpty) {
      return EmptyState(
        icon: Icons.email_outlined,
        title: 'No Email Drafts',
        subtitle: 'Generate your first AI email draft',
        action: ElevatedButton.icon(
          onPressed: () => _showGenerateDialog(context),
          icon: const Icon(Icons.auto_awesome),
          label: const Text('Generate Email'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.emailDrafts.length + 1,
      itemBuilder: (context, index) {
        if (index == 0) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: ElevatedButton.icon(
              onPressed: () => _showGenerateDialog(context),
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Generate New Email'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.all(16),
              ),
            ),
          );
        }
        return _buildDraftCard(context, provider.emailDrafts[index - 1]);
      },
    );
  }

  Widget _buildDraftCard(BuildContext context, AIEmailDraft draft) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    draft.emailType.replaceAll('_', ' ').toUpperCase(),
                    style: const TextStyle(
                      color: Colors.blue,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.grey.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    draft.tone.toUpperCase(),
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.copy, size: 20),
                  onPressed: () {
                    // Copy to clipboard
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Copied to clipboard')),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              draft.subject,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              draft.body,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }

  void _showGenerateDialog(BuildContext context) {
    final emailTypeController = TextEditingController(text: 'follow_up');
    final contactIdController = TextEditingController();
    final contextController = TextEditingController();
    final toneController = TextEditingController(text: 'professional');
    final opportunityIdController = TextEditingController();
    final keyPointsController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
          left: 16,
          right: 16,
          top: 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Generate AI Email',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: contactIdController,
              decoration: const InputDecoration(
                labelText: 'Contact ID',
                border: OutlineInputBorder(),
                hintText: 'Enter Contact ID (e.g., 123)',
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(4),
              ),
              child: DropdownButton<String>(
                value: emailTypeController.text,
                onChanged: (value) => emailTypeController.text = value!,
                items: const [
                  DropdownMenuItem(value: 'cold_outreach', child: Text('Cold Outreach')),
                  DropdownMenuItem(value: 'follow_up', child: Text('Follow Up')),
                  DropdownMenuItem(value: 'proposal', child: Text('Proposal')),
                  DropdownMenuItem(value: 'meeting_request', child: Text('Meeting Request')),
                ],
                isExpanded: true,
                underline: const SizedBox(),
                padding: const EdgeInsets.symmetric(horizontal: 12),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: opportunityIdController,
              decoration: const InputDecoration(
                labelText: 'Opportunity ID (Optional)',
                border: OutlineInputBorder(),
                hintText: 'Link to a deal',
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: keyPointsController,
              decoration: const InputDecoration(
                labelText: 'Key Points (comma separated)',
                border: OutlineInputBorder(),
                hintText: 'Pricing, discount, deadline',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: contextController,
              decoration: const InputDecoration(
                labelText: 'Context',
                border: OutlineInputBorder(),
                hintText: 'What is this email about?',
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                if (contactIdController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please enter a Contact ID')),
                  );
                  return;
                }

                Navigator.pop(context);
                provider.generateEmail(
                  emailType: emailTypeController.text,
                  contactId: contactIdController.text,
                  opportunityId: opportunityIdController.text.isNotEmpty ? opportunityIdController.text : null,
                  context: contextController.text,
                  tone: toneController.text,
                  keyPoints: keyPointsController.text.isNotEmpty
                      ? keyPointsController.text.split(',').map((e) => e.trim()).toList()
                      : null,
                );

                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Generating email...')),
                );
              },
              child: const Text('Generate'),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
