'use client';

import React from 'react';
// import { useQuery } from '@tanstack/react-query';
import {
  Trophy,
  Medal,
  Target,
  Flame,
  Zap,
  Crown,
  Gift,
  Users,
  Award,
  Heart,
  Sparkles,
  ArrowUp,
  ArrowDown,
  Minus,
  Clock,
  Send,
} from 'lucide-react';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

// Types
interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  points: number;
  progress: number;
  isCompleted: boolean;
  completedAt?: string;
  isSecret: boolean;
  tier: number;
}

interface Challenge {
  id: string;
  name: string;
  description: string;
  type: string;
  goalType: string;
  goalTarget: number;
  goalUnit: string;
  currentValue: number;
  startDate: string;
  endDate: string;
  reward: {
    points: number;
    badge?: string;
    prize?: string;
  };
  participantCount: number;
  isAiGenerated: boolean;
  difficulty: string;
}

interface LeaderboardEntry {
  rank: number;
  previousRank: number | null;
  user: {
    id: string;
    name: string;
    avatar?: string;
    title: string;
  };
  value: number;
  metric: string;
}

interface Recognition {
  id: string;
  sender: { name: string; avatar?: string };
  recipient: { name: string; avatar?: string };
  type: string;
  message: string;
  points: number;
  createdAt: string;
  reactions: Record<string, number>;
}

interface UserStats {
  level: number;
  title: string;
  totalXp: number;
  xpProgress: number;
  xpForNextLevel: number;
  coins: number;
  streaks: { type: string; count: number; best: number }[];
  achievementsCount: number;
  totalAchievements: number;
  challengesWon: number;
}

// Mock data
const mockUserStats: UserStats = {
  level: 12,
  title: 'Sales Champion',
  totalXp: 4850,
  xpProgress: 350,
  xpForNextLevel: 500,
  coins: 2400,
  streaks: [
    { type: 'login', count: 15, best: 45 },
    { type: 'activity', count: 8, best: 22 },
    { type: 'deal', count: 3, best: 12 },
  ],
  achievementsCount: 24,
  totalAchievements: 50,
  challengesWon: 7,
};

const mockAchievements: Achievement[] = [
  {
    id: '1',
    name: 'First Deal',
    description: 'Close your first deal',
    icon: 'trophy',
    category: 'sales',
    rarity: 'common',
    points: 50,
    progress: 100,
    isCompleted: true,
    completedAt: '2024-01-15',
    isSecret: false,
    tier: 1,
  },
  {
    id: '2',
    name: 'Deal Master',
    description: 'Close 100 deals',
    icon: 'target',
    category: 'sales',
    rarity: 'epic',
    points: 500,
    progress: 67,
    isCompleted: false,
    isSecret: false,
    tier: 3,
  },
  {
    id: '3',
    name: 'Million Dollar Club',
    description: 'Reach $1M in closed revenue',
    icon: 'crown',
    category: 'milestone',
    rarity: 'legendary',
    points: 1000,
    progress: 45,
    isCompleted: false,
    isSecret: false,
    tier: 1,
  },
  {
    id: '4',
    name: 'Team Player',
    description: 'Send 50 recognitions to teammates',
    icon: 'heart',
    category: 'teamwork',
    rarity: 'rare',
    points: 200,
    progress: 80,
    isCompleted: false,
    isSecret: false,
    tier: 2,
  },
  {
    id: '5',
    name: '???',
    description: 'Complete a hidden challenge',
    icon: 'sparkles',
    category: 'special',
    rarity: 'legendary',
    points: 500,
    progress: 0,
    isCompleted: false,
    isSecret: true,
    tier: 1,
  },
];

