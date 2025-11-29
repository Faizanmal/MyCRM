'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  gamificationAPI,
  Achievement,
  UserPoints,
  Leaderboard,
  Challenge,
} from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import {
  TrophyIcon,
  StarIcon,
  FireIcon,
  ChartBarIcon,
  UsersIcon,
  ArrowPathIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Ranking {
  rank?: number;
  user?: {
    id: string;
    username: string;
    email: string;
  };
  score?: number;
}

export default function GamificationPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'leaderboards' | 'challenges'>('overview');
  const [loading, setLoading] = useState(true);
  
  // User stats
  const [myPoints, setMyPoints] = useState<UserPoints | null>(null);
  const [myAchievements, setMyAchievements] = useState<Achievement[]>([]);
  
  // Achievements
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  
  // Leaderboards
  const [leaderboards, setLeaderboards] = useState<Leaderboard[]>([]);
  const [selectedLeaderboard, setSelectedLeaderboard] = useState<string | null>(null);
  const [rankings, setRankings] = useState<Ranking[]>([]);
  
  // Challenges
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [myChallenges, setMyChallenges] = useState<Challenge[]>([]);

  const loadLeaderboardRankings = useCallback(async (leaderboardId: string) => {
    try {
      const response = await gamificationAPI.getLeaderboardRankings(leaderboardId);
      setRankings(response.data);
    } catch (error) {
      console.error('Failed to load rankings:', error);
    }
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 'overview') {
        const [pointsRes, achievementsRes, challengesRes] = await Promise.all([
          gamificationAPI.getMyPoints(),
          gamificationAPI.getMyAchievements(),
          gamificationAPI.getMyChallenges(),
        ]);
        setMyPoints(pointsRes.data);
        setMyAchievements(achievementsRes.data.results || achievementsRes.data);
        setMyChallenges(challengesRes.data.results || challengesRes.data);
      } else if (activeTab === 'achievements') {
        const response = await gamificationAPI.getAchievements({ is_active: true });
        setAchievements(response.data.results || response.data);
      } else if (activeTab === 'leaderboards') {
        const response = await gamificationAPI.getLeaderboards({ is_active: true });
        const boards = response.data.results || response.data;
        setLeaderboards(boards);
        if (boards.length > 0 && !selectedLeaderboard) {
          setSelectedLeaderboard(boards[0].id);
          loadLeaderboardRankings(boards[0].id);
        }
      } else if (activeTab === 'challenges') {
        const [allChallenges, userChallenges] = await Promise.all([
          gamificationAPI.getChallenges({ status: 'active' }),
          gamificationAPI.getMyChallenges(),
        ]);
        setChallenges(allChallenges.data.results || allChallenges.data);
        setMyChallenges(userChallenges.data.results || userChallenges.data);
      }
    } catch (error) {
      console.error('Failed to load gamification data:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab, selectedLeaderboard, loadLeaderboardRankings]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleJoinChallenge = useCallback(async (challengeId: string) => {
    try {
      await gamificationAPI.joinChallenge(challengeId);
      alert('Successfully joined the challenge!');
      await loadData();
    } catch (error) {
      console.error('Failed to join challenge:', error);
      alert('Failed to join challenge.');
    }
  }, [loadData]);

  const handleLeaveChallenge = useCallback(async (challengeId: string) => {
    if (!confirm('Are you sure you want to leave this challenge?')) {
      return;
    }
    
    try {
      await gamificationAPI.leaveChallenge(challengeId);
      alert('Successfully left the challenge.');
      await loadData();
    } catch (error) {
      console.error('Failed to leave challenge:', error);
      alert('Failed to leave challenge.');
    }
  }, [loadData]);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'legendary':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'hard':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'easy':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getChallengeStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'upcoming':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-96">
            <ArrowPathIcon className="w-12 h-12 text-blue-600 animate-spin" />
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <TrophyIcon className="w-10 h-10 text-yellow-500" />
                  Gamification
                </h1>
                <p className="text-gray-600 mt-2">
                  Track your progress, earn achievements, and compete with your team
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'overview'
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <ChartBarIcon className="w-5 h-5" />
                Overview
              </button>
              <button
                onClick={() => setActiveTab('achievements')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'achievements'
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <StarIcon className="w-5 h-5" />
                Achievements
              </button>
              <button
                onClick={() => setActiveTab('leaderboards')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'leaderboards'
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <UsersIcon className="w-5 h-5" />
                Leaderboards
              </button>
              <button
                onClick={() => setActiveTab('challenges')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'challenges'
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FireIcon className="w-5 h-5" />
                Challenges
              </button>
            </nav>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && myPoints && (
            <div className="space-y-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-linear-to-br from-yellow-400 to-orange-500 text-white">
                  <CardHeader className="pb-2">
                    <CardDescription className="text-yellow-50">Total Points</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{myPoints.total_points.toLocaleString()}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Current Level</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-blue-600">Level {myPoints.current_level}</div>
                    <p className="text-xs text-gray-600 mt-1">
                      {myPoints.points_to_next_level} pts to next level
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Current Streak</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <FireIcon className="w-6 h-6 text-orange-500" />
                      <div className="text-3xl font-bold">{myPoints.streak_days}</div>
                      <span className="text-sm text-gray-600">days</span>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Achievements</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <StarIcon className="w-6 h-6 text-yellow-500" />
                      <div className="text-3xl font-bold">{myPoints.achievements_count}</div>
                      <span className="text-sm text-gray-600">earned</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recent Achievements */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Achievements</CardTitle>
                  <CardDescription>Your latest accomplishments</CardDescription>
                </CardHeader>
                <CardContent>
                  {myAchievements.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No achievements yet. Keep working!</p>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {myAchievements.slice(0, 6).map((achievement) => (
                        <div
                          key={achievement.id}
                          className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg"
                        >
                          <div className="text-3xl">{achievement.icon}</div>
                          <div>
                            <p className="font-semibold text-sm">{achievement.name}</p>
                            <p className="text-xs text-gray-600">+{achievement.points} pts</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Active Challenges */}
              <Card>
                <CardHeader>
                  <CardTitle>Active Challenges</CardTitle>
                  <CardDescription>Challenges you&apos;re currently participating in</CardDescription>
                </CardHeader>
                <CardContent>
                  {myChallenges.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">Not participating in any challenges</p>
                  ) : (
                    <div className="space-y-3">
                      {myChallenges.map((challenge) => (
                        <div
                          key={challenge.id}
                          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                        >
                          <div>
                            <p className="font-semibold">{challenge.name}</p>
                            <p className="text-sm text-gray-600">
                              {challenge.goal_type}: {challenge.goal_value} • +{challenge.reward_points} pts
                            </p>
                            <p className="text-xs text-gray-500">
                              Ends {new Date(challenge.end_date).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge className={getChallengeStatusColor(challenge.status)}>
                            {challenge.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Achievements Tab */}
          {activeTab === 'achievements' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {achievements.map((achievement) => {
                const isEarned = myAchievements.some(a => a.id === achievement.id);
                return (
                  <Card
                    key={achievement.id}
                    className={`hover:shadow-lg transition-shadow ${
                      isEarned ? 'border-2 border-yellow-400' : ''
                    }`}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <div className="text-4xl">{achievement.icon}</div>
                        {isEarned && <CheckCircleIcon className="w-6 h-6 text-green-500" />}
                      </div>
                      <CardTitle className="text-lg">{achievement.name}</CardTitle>
                      <CardDescription>{achievement.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <Badge className={getDifficultyColor(achievement.difficulty)}>
                          {achievement.difficulty}
                        </Badge>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-yellow-600">
                            +{achievement.points}
                          </div>
                          <div className="text-xs text-gray-600">points</div>
                        </div>
                      </div>
                      <div className="mt-3 text-xs text-gray-600">
                        <Badge variant="secondary" className="capitalize">
                          {achievement.category}
                        </Badge>
                        <span className="ml-2">
                          {achievement.earned_by_count} {achievement.earned_by_count === 1 ? 'person' : 'people'} earned
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Leaderboards Tab */}
          {activeTab === 'leaderboards' && (
            <div className="space-y-6">
              {/* Leaderboard Selector */}
              <div className="flex gap-2 flex-wrap">
                {leaderboards.map((board) => (
                  <Button
                    key={board.id}
                    variant={selectedLeaderboard === board.id ? 'default' : 'outline'}
                    onClick={() => {
                      setSelectedLeaderboard(board.id);
                      loadLeaderboardRankings(board.id);
                    }}
                  >
                    {board.name}
                  </Button>
                ))}
              </div>

              {/* Rankings Table */}
              <Card>
                <CardHeader>
                  <CardTitle>
                    {leaderboards.find(b => b.id === selectedLeaderboard)?.name || 'Rankings'}
                  </CardTitle>
                  <CardDescription>
                    {leaderboards.find(b => b.id === selectedLeaderboard)?.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {rankings.length === 0 ? (
                      <p className="text-center text-gray-500 py-8">No rankings available</p>
                    ) : (
                      rankings.map((ranking, index) => (
                        <div
                          key={ranking.user?.id || index}
                          className={`flex items-center justify-between p-4 rounded-lg ${
                            index < 3 ? 'bg-linear-to-r from-yellow-50 to-orange-50' : 'bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center gap-4">
                            <div
                              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                                index === 0
                                  ? 'bg-yellow-400 text-white'
                                  : index === 1
                                  ? 'bg-gray-300 text-white'
                                  : index === 2
                                  ? 'bg-orange-400 text-white'
                                  : 'bg-gray-200 text-gray-700'
                              }`}
                            >
                              {ranking.rank || index + 1}
                            </div>
                            <div>
                              <p className="font-semibold">{ranking.user?.username || 'Unknown'}</p>
                              <p className="text-sm text-gray-600">{ranking.user?.email || ''}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-bold">{ranking.score?.toLocaleString() || 0}</div>
                            <div className="text-xs text-gray-600">points</div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Challenges Tab */}
          {activeTab === 'challenges' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {challenges.map((challenge) => {
                  const isParticipating = myChallenges.some(c => c.id === challenge.id);
                  return (
                    <Card
                      key={challenge.id}
                      className={`hover:shadow-lg transition-shadow ${
                        isParticipating ? 'border-2 border-blue-400' : ''
                      }`}
                    >
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{challenge.name}</CardTitle>
                            <CardDescription>{challenge.description}</CardDescription>
                          </div>
                          <Badge className={getChallengeStatusColor(challenge.status)}>
                            {challenge.status}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Type:</span>
                            <Badge variant="secondary" className="capitalize">
                              {challenge.challenge_type}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Goal:</span>
                            <span className="font-medium">
                              {challenge.goal_type}: {challenge.goal_value}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Reward:</span>
                            <span className="font-bold text-yellow-600">
                              +{challenge.reward_points} pts
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Duration:</span>
                            <span className="font-medium">
                              {new Date(challenge.start_date).toLocaleDateString()} - 
                              {new Date(challenge.end_date).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Participants:</span>
                            <span className="font-medium">{challenge.participants_count}</span>
                          </div>
                          
                          {isParticipating ? (
                            <Button
                              variant="outline"
                              className="w-full"
                              onClick={() => handleLeaveChallenge(challenge.id)}
                            >
                              Leave Challenge
                            </Button>
                          ) : (
                            <Button
                              className="w-full"
                              onClick={() => handleJoinChallenge(challenge.id)}
                              disabled={challenge.status !== 'active'}
                            >
                              Join Challenge
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
