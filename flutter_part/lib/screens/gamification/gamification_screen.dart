import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class GamificationScreen extends StatefulWidget {
  const GamificationScreen({super.key});

  @override
  State<GamificationScreen> createState() => _GamificationScreenState();
}

class _GamificationScreenState extends State<GamificationScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late GamificationProvider _provider;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _provider = GamificationProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await _provider.loadAll();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _provider,
      child: Scaffold(
        body: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) => [
            SliverAppBar(
              expandedHeight: 260,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text('Gamification'),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.amber.shade600,
                        Colors.orange.shade700,
                      ],
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Consumer<GamificationProvider>(
                        builder: (context, provider, _) {
                          final points = provider.myPoints;
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 40),
                              _buildUserStats(points),
                              if (points != null) ...[
                                const SizedBox(height: 16),
                                _buildLevelProgress(points),
                              ],
                            ],
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
              bottom: TabBar(
                controller: _tabController,
                indicatorColor: Colors.white,
                isScrollable: true,
                tabs: const [
                  Tab(text: 'Overview'),
                  Tab(text: 'Achievements'),
                  Tab(text: 'Leaderboards'),
                  Tab(text: 'Challenges'),
                ],
              ),
            ),
          ],
          body: Consumer<GamificationProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading) {
                return const LoadingIndicator(message: 'Loading gamification...');
              }

              return RefreshIndicator(
                onRefresh: _loadData,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildOverviewTab(provider),
                    _buildAchievementsTab(provider),
                    _buildLeaderboardsTab(provider),
                    _buildChallengesTab(provider),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildUserStats(UserPoints? points) {
    return Row(
      children: [
        _buildStatCard(
          '🏆',
          '${points?.totalPoints ?? 0}',
          'Points',
          Colors.white,
        ),
        const SizedBox(width: 12),
        _buildStatCard(
          '⭐',
          'Level ${points?.currentLevel ?? 1}',
          'Current',
          Colors.white,
        ),
        const SizedBox(width: 12),
        _buildStatCard(
          '🔥',
          '${points?.streakDays ?? 0}',
          'Day Streak',
          Colors.white,
        ),
        const SizedBox(width: 12),
        _buildStatCard(
          '🏅',
          '${points?.achievementsCount ?? 0}',
          'Badges',
          Colors.white,
        ),
      ],
    );
  }

  Widget _buildStatCard(String emoji, String value, String label, Color textColor) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 20)),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                color: textColor,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                color: textColor.withValues(alpha: 0.8),
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLevelProgress(UserPoints points) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Level ${points.currentLevel}',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              '${points.pointsToNextLevel} to Level ${points.currentLevel + 1}',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
                fontSize: 12,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: points.levelProgress,
          backgroundColor: Colors.white.withValues(alpha: 0.3),
          valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
          borderRadius: BorderRadius.circular(4),
          minHeight: 8,
        ),
      ],
    );
  }

  Widget _buildOverviewTab(GamificationProvider provider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Recent Achievements',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          if (provider.achievements.isEmpty)
            const Text('No achievements yet')
          else
            SizedBox(
              height: 120,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: provider.achievements.take(5).length,
                itemBuilder: (context, index) {
                  final achievement = provider.achievements[index];
                  return _buildAchievementPreview(achievement);
                },
              ),
            ),
          const SizedBox(height: 24),
          const Text(
            'Active Challenges',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          if (provider.challenges.where((c) => c.status == 'active').isEmpty)
            const Text('No active challenges')
          else
            ...provider.challenges
                .where((c) => c.status == 'active')
                .take(3)
                .map((challenge) => _buildChallengeCard(challenge, provider)),
          const SizedBox(height: 24),
          const Text(
            'Top Performers',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          if (provider.leaderboards.isEmpty)
            const Text('No leaderboards available')
          else
            _buildQuickLeaderboard(provider),
        ],
      ),
    );
  }

  Widget _buildAchievementPreview(Achievement achievement) {
    Color difficultyColor;
    switch (achievement.difficulty) {
      case 'legendary':
        difficultyColor = Colors.purple;
        break;
      case 'hard':
        difficultyColor = Colors.red;
        break;
      case 'medium':
        difficultyColor = Colors.orange;
        break;
      default:
        difficultyColor = Colors.green;
    }

    return Container(
      width: 100,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: difficultyColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: difficultyColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(achievement.icon, style: const TextStyle(fontSize: 32)),
          const SizedBox(height: 8),
          Text(
            achievement.name,
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
          ),
          Text(
            '+${achievement.points}',
            style: TextStyle(
              color: difficultyColor,
              fontWeight: FontWeight.bold,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAchievementsTab(GamificationProvider provider) {
    if (provider.achievements.isEmpty) {
      return const EmptyState(
        icon: Icons.emoji_events_outlined,
        title: 'No Achievements',
        subtitle: 'Complete actions to earn achievements',
      );
    }

    // Group by category
    final grouped = <String, List<Achievement>>{};
    for (final achievement in provider.achievements) {
      grouped.putIfAbsent(achievement.category, () => []).add(achievement);
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: grouped.entries.map((entry) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 12, top: 8),
              child: Text(
                entry.key.toUpperCase(),
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade600,
                  letterSpacing: 1,
                ),
              ),
            ),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                childAspectRatio: 0.85,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemCount: entry.value.length,
              itemBuilder: (context, index) {
                return _buildAchievementCard(entry.value[index]);
              },
            ),
            const SizedBox(height: 16),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildAchievementCard(Achievement achievement) {
    final isEarned = achievement.isEarned ?? false;
    Color difficultyColor;
    switch (achievement.difficulty) {
      case 'legendary':
        difficultyColor = Colors.purple;
        break;
      case 'hard':
        difficultyColor = Colors.red;
        break;
      case 'medium':
        difficultyColor = Colors.orange;
        break;
      default:
        difficultyColor = Colors.green;
    }

    return GestureDetector(
      onTap: () => _showAchievementDetails(achievement),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isEarned
              ? difficultyColor.withValues(alpha: 0.1)
              : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isEarned
                ? difficultyColor.withValues(alpha: 0.3)
                : Colors.grey.shade300,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              children: [
                Text(
                  achievement.icon,
                  style: TextStyle(
                    fontSize: 36,
                    color: isEarned ? null : Colors.grey,
                  ),
                ),
                if (isEarned)
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: Container(
                      padding: const EdgeInsets.all(2),
                      decoration: const BoxDecoration(
                        color: Colors.green,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.check, size: 12, color: Colors.white),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              achievement.name,
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: isEarned ? null : Colors.grey,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: difficultyColor.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                '+${achievement.points}',
                style: TextStyle(
                  color: difficultyColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLeaderboardsTab(GamificationProvider provider) {
    if (provider.leaderboards.isEmpty) {
      return const EmptyState(
        icon: Icons.leaderboard_outlined,
        title: 'No Leaderboards',
        subtitle: 'Leaderboards will appear here',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.leaderboards.length,
      itemBuilder: (context, index) {
        final leaderboard = provider.leaderboards[index];
        return _buildLeaderboardCard(leaderboard, provider);
      },
    );
  }

  Widget _buildLeaderboardCard(Leaderboard leaderboard, GamificationProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.amber.shade400, Colors.orange.shade500],
              ),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            ),
            child: Row(
              children: [
                const Icon(Icons.emoji_events, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        leaderboard.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        '${leaderboard.timePeriod.toUpperCase()} • ${leaderboard.metricType.replaceAll('_', ' ').toUpperCase()}',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.8),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          FutureBuilder<List<LeaderboardEntry>>(
            future: provider.loadLeaderboardRankings(leaderboard.id),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                );
              }

              final rankings = snapshot.data ?? [];
              if (rankings.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Text('No rankings yet'),
                );
              }

              return Column(
                children: rankings.take(5).map((entry) {
                  Color? rankColor;
                  if (entry.rank == 1) rankColor = Colors.amber;
                  if (entry.rank == 2) rankColor = Colors.grey.shade400;
                  if (entry.rank == 3) rankColor = Colors.brown.shade300;

                  return ListTile(
                    leading: CircleAvatar(
                      backgroundColor: rankColor ?? Colors.blue.shade100,
                      child: Text(
                        '#${entry.rank}',
                        style: TextStyle(
                          color: rankColor != null ? Colors.white : Colors.blue,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    title: Text(entry.user.username),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          '${entry.score}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        if (entry.change != 0) ...[
                          const SizedBox(width: 4),
                          Icon(
                            entry.change > 0 ? Icons.arrow_upward : Icons.arrow_downward,
                            size: 14,
                            color: entry.change > 0 ? Colors.green : Colors.red,
                          ),
                        ],
                      ],
                    ),
                  );
                }).toList(),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildQuickLeaderboard(GamificationProvider provider) {
    final firstLeaderboard = provider.leaderboards.first;
    return _buildLeaderboardCard(firstLeaderboard, provider);
  }

  Widget _buildChallengesTab(GamificationProvider provider) {
    if (provider.challenges.isEmpty) {
      return const EmptyState(
        icon: Icons.flag_outlined,
        title: 'No Challenges',
        subtitle: 'Challenges will appear here',
      );
    }

    final activeChallenges = provider.challenges.where((c) => c.status == 'active').toList();
    final upcomingChallenges = provider.challenges.where((c) => c.status == 'upcoming').toList();
    final completedChallenges = provider.challenges.where((c) => c.status == 'completed').toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (activeChallenges.isNotEmpty) ...[
          _buildSectionHeader('Active', Icons.play_arrow, Colors.green),
          ...activeChallenges.map((c) => _buildChallengeCard(c, provider)),
        ],
        if (upcomingChallenges.isNotEmpty) ...[
          _buildSectionHeader('Upcoming', Icons.schedule, Colors.blue),
          ...upcomingChallenges.map((c) => _buildChallengeCard(c, provider)),
        ],
        if (completedChallenges.isNotEmpty) ...[
          _buildSectionHeader('Completed', Icons.check_circle, Colors.grey),
          ...completedChallenges.map((c) => _buildChallengeCard(c, provider)),
        ],
      ],
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 12),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChallengeCard(Challenge challenge, GamificationProvider provider) {
    final isActive = challenge.status == 'active';
    final isParticipating = challenge.isParticipating ?? false;

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
                    color: challenge.challengeType == 'team'
                        ? Colors.blue.shade50
                        : Colors.purple.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    challenge.challengeType == 'team' ? Icons.groups : Icons.person,
                    color: challenge.challengeType == 'team'
                        ? Colors.blue
                        : Colors.purple,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        challenge.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        challenge.description,
                        style: TextStyle(color: Colors.grey.shade600),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.star, size: 14, color: Colors.amber),
                      const SizedBox(width: 4),
                      Text(
                        '+${challenge.rewardPoints}',
                        style: TextStyle(
                          color: Colors.amber.shade800,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (isActive && challenge.currentProgress != null) ...[
              Row(
                children: [
                  Expanded(
                    child: LinearProgressIndicator(
                      value: challenge.progressPercent,
                      backgroundColor: Colors.grey.shade200,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.amber.shade600),
                      borderRadius: BorderRadius.circular(4),
                      minHeight: 8,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    '${challenge.currentProgress}/${challenge.goalValue}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 12),
            ],
            Row(
              children: [
                Icon(Icons.people, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  '${challenge.participantsCount} participants',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                const Spacer(),
                if (isActive)
                  isParticipating
                      ? OutlinedButton(
                          onPressed: () => provider.leaveChallenge(challenge.id),
                          child: const Text('Leave'),
                        )
                      : ElevatedButton(
                          onPressed: () => provider.joinChallenge(challenge.id),
                          child: const Text('Join'),
                        ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showAchievementDetails(Achievement achievement) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(achievement.icon, style: const TextStyle(fontSize: 64)),
            const SizedBox(height: 16),
            Text(
              achievement.name,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              achievement.description,
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildDetailChip('Category', achievement.category),
                const SizedBox(width: 12),
                _buildDetailChip('Difficulty', achievement.difficulty),
                const SizedBox(width: 12),
                _buildDetailChip('Points', '+${achievement.points}'),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Earned by ${achievement.earnedByCount} users',
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: TextStyle(color: Colors.grey.shade600, fontSize: 10),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}