const mockChallenges: Challenge[] = [
  {
    id: '1',
    name: 'March Madness',
    description: 'Close the most deals this month',
    type: 'leaderboard',
    goalType: 'deals_closed',
    goalTarget: 20,
    goalUnit: 'deals',
    currentValue: 12,
    startDate: '2024-03-01',
    endDate: '2024-03-31',
    reward: { points: 500, badge: 'March Champion', prize: '$500 Amazon Gift Card' },
    participantCount: 45,
    isAiGenerated: false,
    difficulty: 'hard',
  },
  {
    id: '2',
    name: 'Pipeline Builder',
    description: 'AI-generated challenge based on your performance',
    type: 'individual',
    goalType: 'pipeline_value',
    goalTarget: 250000,
    goalUnit: 'dollars',
    currentValue: 180000,
    startDate: '2024-03-10',
    endDate: '2024-03-17',
    reward: { points: 150 },
    participantCount: 1,
    isAiGenerated: true,
    difficulty: 'medium',
  },
  {
    id: '3',
    name: 'Team Challenge: Q1 Sprint',
    description: 'Collaborate with your team to hit the quarterly target',
    type: 'team',
    goalType: 'revenue',
    goalTarget: 1000000,
    goalUnit: 'dollars',
    currentValue: 720000,
    startDate: '2024-01-01',
    endDate: '2024-03-31',
    reward: { points: 1000, badge: 'Q1 Champions' },
    participantCount: 8,
    isAiGenerated: false,
    difficulty: 'hard',
  },
];

const mockLeaderboard: LeaderboardEntry[] = [
  { rank: 1, previousRank: 2, user: { id: '1', name: 'Sarah Johnson', title: 'Sales Champion', avatar: '' }, value: 5200, metric: 'xp' },
  { rank: 2, previousRank: 1, user: { id: '2', name: 'Mike Chen', title: 'Deal Closer', avatar: '' }, value: 4850, metric: 'xp' },
  { rank: 3, previousRank: 3, user: { id: '3', name: 'Emily Davis', title: 'Rising Star', avatar: '' }, value: 4500, metric: 'xp' },
  { rank: 4, previousRank: 6, user: { id: '4', name: 'David Wilson', title: 'Pipeline Pro', avatar: '' }, value: 4200, metric: 'xp' },
  { rank: 5, previousRank: 4, user: { id: '5', name: 'Lisa Brown', title: 'Activity King', avatar: '' }, value: 3900, metric: 'xp' },
];

const mockRecognitions: Recognition[] = [
  {
    id: '1',
    sender: { name: 'Sarah Johnson' },
    recipient: { name: 'Mike Chen' },
    type: 'great_job',
    message: 'Amazing work closing that enterprise deal! Your persistence really paid off.',
    points: 10,
    createdAt: '2024-03-15T10:30:00',
    reactions: { '👏': 5, '🔥': 3, '⭐': 2 },
  },
  {
    id: '2',
    sender: { name: 'David Wilson' },
    recipient: { name: 'Emily Davis' },
    type: 'teamwork',
    message: 'Thanks for helping me prepare for my presentation. Couldn\'t have done it without you!',
    points: 10,
    createdAt: '2024-03-14T16:45:00',
    reactions: { '❤️': 4, '👍': 2 },
  },
];

// Utility Components
const RarityBadge: React.FC<{ rarity: Achievement['rarity'] }> = ({ rarity }) => {
  const colors = {
    common: 'bg-gray-100 text-gray-800',
    uncommon: 'bg-green-100 text-green-800',
    rare: 'bg-blue-100 text-blue-800',
    epic: 'bg-purple-100 text-purple-800',
    legendary: 'bg-yellow-100 text-yellow-800 border border-yellow-300',
  };

  return (
    <Badge className={colors[rarity]}>{rarity.charAt(0).toUpperCase() + rarity.slice(1)}</Badge>
  );
};

