'use client';

// FIXME: Add all missing imports for components and icons.
import { useRouter } from 'next/navigation';
import {
  Search, Bell, LogOut, BarChart3, Users, UserPlus,
  TrendingUp, Calendar, Mail, Settings, Phone,
  Puzzle, Sparkles, Trophy, MessageSquare, Shield
} from 'lucide-react'; // (Or your icon library)

import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
// (Import any other components you use)

// We are keeping these imports for now, but the router and useEffect are removed below.
import ProtectedRoute from "@/components/ProtectedRoute";

// If this is your main dashboard page, you can name it DashboardPage,
// or keep 'Home' if it's the file 'app/dashboard/page.tsx'
export default function Home() {
  const router = useRouter();
  // const router = useRouter(); // No longer needed if this IS the dashboard

  // FIXME: This redirect was incorrect.
  // A dashboard page should not redirect to itself.
  // I have removed this logic.
  /*
  useEffect(() => {
    // Redirect to dashboard
    router.replace('/dashboard');
  }, [router]);
  */

  // FIXME: You must provide the 'user' object and 'logout' function.
  // They might come from a context or a custom hook, e.g.:
  // const { user, logout } = useAuth();
  
  // Placeholder data so the file runs without errors:
  const user = { 
    first_name: 'Jane', 
    last_name: 'Doe', 
    username: 'janedoe' 
  };
  const logout = () => { 
    console.log("Logging out..."); 
  };
  
  // The main error was that all the UI code below was *outside*
  // the component. I have moved it inside the 'return' statement
  // and wrapped it in the <ProtectedRoute>.
  return (
    <ProtectedRoute>
      <div className="flex flex-col min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">CRM</span>
                </div>
                <h1 className="text-xl font-semibold text-gray-900">MyCRM</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search contacts, leads, opportunities..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <Button variant="ghost" size="sm">
                <Bell className="w-5 h-5" />
              </Button>
              
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-700">
                    {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                  </span>
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {user?.first_name && user?.last_name 
                    ? `${user.first_name} ${user.last_name}` 
                    : user?.username || 'User'
                  }
                </span>
                <Button variant="ghost" size="sm" onClick={logout}>
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        <div className="flex flex-1">
          {/* Sidebar */}
          <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
            <nav className="p-4 space-y-2">
              <div className="space-y-1">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Main</h3>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/dashboard')}
                >
                  <BarChart3 className="w-4 h-4 mr-3" />
                  Dashboard
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/contacts')}
                >
                  <Users className="w-4 h-4 mr-3" />
                  Contacts
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/leads')}
                >
                  <UserPlus className="w-4 h-4 mr-3" />
                  Leads
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/opportunities')}
                >
                  <TrendingUp className="w-4 h-4 mr-3" />
                  Opportunities
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/tasks')}
                >
                  <Calendar className="w-4 h-4 mr-3" />
                  Tasks & Calendar
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/communications')}
                >
                  <Mail className="w-4 h-4 mr-3" />
                  Communications
                </Button>
              </div>
              
              <div className="space-y-1 mt-6">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Advanced</h3>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/integration-hub')}
                >
                  <Puzzle className="w-4 h-4 mr-3" />
                  Integration Hub
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/ai-insights')}
                >
                  <Sparkles className="w-4 h-4 mr-3" />
                  AI Insights
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/gamification')}
                >
                  <Trophy className="w-4 h-4 mr-3" />
                  Gamification
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/organizations')}
                >
                  <Users className="w-4 h-4 mr-3" />
                  Organizations
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/collaboration')}
                >
                  <MessageSquare className="w-4 h-4 mr-3" />
                  Collaboration
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/gdpr-compliance')}
                >
                  <Shield className="w-4 h-4 mr-3" />
                  GDPR Compliance
                </Button>
              </div>
              
              <div className="space-y-1 mt-6">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Tools</h3>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/sso-settings')}
                >
                  <Settings className="w-4 h-4 mr-3" />
                  SSO Settings
                </Button>
                
                <Button 
                  variant="ghost" 
                  className="w-full justify-start text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={() => router.push('/settings')}
                >
                  <Settings className="w-4 h-4 mr-3" />
                  Settings
                </Button>
              </div>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 p-6">
            <div className="space-y-6">
              {/* Welcome Section */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6 text-white">
                <h2 className="text-2xl font-bold mb-2">
                  Welcome back, {user?.first_name || user?.username || 'User'}!
                </h2>
                <p className="text-blue-100">Here&apos;s what&apos;s happening with your CRM today.</p>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Contacts</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">1,234</div>
                    <p className="text-xs text-muted-foreground">
                      +12% from last month
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Leads</CardTitle>
                    <UserPlus className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">456</div>
                    <p className="text-xs text-muted-foreground">
                      +8% from last month
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Opportunities</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">89</div>
                    <p className="text-xs text-muted-foreground">
                      +23% from last month
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                    <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">$45,231</div>
                    <p className="text-xs text-muted-foreground">
                      +15% from last month
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Activities</CardTitle>
                    <CardDescription>Latest updates from your CRM</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">New lead added</p>
                        <p className="text-xs text-gray-500">Sarah Johnson from TechCorp</p>
                      </div>
                      <span className="text-xs text-gray-400">2 min ago</span>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Opportunity updated</p>
                        <p className="text-xs text-gray-500">Deal with ABC Company moved to Proposal stage</p>
                      </div>
                      <span className="text-xs text-gray-400">15 min ago</span>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Task completed</p>
                        <p className="text-xs text-gray-500">Follow up call with XYZ Corp</p>
                      </div>
                      <span className="text-xs text-gray-400">1 hour ago</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Upcoming Tasks</CardTitle>
                    <CardDescription>Tasks due today and tomorrow</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium">Call prospect</p>
                          <p className="text-xs text-gray-500">Mike Smith - TechStart Inc</p>
                        </div>
                      </div>
                      <Badge variant="destructive">High</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium">Send proposal</p>
                          <p className="text-xs text-gray-500">ABC Corporation</p>
                        </div>
                      </div>
                      <Badge variant="secondary">Medium</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium">Follow up email</p>
                          <p className="text-xs text-gray-500">Sarah Wilson - Design Co</p>
                        </div>
                      </div>
                      <Badge variant="outline">Low</Badge>
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
                    <Button variant="outline" className="h-20 flex flex-col space-y-2">
                      <UserPlus className="w-6 h-6" />
                      <span>Add Contact</span>
                    </Button>
                    
                    <Button variant="outline" className="h-20 flex flex-col space-y-2">
                      <Phone className="w-6 h-6" />
                      <span>Log Call</span>
                    </Button>
                    
                    <Button variant="outline" className="h-20 flex flex-col space-y-2">
                      <Mail className="w-6 h-6" />
                      <span>Send Email</span>
                    </Button>
                    
                    <Button variant="outline" className="h-20 flex flex-col space-y-2">
                      <Calendar className="w-6 h-6" />
                      <span>Schedule Meeting</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}