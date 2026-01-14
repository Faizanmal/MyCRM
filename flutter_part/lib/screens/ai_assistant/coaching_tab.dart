import 'package:flutter/material.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/empty_state.dart';

class CoachingTab extends StatelessWidget {
  final AISalesAssistantProvider provider;

  const CoachingTab({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    if (provider.coachingAdvice.isEmpty) {
      return EmptyState(
        icon: Icons.psychology_outlined,
        title: 'No Coaching Advice',
        subtitle: 'Analyze a deal to get personalized advice',
        action: ElevatedButton.icon(
          onPressed: () => _showAnalyzeDialog(context),
          icon: const Icon(Icons.analytics),
          label: const Text('Analyze Deal'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.coachingAdvice.length,
      itemBuilder: (context, index) {
        return _buildAdviceCard(provider.coachingAdvice[index]);
      },
    );
  }

  void _showAnalyzeDialog(BuildContext context) {
    final opportunityIdController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Analyze Deal'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Enter Opportunity ID to analyze:'),
            const SizedBox(height: 12),
            TextField(
              controller: opportunityIdController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Opportunity ID (e.g., 456)',
              ),
              keyboardType: TextInputType.number,
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
              if (opportunityIdController.text.isNotEmpty) {
                Navigator.pop(context);
                provider.analyzeDeal(opportunityIdController.text);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Analyzing deal...')),
                );
              }
            },
            child: const Text('Analyze'),
          ),
        ],
      ),
    );
  }

  Widget _buildAdviceCard(SalesCoachAdvice advice) {
    Color priorityColor;
    switch (advice.priority) {
      case 'critical':
        priorityColor = Colors.red;
        break;
      case 'high':
        priorityColor = Colors.orange;
        break;
      case 'medium':
        priorityColor = Colors.yellow.shade700;
        break;
      default:
        priorityColor = Colors.blue;
    }

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
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: priorityColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.lightbulb_outline,
                    color: priorityColor,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        advice.title,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        advice.adviceType.replaceAll('_', ' ').toUpperCase(),
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(advice.advice),
            if (advice.actionItems.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Text(
                'Action Items:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              ...advice.actionItems.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check_circle_outline, size: 16, color: Colors.green),
                    const SizedBox(width: 8),
                    Expanded(child: Text(item, style: const TextStyle(fontSize: 13))),
                  ],
                ),
              )),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => provider.dismissAdvice(advice.id),
                  child: const Text('Dismiss'),
                ),
                TextButton(
                  onPressed: () => provider.rateAdvice(advice.id, true),
                  child: const Text('Helpful'),
                ),
                ElevatedButton(
                  onPressed: () => provider.completeAdvice(advice.id),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: priorityColor,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Complete'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
