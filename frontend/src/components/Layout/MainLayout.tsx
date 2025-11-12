'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { 
  BarChart3, 
  Users, 
  UserPlus, 
  TrendingUp, 
  Calendar, 
  Mail,
  Settings,
  Bell,
  Search,
  LogOut,
  Menu,
  X,
  FileText,
  Workflow,
  Shield,
  Upload,
  Zap
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'Contacts', href: '/contacts', icon: Users },
  { name: 'Leads', href: '/leads', icon: UserPlus },
  { name: 'Opportunities', href: '/opportunities', icon: TrendingUp },
  { name: 'Tasks', href: '/tasks', icon: Calendar },
  { name: 'Communications', href: '/communications', icon: Mail },
];

const toolsNavigation = [
  { name: 'Workflows', href: '/workflows', icon: Workflow },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Email Campaigns', href: '/campaigns', icon: Zap },
  { name: 'Import/Export', href: '/data', icon: Upload },
  { name: 'Security', href: '/security', icon: Shield },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 lg:px-6 py-4 sticky top-0 z-40">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:flex"
            >
              <Menu className="w-5 h-5" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>

            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">C</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900 hidden sm:block">MyCRM</h1>
            </Link>
          </div>
          
          <div className="flex items-center space-x-2 lg:space-x-4">
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 w-64 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
            
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-5 h-5" />
              <Badge className="absolute -top-1 -right-1 px-1 min-w-5 h-5 flex items-center justify-center text-xs">
                3
              </Badge>
            </Button>
            
            <div className="flex items-center space-x-2 pl-2 border-l">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                </span>
              </div>
              <span className="text-sm font-medium text-gray-700 hidden sm:block">
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}` 
                  : user?.username || 'User'
                }
              </span>
              <Button variant="ghost" size="sm" onClick={logout} title="Logout">
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Desktop Sidebar */}
        <aside 
          className={cn(
            "hidden lg:block bg-white border-r border-gray-200 transition-all duration-300 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto",
            sidebarOpen ? "w-64" : "w-20"
          )}
        >
          <nav className="p-4 space-y-6">
            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3",
                !sidebarOpen && "text-center"
              )}>
                {sidebarOpen ? 'Main' : 'M'}
              </h3>
              
              {navigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start",
                        isActive 
                          ? "bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700" 
                          : "text-gray-700 hover:bg-gray-50",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3")} />
                      {sidebarOpen && item.name}
                    </Button>
                  </Link>
                );
              })}
            </div>
            
            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3",
                !sidebarOpen && "text-center"
              )}>
                {sidebarOpen ? 'Tools' : 'T'}
              </h3>
              
              {toolsNavigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start",
                        isActive 
                          ? "bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700" 
                          : "text-gray-700 hover:bg-gray-50",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3")} />
                      {sidebarOpen && item.name}
                    </Button>
                  </Link>
                );
              })}
            </div>
          </nav>
        </aside>

        {/* Mobile Sidebar */}
        {mobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-50 bg-black bg-opacity-50" onClick={() => setMobileMenuOpen(false)}>
            <aside 
              className="absolute left-0 top-0 bottom-0 w-64 bg-white shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b flex items-center justify-between">
                <h2 className="font-semibold text-gray-900">Menu</h2>
                <Button variant="ghost" size="sm" onClick={() => setMobileMenuOpen(false)}>
                  <X className="w-5 h-5" />
                </Button>
              </div>
              
              <nav className="p-4 space-y-6">
                <div className="space-y-1">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Main
                  </h3>
                  
                  {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start",
                            isActive 
                              ? "bg-blue-50 text-blue-600" 
                              : "text-gray-700"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          {item.name}
                        </Button>
                      </Link>
                    );
                  })}
                </div>
                
                <div className="space-y-1">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Tools
                  </h3>
                  
                  {toolsNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start",
                            isActive 
                              ? "bg-blue-50 text-blue-600" 
                              : "text-gray-700"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          {item.name}
                        </Button>
                      </Link>
                    );
                  })}
                </div>
              </nav>
            </aside>
          </div>
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