const RankChange: React.FC<{ current: number; previous: number | null }> = ({ current, previous }) => {
  if (!previous) return null;
  
  const diff = previous - current;
  
  if (diff > 0) {
    return (
      <span className="flex items-center text-green-600 text-sm">
        <ArrowUp className="h-3 w-3" />
        {diff}
      </span>
    );
  } else if (diff < 0) {
    return (
      <span className="flex items-center text-red-600 text-sm">
        <ArrowDown className="h-3 w-3" />
        {Math.abs(diff)}
      </span>
    );
  }
  
  return <Minus className="h-3 w-3 text-gray-400" />;
};

// Tab Components
const OverviewTab: React.FC<{ stats: UserStats }> = ({ stats }) => (
  <div className="space-y-6">
    {/* Level Card */}
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-6">
          <div className="relative">
            <div className="h-24 w-24 rounded-full bg-linear-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
              <span className="text-3xl font-bold text-white">{stats.level}</span>
            </div>
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-2 py-0.5 rounded-full text-xs">
              {stats.title}
            </div>
          </div>
          <div className="flex-1 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Level Progress</span>
              <span className="text-sm font-medium">
                {stats.xpProgress} / {stats.xpForNextLevel} XP
              </span>
            </div>
            <Progress value={(stats.xpProgress / stats.xpForNextLevel) * 100} />
            <div className="flex gap-6">
              <div>
                <p className="text-2xl font-bold">{stats.totalXp.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">Total XP</p>
              </div>
              <div>
                <p className="text-2xl font-bold flex items-center gap-1">
                  <span className="text-yellow-500">🪙</span> {stats.coins.toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">Coins</p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    {/* Stats Grid */}
    <div className="grid grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4 text-center">
          <Trophy className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
          <p className="text-2xl font-bold">{stats.achievementsCount}</p>
          <p className="text-sm text-muted-foreground">Achievements</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 text-center">
          <Target className="h-8 w-8 mx-auto mb-2 text-blue-500" />
          <p className="text-2xl font-bold">{stats.challengesWon}</p>
          <p className="text-sm text-muted-foreground">Challenges Won</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 text-center">
          <Flame className="h-8 w-8 mx-auto mb-2 text-orange-500" />
          <p className="text-2xl font-bold">{stats.streaks[0]?.count || 0}</p>
          <p className="text-sm text-muted-foreground">Day Streak</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 text-center">
          <Medal className="h-8 w-8 mx-auto mb-2 text-purple-500" />
          <p className="text-2xl font-bold">#2</p>
          <p className="text-sm text-muted-foreground">Leaderboard</p>
        </CardContent>
      </Card>
    </div>

    {/* Streaks */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="h-5 w-5 text-orange-500" />
          Active Streaks
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          {stats.streaks.map((streak) => (
            <div key={streak.type} className="p-4 rounded-lg bg-muted/50 text-center">
              <p className="text-3xl font-bold text-orange-500">{streak.count}</p>
              <p className="text-sm capitalize">{streak.type} Streak</p>
              <p className="text-xs text-muted-foreground">Best: {streak.best} days</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const AchievementsTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <div className="flex gap-2">
        <Button variant="outline" size="sm">All</Button>
        <Button variant="ghost" size="sm">Completed</Button>
        <Button variant="ghost" size="sm">In Progress</Button>
      </div>
      <Badge variant="secondary">24 / 50 Unlocked</Badge>
    </div>

    <div className="grid grid-cols-2 gap-4">
      {mockAchievements.map((achievement) => (
        <Card
          key={achievement.id}
          className={`${achievement.isCompleted ? '' : 'opacity-80'} ${
            achievement.isSecret && !achievement.isCompleted ? 'bg-muted/50' : ''
          }`}
        >
          <CardContent className="p-4">
            <div className="flex items-start gap-4">
              <div
                className={`h-14 w-14 rounded-lg flex items-center justify-center ${
                  achievement.rarity === 'legendary'
                    ? 'bg-linear-to-br from-yellow-400 to-orange-500'
                    : achievement.rarity === 'epic'
                    ? 'bg-linear-to-br from-purple-400 to-purple-600'
                    : achievement.rarity === 'rare'
                    ? 'bg-linear-to-br from-blue-400 to-blue-600'
                    : 'bg-muted'
                }`}
              >
                {achievement.isSecret && !achievement.isCompleted ? (
                  <span className="text-2xl">❓</span>
                ) : (
                  <Trophy
                    className={`h-7 w-7 ${
                      achievement.rarity === 'legendary' || achievement.rarity === 'epic'
                        ? 'text-white'
                        : 'text-muted-foreground'
                    }`}
                  />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-medium">
                    {achievement.isSecret && !achievement.isCompleted
                      ? 'Secret Achievement'
                      : achievement.name}
                  </h4>
                  <RarityBadge rarity={achievement.rarity} />
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  {achievement.isSecret && !achievement.isCompleted
                    ? 'Complete special conditions to unlock'
                    : achievement.description}
                </p>
                {!achievement.isCompleted && !achievement.isSecret && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span>Progress</span>
                      <span>{achievement.progress}%</span>
                    </div>
                    <Progress value={achievement.progress} className="h-1.5" />
                  </div>
                )}
                {achievement.isCompleted && (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <Award className="h-4 w-4" />
                    <span>+{achievement.points} XP earned</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  </div>
);

const ChallengesTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <div className="flex gap-2">
        <Button variant="outline" size="sm">Active</Button>
        <Button variant="ghost" size="sm">Completed</Button>
        <Button variant="ghost" size="sm">Upcoming</Button>
      </div>
      <Button>
        <Sparkles className="h-4 w-4 mr-2" />
        AI Suggest Challenge
      </Button>
    </div>

    <div className="space-y-4">
      {mockChallenges.map((challenge) => (
        <Card key={challenge.id}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-3">
                <div
                  className={`h-12 w-12 rounded-lg flex items-center justify-center ${
                    challenge.type === 'team'
                      ? 'bg-purple-100'
                      : challenge.type === 'leaderboard'
                      ? 'bg-yellow-100'
                      : 'bg-blue-100'
                  }`}
                >
                  {challenge.type === 'team' ? (
                    <Users className="h-6 w-6 text-purple-600" />
                  ) : challenge.type === 'leaderboard' ? (
                    <Crown className="h-6 w-6 text-yellow-600" />
                  ) : (
                    <Target className="h-6 w-6 text-blue-600" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{challenge.name}</h4>
                    {challenge.isAiGenerated && (
                      <Badge variant="secondary" className="text-xs">
                        <Sparkles className="h-3 w-3 mr-1" />
                        AI Generated
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">{challenge.description}</p>
                </div>
              </div>
              <Badge variant="outline">{challenge.difficulty}</Badge>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>
                  {challenge.currentValue.toLocaleString()} / {challenge.goalTarget.toLocaleString()}{' '}
                  {challenge.goalUnit}
                </span>
                <span className="font-medium">
                  {Math.round((challenge.currentValue / challenge.goalTarget) * 100)}%
                </span>
              </div>
              <Progress value={(challenge.currentValue / challenge.goalTarget) * 100} />
            </div>

            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  {challenge.participantCount} participants
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Ends {new Date(challenge.endDate).toLocaleDateString()}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-500" />
                <span className="font-medium">+{challenge.reward.points} XP</span>
                {challenge.reward.prize && (
                  <Badge className="bg-green-100 text-green-800">{challenge.reward.prize}</Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  </div>
);

const LeaderboardTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <div className="flex gap-2">
        <Button variant="outline" size="sm">Weekly</Button>
        <Button variant="ghost" size="sm">Monthly</Button>
        <Button variant="ghost" size="sm">All Time</Button>
      </div>
      <div className="text-sm text-muted-foreground">
        Updated 5 minutes ago
      </div>
    </div>

    <Card>
      <CardContent className="p-0">
        <div className="divide-y">
          {mockLeaderboard.map((entry, index) => (
            <div
              key={entry.user.id}
              className={`flex items-center gap-4 p-4 ${index < 3 ? 'bg-muted/30' : ''}`}
            >
              <div className="w-8 text-center">
                {index === 0 ? (
                  <span className="text-2xl">🥇</span>
                ) : index === 1 ? (
                  <span className="text-2xl">🥈</span>
                ) : index === 2 ? (
                  <span className="text-2xl">🥉</span>
                ) : (
                  <span className="text-lg font-bold text-muted-foreground">#{entry.rank}</span>
                )}
              </div>
              <Avatar className="h-10 w-10">
                <AvatarImage src={entry.user.avatar} />
                <AvatarFallback>{entry.user.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <p className="font-medium">{entry.user.name}</p>
                <p className="text-sm text-muted-foreground">{entry.user.title}</p>
              </div>
              <div className="text-right">
                <p className="font-bold">{entry.value.toLocaleString()} XP</p>
                <RankChange current={entry.rank} previous={entry.previousRank} />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const RecognitionTab: React.FC = () => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="h-5 w-5 text-red-500" />
          Give Recognition
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            {['kudos', 'great_job', 'teamwork', 'innovation', 'leadership'].map((type) => (
              <Button key={type} variant="outline" size="sm" className="capitalize">
                {type.replace('_', ' ')}
              </Button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Write a message..."
              className="flex-1 px-3 py-2 border rounded-lg"
            />
            <Button>
              <Send className="h-4 w-4 mr-2" />
              Send
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Recent Recognitions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {mockRecognitions.map((rec) => (
          <div key={rec.id} className="p-4 rounded-lg border">
            <div className="flex items-start gap-3">
              <Avatar>
                <AvatarFallback>{rec.sender.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <p className="text-sm">
                  <span className="font-medium">{rec.sender.name}</span>
                  <span className="text-muted-foreground"> gave </span>
                  <Badge variant="secondary" className="capitalize mx-1">
                    {rec.type.replace('_', ' ')}
                  </Badge>
                  <span className="text-muted-foreground"> to </span>
                  <span className="font-medium">{rec.recipient.name}</span>
                </p>
                <p className="mt-2">{rec.message}</p>
                <div className="flex items-center gap-4 mt-3">
                  <div className="flex gap-2">
                    {Object.entries(rec.reactions).map(([emoji, count]) => (
                      <button
                        key={emoji}
                        className="px-2 py-1 rounded-full bg-muted text-sm hover:bg-muted/80"
                      >
                        {emoji} {count}
                      </button>
                    ))}
                    <button className="px-2 py-1 rounded-full bg-muted text-sm hover:bg-muted/80">
                      +
                    </button>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(rec.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  </div>
);

// Main Component
export default function GamificationDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Trophy className="h-8 w-8 text-yellow-500" />
            Gamification Center
          </h1>
          <p className="text-muted-foreground mt-1">
            Earn points, complete challenges, and climb the leaderboard
          </p>
        </div>
        <Button>
          <Gift className="h-4 w-4 mr-2" />
          Rewards Store
        </Button>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="achievements" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Achievements
          </TabsTrigger>
          <TabsTrigger value="challenges" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Challenges
          </TabsTrigger>
          <TabsTrigger value="leaderboard" className="flex items-center gap-2">
            <Crown className="h-4 w-4" />
            Leaderboard
          </TabsTrigger>
          <TabsTrigger value="recognition" className="flex items-center gap-2">
            <Heart className="h-4 w-4" />
            Recognition
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4">
          <OverviewTab stats={mockUserStats} />
        </TabsContent>

        <TabsContent value="achievements" className="mt-4">
          <AchievementsTab />
        </TabsContent>

        <TabsContent value="challenges" className="mt-4">
          <ChallengesTab />
        </TabsContent>

        <TabsContent value="leaderboard" className="mt-4">
          <LeaderboardTab />
        </TabsContent>

        <TabsContent value="recognition" className="mt-4">
          <RecognitionTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

