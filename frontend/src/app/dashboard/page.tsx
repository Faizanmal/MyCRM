'use client';

import { useEffect, useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  UserPlus, 
  TrendingUp, 
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Phone,
  Mail,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Clock,
  Target
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface StatCardProps {
  title: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down';
  icon: React.ElementType;
}

function StatCard({ title, value, change, trend, icon: Icon }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs flex items-center mt-1">
          {trend === 'up' ? (
            <ArrowUpRight className="w-3 h-3 text-green-600 mr-1" />
          ) : (
            <ArrowDownRight className="w-3 h-3 text-red-600 mr-1" />
          )}
          <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
            {change}
          </span>
          <span className="text-muted-foreground ml-1">from last month</span>
        </p>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-6">
            <div className="animate-pulse space-y-6">
              <div className="h-32 bg-gray-200 rounded-lg"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
                ))}
              </div>
            </div>
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Welcome Section */}
          <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-lg p-6 text-white shadow-lg">
            <h2 className="text-2xl lg:text-3xl font-bold mb-2">
              Welcome back, {user?.first_name || user?.username || 'User'}! 👋
            </h2>
            <p className="text-blue-100">Here&apos;s what&apos;s happening with your CRM today.</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            <StatCard
              title="Total Contacts"
              value="1,234"
              change="+12.5%"
              trend="up"
              icon={Users}
            />
            <StatCard
              title="Active Leads"
              value="456"
              change="+8.2%"
              trend="up"
              icon={UserPlus}
            />
            <StatCard
              title="Opportunities"
              value="89"
              change="+23.4%"
              trend="up"
              icon={TrendingUp}
            />
            <StatCard
              title="Revenue"
              value="$45.2K"
              change="+15.3%"
              trend="up"
              icon={DollarSign}
            />
          </div>

          {/* Charts and Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sales Pipeline */}
            <Card>
              <CardHeader>
                <CardTitle>Sales Pipeline</CardTitle>
                <CardDescription>Current opportunities by stage</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Prospecting</span>
                    <span className="text-muted-foreground">24 deals • $128K</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '35%' }}></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Qualification</span>
                    <span className="text-muted-foreground">18 deals • $94K</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '28%' }}></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Proposal</span>
                    <span className="text-muted-foreground">12 deals • $67K</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: '22%' }}></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Negotiation</span>
                    <span className="text-muted-foreground">8 deals • $45K</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '15%' }}></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Wins */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Wins</CardTitle>
                <CardDescription>Deals closed this week</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">Enterprise Package - TechCorp</p>
                    <p className="text-xs text-muted-foreground">$45,000 • Closed yesterday</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">Annual License - StartupXYZ</p>
                    <p className="text-xs text-muted-foreground">$28,500 • Closed 2 days ago</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">Premium Support - GlobalTech</p>
                    <p className="text-xs text-muted-foreground">$12,000 • Closed 3 days ago</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Activity and Tasks */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Activities */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
                <CardDescription>Latest updates from your team</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">New lead added</p>
                    <p className="text-xs text-muted-foreground truncate">Sarah Johnson from TechCorp</p>
                  </div>
                  <span className="text-xs text-muted-foreground flex-shrink-0">2 min ago</span>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">Opportunity updated</p>
                    <p className="text-xs text-muted-foreground truncate">Deal with ABC Company moved to Proposal stage</p>
                  </div>
                  <span className="text-xs text-muted-foreground flex-shrink-0">15 min ago</span>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">Task completed</p>
                    <p className="text-xs text-muted-foreground truncate">Follow up call with XYZ Corp</p>
                  </div>
                  <span className="text-xs text-muted-foreground flex-shrink-0">1 hour ago</span>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-purple-500 rounded-full flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">Meeting scheduled</p>
                    <p className="text-xs text-muted-foreground truncate">Demo with Startup Inc on Friday</p>
                  </div>
                  <span className="text-xs text-muted-foreground flex-shrink-0">2 hours ago</span>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-red-500 rounded-full flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">Lead converted</p>
                    <p className="text-xs text-muted-foreground truncate">Mike Smith converted to customer</p>
                  </div>
                  <span className="text-xs text-muted-foreground flex-shrink-0">3 hours ago</span>
                </div>
              </CardContent>
            </Card>

            {/* Upcoming Tasks */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Tasks</CardTitle>
                <CardDescription>Your priorities for today and tomorrow</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-2 h-2 bg-red-500 rounded-full flex-shrink-0"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">Call prospect</p>
                      <p className="text-xs text-muted-foreground truncate">Mike Smith - TechStart Inc</p>
                    </div>
                  </div>
                  <Badge variant="destructive" className="ml-2 flex-shrink-0">High</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full flex-shrink-0"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">Send proposal</p>
                      <p className="text-xs text-muted-foreground truncate">ABC Corporation</p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="ml-2 flex-shrink-0">Medium</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">Follow up email</p>
                      <p className="text-xs text-muted-foreground truncate">Sarah Wilson - Design Co</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="ml-2 flex-shrink-0">Low</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">Prepare demo</p>
                      <p className="text-xs text-muted-foreground truncate">Enterprise client presentation</p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="ml-2 flex-shrink-0">Medium</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-2 h-2 bg-purple-500 rounded-full flex-shrink-0"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">Review contract</p>
                      <p className="text-xs text-muted-foreground truncate">Legal review for GlobalTech</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="ml-2 flex-shrink-0">Low</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" className="h-24 flex flex-col space-y-2 hover:bg-blue-50 hover:border-blue-300">
                  <UserPlus className="w-6 h-6 text-blue-600" />
                  <span className="text-sm">Add Contact</span>
                </Button>
                
                <Button variant="outline" className="h-24 flex flex-col space-y-2 hover:bg-green-50 hover:border-green-300">
                  <Phone className="w-6 h-6 text-green-600" />
                  <span className="text-sm">Log Call</span>
                </Button>
                
                <Button variant="outline" className="h-24 flex flex-col space-y-2 hover:bg-purple-50 hover:border-purple-300">
                  <Mail className="w-6 h-6 text-purple-600" />
                  <span className="text-sm">Send Email</span>
                </Button>
                
                <Button variant="outline" className="h-24 flex flex-col space-y-2 hover:bg-orange-50 hover:border-orange-300">
                  <Calendar className="w-6 h-6 text-orange-600" />
                  <span className="text-sm">Schedule Meeting</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24.5%</div>
                <div className="mt-2 h-2 bg-gray-200 rounded-full">
                  <div className="h-2 bg-gradient-to-r from-green-500 to-green-600 rounded-full" style={{ width: '24.5%' }}></div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Target: 25%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Response Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2.4h</div>
                <p className="text-xs flex items-center mt-1">
                  <ArrowDownRight className="w-3 h-3 text-green-600 mr-1" />
                  <span className="text-green-600">-18%</span>
                  <span className="text-muted-foreground ml-1">vs last week</span>
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Customer Satisfaction</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4.8/5.0</div>
                <p className="text-xs flex items-center mt-1">
                  <ArrowUpRight className="w-3 h-3 text-green-600 mr-1" />
                  <span className="text-green-600">+0.2</span>
                  <span className="text-muted-foreground ml-1">this month</span>
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
