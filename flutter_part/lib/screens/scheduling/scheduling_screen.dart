import 'package:flutter/material.dart';
import '../../core/utils/api_client.dart';
import '../../services/advanced_services.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class SchedulingScreen extends StatefulWidget {
  const SchedulingScreen({super.key});

  @override
  State<SchedulingScreen> createState() => _SchedulingScreenState();
}

class _SchedulingScreenState extends State<SchedulingScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late SchedulingService _service;
  
  List<ScheduledMeeting> _meetings = [];
  List<SchedulingPage> _pages = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _service = SchedulingService(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final results = await Future.wait([
        _service.getMeetings(),
        _service.getPages(),
      ]);
      setState(() {
        _meetings = results[0] as List<ScheduledMeeting>;
        _pages = results[1] as List<SchedulingPage>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) => [
          SliverAppBar(
            expandedHeight: 180,
            floating: false,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text('Smart Scheduling'),
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.indigo.shade700,
                      Colors.purple.shade600,
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 40),
                        _buildStatsRow(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            bottom: TabBar(
              controller: _tabController,
              indicatorColor: Colors.white,
              tabs: const [
                Tab(text: 'Upcoming'),
                Tab(text: 'Booking Pages'),
                Tab(text: 'Availability'),
              ],
            ),
          ),
        ],
        body: _isLoading
            ? const LoadingIndicator(message: 'Loading schedule...')
            : RefreshIndicator(
                onRefresh: _loadData,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildUpcomingTab(),
                    _buildPagesTab(),
                    _buildAvailabilityTab(),
                  ],
                ),
              ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showBookMeetingDialog(),
        icon: const Icon(Icons.add),
        label: const Text('New Meeting'),
        backgroundColor: Colors.indigo,
      ),
    );
  }

  Widget _buildStatsRow() {
    final today = DateTime.now();
    final todayMeetings = _meetings.where((m) => 
      m.startTime.day == today.day && 
      m.startTime.month == today.month &&
      m.startTime.year == today.year
    ).length;
    final upcomingMeetings = _meetings.where((m) => 
      m.startTime.isAfter(today) && m.status == 'scheduled'
    ).length;

    return Row(
      children: [
        _buildStatCard('$todayMeetings', 'Today', Icons.today),
        const SizedBox(width: 12),
        _buildStatCard('$upcomingMeetings', 'Upcoming', Icons.event),
        const SizedBox(width: 12),
        _buildStatCard('${_pages.length}', 'Pages', Icons.link),
      ],
    );
  }

  Widget _buildStatCard(String value, String label, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  label,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.8),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUpcomingTab() {
    final upcoming = _meetings.where((m) => 
      m.startTime.isAfter(DateTime.now()) && m.status == 'scheduled'
    ).toList()
      ..sort((a, b) => a.startTime.compareTo(b.startTime));

    if (upcoming.isEmpty) {
      return const EmptyState(
        icon: Icons.event_available,
        title: 'No Upcoming Meetings',
        subtitle: 'Your schedule is clear!',
      );
    }

    // Group by date
    final grouped = <String, List<ScheduledMeeting>>{};
    for (final meeting in upcoming) {
      final dateKey = _formatDateKey(meeting.startTime);
      grouped.putIfAbsent(dateKey, () => []).add(meeting);
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: grouped.length,
      itemBuilder: (context, index) {
        final dateKey = grouped.keys.elementAt(index);
        final meetings = grouped[dateKey]!;
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 8, top: 8),
              child: Text(
                dateKey,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade600,
                ),
              ),
            ),
            ...meetings.map((m) => _buildMeetingCard(m)),
          ],
        );
      },
    );
  }

  Widget _buildMeetingCard(ScheduledMeeting meeting) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 4,
              height: 60,
              decoration: BoxDecoration(
                color: Colors.indigo,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    meeting.title,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.person, size: 14, color: Colors.grey.shade600),
                      const SizedBox(width: 4),
                      Text(
                        meeting.attendeeName,
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.access_time, size: 14, color: Colors.grey.shade600),
                      const SizedBox(width: 4),
                      Text(
                        '${_formatTime(meeting.startTime)} - ${_formatTime(meeting.endTime)}',
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Column(
              children: [
                IconButton(
                  icon: Icon(Icons.videocam, color: Colors.indigo.shade400),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Starting video call...')),
                    );
                  },
                ),
                IconButton(
                  icon: Icon(Icons.cancel_outlined, color: Colors.red.shade300),
                  onPressed: () => _showCancelDialog(meeting),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPagesTab() {
    if (_pages.isEmpty) {
      return EmptyState(
        icon: Icons.link_off,
        title: 'No Booking Pages',
        subtitle: 'Create a booking page to share with clients',
        action: ElevatedButton.icon(
          onPressed: () => _showCreatePageDialog(),
          icon: const Icon(Icons.add),
          label: const Text('Create Page'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _pages.length,
      itemBuilder: (context, index) {
        final page = _pages[index];
        return _buildPageCard(page);
      },
    );
  }

  Widget _buildPageCard(SchedulingPage page) {
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
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.indigo.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(Icons.event_note, color: Colors.indigo.shade700),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        page.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        page.description,
                        style: TextStyle(color: Colors.grey.shade600),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Switch(
                  value: page.isActive,
                  onChanged: (value) {
                    // Toggle page active status
                  },
                  activeThumbColor: Colors.indigo,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.link, size: 16, color: Colors.grey.shade600),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'schedule.mycrm.com/${page.slug}',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Link copied!')),
                      );
                    },
                    child: const Text('Copy'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvailabilityTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Working Hours',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          ...['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(
            (day) => _buildDayRow(day, '9:00 AM', '5:00 PM', true),
          ),
          _buildDayRow('Saturday', '-', '-', false),
          _buildDayRow('Sunday', '-', '-', false),
          const SizedBox(height: 24),
          const Text(
            'Buffer Time',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Before meetings'),
                      DropdownButton<int>(
                        value: 15,
                        items: [0, 5, 10, 15, 30].map((min) {
                          return DropdownMenuItem(
                            value: min,
                            child: Text('$min min'),
                          );
                        }).toList(),
                        onChanged: (value) {},
                      ),
                    ],
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('After meetings'),
                      DropdownButton<int>(
                        value: 15,
                        items: [0, 5, 10, 15, 30].map((min) {
                          return DropdownMenuItem(
                            value: min,
                            child: Text('$min min'),
                          );
                        }).toList(),
                        onChanged: (value) {},
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Availability saved!')),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigo,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: const Text('Save Availability'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDayRow(String day, String start, String end, bool isActive) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            SizedBox(
              width: 100,
              child: Text(
                day,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: isActive ? null : Colors.grey,
                ),
              ),
            ),
            Expanded(
              child: isActive
                  ? Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(start),
                        ),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 8),
                          child: Text('-'),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(end),
                        ),
                      ],
                    )
                  : Text(
                      'Unavailable',
                      style: TextStyle(color: Colors.grey.shade500),
                    ),
            ),
            Switch(
              value: isActive,
              onChanged: (value) {},
              activeThumbColor: Colors.indigo,
            ),
          ],
        ),
      ),
    );
  }

  String _formatDateKey(DateTime date) {
    final now = DateTime.now();
    if (date.day == now.day && date.month == now.month && date.year == now.year) {
      return 'Today';
    }
    final tomorrow = now.add(const Duration(days: 1));
    if (date.day == tomorrow.day && date.month == tomorrow.month && date.year == tomorrow.year) {
      return 'Tomorrow';
    }
    final weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${weekdays[date.weekday - 1]}, ${months[date.month - 1]} ${date.day}';
  }

  String _formatTime(DateTime time) {
    final hour = time.hour > 12 ? time.hour - 12 : time.hour;
    final period = time.hour >= 12 ? 'PM' : 'AM';
    return '$hour:${time.minute.toString().padLeft(2, '0')} $period';
  }

  void _showBookMeetingDialog() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Book meeting dialog')),
    );
  }

  void _showCancelDialog(ScheduledMeeting meeting) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Meeting'),
        content: Text('Are you sure you want to cancel "${meeting.title}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Keep'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _service.cancelMeeting(meeting.id).then((_) => _loadData());
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Cancel Meeting'),
          ),
        ],
      ),
    );
  }

  void _showCreatePageDialog() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Create page dialog')),
    );
  }
}
