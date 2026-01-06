import 'package:flutter/material.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/empty_state.dart';

class ObjectionTab extends StatelessWidget {
  final AISalesAssistantProvider provider;

  const ObjectionTab({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    if (provider.objectionResponses.isEmpty) {
      return const EmptyState(
        icon: Icons.question_answer_outlined,
        title: 'Objection Library Empty',
        subtitle: 'No objection responses found',
      );
    }

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            decoration: InputDecoration(
              hintText: 'Search objections...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: Colors.grey.shade50,
            ),
            onSubmitted: (value) => provider.handleObjection(value),
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: provider.objectionResponses.length,
            itemBuilder: (context, index) {
              return _buildObjectionCard(provider.objectionResponses[index]);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildObjectionCard(ObjectionResponse objection) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        title: Text(
          objection.objection,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          objection.category.toUpperCase(),
          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.withOpacity(0.3)),
                  ),
                  child: Text(
                    objection.bestResponse,
                    style: const TextStyle(color: Colors.black87),
                  ),
                ),
                if (objection.responses.length > 1) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Alternatives:',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  ...objection.responses.skip(1).take(2).map((r) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text('• $r', style: TextStyle(color: Colors.grey.shade700)),
                  )),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
