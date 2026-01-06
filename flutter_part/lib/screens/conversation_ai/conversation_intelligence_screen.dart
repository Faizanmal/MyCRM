import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../widgets/common/app_drawer.dart';

class ConversationIntelligenceScreen extends StatefulWidget {
  const ConversationIntelligenceScreen({super.key});

  @override
  State<ConversationIntelligenceScreen> createState() => _ConversationIntelligenceScreenState();
}

class _ConversationIntelligenceScreenState extends State<ConversationIntelligenceScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final List<CallRecording> _recordings = _getSampleRecordings();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  static List<CallRecording> _getSampleRecordings() {
    return [
      CallRecording(
        id: '1',
        title: 'Discovery Call - Acme Corp',
        contact: 'John Smith',
        company: 'Acme Corp',
        duration: const Duration(minutes: 32, seconds: 15),
        date: DateTime.now().subtract(const Duration(hours: 2)),
        sentiment: 0.78,
        keywords: ['pricing', 'integration', 'timeline', 'budget'],
        talkRatio: 0.45,
        insights: [
          'Customer expressed interest in enterprise plan',
          'Concerns about implementation timeline',
          'Potential deal size: \$45,000',
        ],
        actionItems: [
          'Send pricing proposal by Friday',
          'Schedule technical demo',
          'Follow up on integration requirements',
        ],
      ),
      CallRecording(
        id: '2',
        title: 'Follow-up - TechStart',
        contact: 'Sarah Johnson',
        company: 'TechStart Inc',
        duration: const Duration(minutes: 18, seconds: 42),
        date: DateTime.now().subtract(const Duration(days: 1)),
        sentiment: 0.92,
        keywords: ['features', 'demo', 'trial', 'success'],
        talkRatio: 0.38,
        insights: [
          'Very positive reaction to product demo',
          'Ready to move forward with trial',
          'Decision maker engaged throughout',
        ],
        actionItems: [
          'Set up trial account',
          'Send onboarding materials',
        ],
      ),
      CallRecording(
        id: '3',
        title: 'Negotiation - Global Industries',
        contact: 'Mike Chen',
        company: 'Global Industries',
        duration: const Duration(minutes: 45, seconds: 30),
        date: DateTime.now().subtract(const Duration(days: 2)),
        sentiment: 0.55,
        keywords: ['discount', 'competitor', 'contract', 'terms'],
        talkRatio: 0.52,
        insights: [
          'Customer comparing with competitor pricing',
          'Requesting 15% discount',
          'Contract terms need legal review',
        ],
        actionItems: [
          'Prepare competitive analysis',
          'Get approval for discount',
          'Schedule legal review call',
        ],
      ),
      CallRecording(
        id: '4',
        title: 'Product Demo - StartupXYZ',
        contact: 'Emily Davis',
        company: 'StartupXYZ',
        duration: const Duration(minutes: 55, seconds: 20),
        date: DateTime.now().subtract(const Duration(days: 3)),
        sentiment: 0.85,
        keywords: ['API', 'customization', 'workflow', 'automation'],
        talkRatio: 0.35,
        insights: [
          'Strong interest in API capabilities',
          'Wants custom workflow automation',
          'Technical decision maker present',
        ],
        actionItems: [
          'Share API documentation',
          'Create custom workflow mockup',
        ],
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Conversation Intelligence'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF7C3AED), Color(0xFF9333EA)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        actions: [
          IconButton(icon: const Icon(Icons.search), onPressed: () {}),
          IconButton(icon: const Icon(Icons.filter_list), onPressed: () {}),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'Recordings', icon: Icon(Icons.mic)),
            Tab(text: 'Analytics', icon: Icon(Icons.analytics)),
            Tab(text: 'Coaching', icon: Icon(Icons.school)),
          ],
        ),
      ),
      drawer: const AppDrawer(),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildRecordingsTab(),
          _buildAnalyticsTab(),
          _buildCoachingTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _startRecording,
        icon: const Icon(Icons.mic),
        label: const Text('Record Call'),
        backgroundColor: const Color(0xFF7C3AED),
      ),
    );
  }

  Widget _buildRecordingsTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _recordings.length,
      itemBuilder: (context, index) => _buildRecordingCard(_recordings[index]),
    );
  }

  Widget _buildRecordingCard(CallRecording recording) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => _showRecordingDetails(recording),
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
                      color: const Color(0xFF7C3AED).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.mic, color: Color(0xFF7C3AED)),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(recording.title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                        const SizedBox(height: 4),
                        Text('${recording.contact} • ${recording.company}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                      ],
                    ),
                  ),
                  _buildSentimentIndicator(recording.sentiment),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.schedule, size: 14, color: Colors.grey[500]),
                  const SizedBox(width: 4),
                  Text(_formatDuration(recording.duration), style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                  const SizedBox(width: 16),
                  Icon(Icons.calendar_today, size: 14, color: Colors.grey[500]),
                  const SizedBox(width: 4),
                  Text(_formatDate(recording.date), style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: recording.keywords.take(4).map((keyword) => Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(keyword, style: TextStyle(fontSize: 11, color: Colors.grey[700])),
                )).toList(),
              ),
              if (recording.insights.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.lightbulb, size: 16, color: Colors.blue[700]),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          recording.insights.first,
                          style: TextStyle(fontSize: 12, color: Colors.blue[700]),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.play_arrow, size: 18),
                      label: const Text('Play'),
                      style: OutlinedButton.styleFrom(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.text_snippet, size: 18),
                      label: const Text('Transcript'),
                      style: OutlinedButton.styleFrom(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSentimentIndicator(double sentiment) {
    Color color;
    String label;
    IconData icon;
    if (sentiment >= 0.7) {
      color = Colors.green;
      label = 'Positive';
      icon = Icons.sentiment_satisfied;
    } else if (sentiment >= 0.4) {
      color = Colors.orange;
      label = 'Neutral';
      icon = Icons.sentiment_neutral;
    } else {
      color = Colors.red;
      label = 'Negative';
      icon = Icons.sentiment_dissatisfied;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _buildAnalyticsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildOverviewCards(),
          const SizedBox(height: 24),
          _buildSectionTitle('Talk Time Distribution'),
          const SizedBox(height: 8),
          _buildTalkTimeChart(),
          const SizedBox(height: 24),
          _buildSectionTitle('Sentiment Trend'),
          const SizedBox(height: 8),
          _buildSentimentTrendChart(),
          const SizedBox(height: 24),
          _buildSectionTitle('Top Keywords This Week'),
          const SizedBox(height: 8),
          _buildKeywordCloud(),
          const SizedBox(height: 24),
          _buildSectionTitle('Call Metrics'),
          const SizedBox(height: 8),
          _buildCallMetrics(),
        ],
      ),
    );
  }

  Widget _buildOverviewCards() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildStatCard('Total Calls', '${_recordings.length}', Icons.phone, Colors.blue),
        _buildStatCard('Total Duration', '2h 31m', Icons.schedule, Colors.green),
        _buildStatCard('Avg Sentiment', '77%', Icons.sentiment_satisfied, Colors.orange),
        _buildStatCard('Action Items', '8', Icons.task_alt, Colors.purple),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('+12%', style: TextStyle(fontSize: 10, color: Colors.green)),
                ),
              ],
            ),
            const Spacer(),
            Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            Text(title, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
          ],
        ),
      ),
    );
  }

  Widget _buildTalkTimeChart() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)],
      ),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: 100,
          barGroups: [
            BarChartGroupData(x: 0, barRods: [
              BarChartRodData(toY: 45, color: const Color(0xFF7C3AED), width: 16),
              BarChartRodData(toY: 55, color: Colors.grey[300], width: 16),
            ]),
            BarChartGroupData(x: 1, barRods: [
              BarChartRodData(toY: 38, color: const Color(0xFF7C3AED), width: 16),
              BarChartRodData(toY: 62, color: Colors.grey[300], width: 16),
            ]),
            BarChartGroupData(x: 2, barRods: [
              BarChartRodData(toY: 52, color: const Color(0xFF7C3AED), width: 16),
              BarChartRodData(toY: 48, color: Colors.grey[300], width: 16),
            ]),
            BarChartGroupData(x: 3, barRods: [
              BarChartRodData(toY: 35, color: const Color(0xFF7C3AED), width: 16),
              BarChartRodData(toY: 65, color: Colors.grey[300], width: 16),
            ]),
          ],
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final labels = ['Call 1', 'Call 2', 'Call 3', 'Call 4'];
                return Text(labels[value.toInt()], style: const TextStyle(fontSize: 10));
              },
            )),
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 30)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          gridData: const FlGridData(show: false),
        ),
      ),
    );
  }

  Widget _buildSentimentTrendChart() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)],
      ),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: true, drawVerticalLine: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 30)),
            bottomTitles: AxisTitles(sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
                if (value.toInt() < labels.length) {
                  return Text(labels[value.toInt()], style: const TextStyle(fontSize: 10));
                }
                return const Text('');
              },
            )),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: const [FlSpot(0, 72), FlSpot(1, 68), FlSpot(2, 85), FlSpot(3, 78), FlSpot(4, 82)],
              isCurved: true,
              color: const Color(0xFF7C3AED),
              barWidth: 3,
              belowBarData: BarAreaData(show: true, color: const Color(0xFF7C3AED).withValues(alpha: 0.1)),
              dotData: const FlDotData(show: true),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKeywordCloud() {
    final keywords = ['pricing', 'features', 'integration', 'timeline', 'demo', 'trial', 'support', 'contract', 'ROI', 'API'];
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)],
      ),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: keywords.asMap().entries.map((entry) {
          final size = 14.0 + (10 - entry.key) * 1.2;
          final opacity = 0.5 + (10 - entry.key) * 0.05;
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF7C3AED).withValues(alpha: opacity),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(entry.value, style: TextStyle(fontSize: size, color: Colors.white, fontWeight: FontWeight.w500)),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildCallMetrics() {
    final metrics = [
      {'label': 'Longest Monologue', 'value': '4m 32s', 'benchmark': '< 5 min', 'isGood': true},
      {'label': 'Filler Words', 'value': '12/call', 'benchmark': '< 15', 'isGood': true},
      {'label': 'Questions Asked', 'value': '8.5/call', 'benchmark': '> 5', 'isGood': true},
      {'label': 'Talk Speed', 'value': '145 wpm', 'benchmark': '120-160 wpm', 'isGood': true},
    ];

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: metrics.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final metric = metrics[index];
          return ListTile(
            title: Text(metric['label'] as String),
            subtitle: Text('Benchmark: ${metric['benchmark']}', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(metric['value'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(width: 8),
                Icon(metric['isGood'] as bool ? Icons.check_circle : Icons.warning, 
                  color: metric['isGood'] as bool ? Colors.green : Colors.orange, size: 20),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCoachingTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCoachingScore(),
          const SizedBox(height: 24),
          _buildSectionTitle('Improvement Areas'),
          const SizedBox(height: 8),
          _buildImprovementAreas(),
          const SizedBox(height: 24),
          _buildSectionTitle('Recommended Courses'),
          const SizedBox(height: 8),
          _buildRecommendedCourses(),
          const SizedBox(height: 24),
          _buildSectionTitle('Best Practices'),
          const SizedBox(height: 8),
          _buildBestPractices(),
        ],
      ),
    );
  }

  Widget _buildCoachingScore() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 100,
                  height: 100,
                  child: CircularProgressIndicator(
                    value: 0.78,
                    strokeWidth: 10,
                    backgroundColor: Colors.grey[200],
                    valueColor: const AlwaysStoppedAnimation(Color(0xFF7C3AED)),
                  ),
                ),
                const Column(
                  children: [
                    Text('78', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
                    Text('Score', style: TextStyle(fontSize: 12, color: Colors.grey)),
                  ],
                ),
              ],
            ),
            const SizedBox(width: 24),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Great Progress!', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text('Your coaching score improved by 5 points this week.', style: TextStyle(color: Colors.grey[600])),
                  const SizedBox(height: 12),
                  LinearProgressIndicator(
                    value: 0.78,
                    backgroundColor: Colors.grey[200],
                    valueColor: const AlwaysStoppedAnimation(Color(0xFF7C3AED)),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  const SizedBox(height: 4),
                  Text('22 points to next level', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImprovementAreas() {
    final areas = [
      {'area': 'Active Listening', 'score': 85, 'change': '+5%'},
      {'area': 'Question Techniques', 'score': 72, 'change': '+3%'},
      {'area': 'Objection Handling', 'score': 68, 'change': '-2%'},
      {'area': 'Closing Skills', 'score': 75, 'change': '+8%'},
    ];

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: areas.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final area = areas[index];
          final isPositive = (area['change'] as String).startsWith('+');
          return ListTile(
            title: Text(area['area'] as String),
            subtitle: LinearProgressIndicator(
              value: (area['score'] as int) / 100,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation(_getScoreColor(area['score'] as int)),
              borderRadius: BorderRadius.circular(4),
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('${area['score']}%', style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(width: 8),
                Text(area['change'] as String, style: TextStyle(color: isPositive ? Colors.green : Colors.red, fontSize: 12)),
              ],
            ),
          );
        },
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  Widget _buildRecommendedCourses() {
    final courses = [
      {'title': 'Mastering Objection Handling', 'duration': '45 min', 'difficulty': 'Intermediate'},
      {'title': 'The Art of Active Listening', 'duration': '30 min', 'difficulty': 'Beginner'},
      {'title': 'Advanced Closing Techniques', 'duration': '60 min', 'difficulty': 'Advanced'},
    ];

    return Column(
      children: courses.map((course) => Card(
        margin: const EdgeInsets.only(bottom: 8),
        child: ListTile(
          leading: Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFF7C3AED).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.play_circle, color: Color(0xFF7C3AED)),
          ),
          title: Text(course['title']!, style: const TextStyle(fontWeight: FontWeight.w500)),
          subtitle: Text('${course['duration']} • ${course['difficulty']}'),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () {},
        ),
      )).toList(),
    );
  }

  Widget _buildBestPractices() {
    final practices = [
      'Ask open-ended questions to understand customer needs',
      'Listen more than you talk (aim for 40% talk ratio)',
      'Summarize key points before moving to next topic',
      'Address objections with empathy and data',
      'Always end with clear next steps',
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: practices.asMap().entries.map((entry) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    color: const Color(0xFF7C3AED).withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Center(child: Text('${entry.key + 1}', style: const TextStyle(color: Color(0xFF7C3AED), fontWeight: FontWeight.bold, fontSize: 12))),
                ),
                const SizedBox(width: 12),
                Expanded(child: Text(entry.value)),
              ],
            ),
          )).toList(),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600));
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds % 60;
    return '${minutes}m ${seconds}s';
  }

  String _formatDate(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inHours < 1) return '${diff.inMinutes}m ago';
    if (diff.inDays < 1) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${date.day}/${date.month}/${date.year}';
  }

  void _showRecordingDetails(CallRecording recording) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey[300], borderRadius: BorderRadius.circular(2)))),
              const SizedBox(height: 16),
              Text(recording.title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text('${recording.contact} • ${recording.company}', style: TextStyle(color: Colors.grey[600])),
              const SizedBox(height: 16),
              Row(
                children: [
                  _buildSentimentIndicator(recording.sentiment),
                  const SizedBox(width: 12),
                  Text(_formatDuration(recording.duration), style: TextStyle(color: Colors.grey[600])),
                  const SizedBox(width: 12),
                  Text(_formatDate(recording.date), style: TextStyle(color: Colors.grey[600])),
                ],
              ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    IconButton(icon: const Icon(Icons.replay_10), onPressed: () {}),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: const BoxDecoration(color: Color(0xFF7C3AED), shape: BoxShape.circle),
                      child: const Icon(Icons.play_arrow, color: Colors.white, size: 32),
                    ),
                    IconButton(icon: const Icon(Icons.forward_10), onPressed: () {}),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              const Text('Key Insights', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
              const SizedBox(height: 8),
              ...recording.insights.map((insight) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.lightbulb, size: 16, color: Colors.amber),
                    const SizedBox(width: 8),
                    Expanded(child: Text(insight)),
                  ],
                ),
              )),
              const SizedBox(height: 24),
              const Text('Action Items', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
              const SizedBox(height: 8),
              ...recording.actionItems.map((item) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    const Icon(Icons.check_box_outline_blank, size: 18, color: Colors.grey),
                    const SizedBox(width: 8),
                    Expanded(child: Text(item)),
                  ],
                ),
              )),
              const SizedBox(height: 24),
              const Text('Keywords', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: recording.keywords.map((keyword) => Chip(label: Text(keyword), backgroundColor: Colors.grey[100])).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _startRecording() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Starting call recording...')),
    );
  }
}

class CallRecording {
  final String id;
  final String title;
  final String contact;
  final String company;
  final Duration duration;
  final DateTime date;
  final double sentiment;
  final List<String> keywords;
  final double talkRatio;
  final List<String> insights;
  final List<String> actionItems;

  CallRecording({
    required this.id,
    required this.title,
    required this.contact,
    required this.company,
    required this.duration,
    required this.date,
    required this.sentiment,
    required this.keywords,
    required this.talkRatio,
    required this.insights,
    required this.actionItems,
  });
}
