'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Calendar, 
  Plus,
  Search,
  Filter,
  CheckCircle2,
  Circle,
  Clock,
  Flag,
  User,
  MoreVertical
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  description: string;
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  status: 'todo' | 'in-progress' | 'completed';
  assignedTo: string;
  relatedTo: string;
}

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Follow up with TechCorp',
    description: 'Send proposal and schedule demo',
    dueDate: '2025-11-12',
    priority: 'high',
    status: 'todo',
    assignedTo: 'Sarah Johnson',
    relatedTo: 'TechCorp Deal',
  },
  {
    id: '2',
    title: 'Prepare Q4 Sales Report',
    description: 'Compile sales data and create presentation',
    dueDate: '2025-11-15',
    priority: 'medium',
    status: 'in-progress',
    assignedTo: 'Mike Smith',
    relatedTo: 'Internal',
  },
  {
    id: '3',
    title: 'Call potential lead',
    description: 'Initial outreach to StartupXYZ',
    dueDate: '2025-11-10',
    priority: 'high',
    status: 'todo',
    assignedTo: 'Sarah Johnson',
    relatedTo: 'StartupXYZ Lead',
  },
  {
    id: '4',
    title: 'Update CRM records',
    description: 'Clean up duplicate contacts',
    dueDate: '2025-11-18',
    priority: 'low',
    status: 'todo',
    assignedTo: 'John Davis',
    relatedTo: 'Data Maintenance',
  },
  {
    id: '5',
    title: 'Client onboarding call',
    description: 'Welcome call for new customer',
    dueDate: '2025-11-08',
    priority: 'high',
    status: 'completed',
    assignedTo: 'Mike Smith',
    relatedTo: 'GlobalTech',
  },
];

export default function TasksPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const filteredTasks = mockTasks.filter(task => {
    const matchesSearch = 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in-progress': return 'bg-blue-100 text-blue-800';
      case 'todo': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'in-progress': return <Clock className="w-5 h-5 text-blue-600" />;
      case 'todo': return <Circle className="w-5 h-5 text-gray-400" />;
      default: return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const isOverdue = (dueDate: string, status: string) => {
    return status !== 'completed' && new Date(dueDate) < new Date();
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Tasks & Calendar</h1>
              <p className="text-gray-500 mt-1">Manage your tasks and schedule</p>
            </div>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              New Task
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">
                  {mockTasks.filter(t => t.status === 'todo').length}
                </div>
                <p className="text-xs text-muted-foreground">To Do</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-600">
                  {mockTasks.filter(t => t.status === 'in-progress').length}
                </div>
                <p className="text-xs text-muted-foreground">In Progress</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-600">
                  {mockTasks.filter(t => t.status === 'completed').length}
                </div>
                <p className="text-xs text-muted-foreground">Completed</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-red-600">
                  {mockTasks.filter(t => isOverdue(t.dueDate, t.status)).length}
                </div>
                <p className="text-xs text-muted-foreground">Overdue</p>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search tasks..."
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Filter className="w-4 h-4 mr-2" />
                      Status: {filterStatus === 'all' ? 'All' : filterStatus}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setFilterStatus('all')}>
                      All Tasks
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setFilterStatus('todo')}>
                      To Do
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setFilterStatus('in-progress')}>
                      In Progress
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setFilterStatus('completed')}>
                      Completed
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardContent>
          </Card>

          {/* Tasks List */}
          <div className="space-y-3">
            {filteredTasks.map((task) => (
              <Card key={task.id} className={`hover:shadow-md transition-shadow ${
                isOverdue(task.dueDate, task.status) ? 'border-l-4 border-l-red-500' : ''
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="pt-1">
                      {getStatusIcon(task.status)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div>
                          <h3 className="font-semibold text-gray-900">{task.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Mark as Complete</DropdownMenuItem>
                            <DropdownMenuItem>Change Priority</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-sm">
                        <div className="flex items-center gap-1">
                          <Calendar className={`w-4 h-4 ${
                            isOverdue(task.dueDate, task.status) ? 'text-red-500' : 'text-gray-400'
                          }`} />
                          <span className={isOverdue(task.dueDate, task.status) ? 'text-red-600 font-medium' : 'text-gray-600'}>
                            {new Date(task.dueDate).toLocaleDateString()}
                            {isOverdue(task.dueDate, task.status) && ' (Overdue)'}
                          </span>
                        </div>

                        <div className="flex items-center gap-1">
                          <Flag className={`w-4 h-4 ${getPriorityColor(task.priority)}`} />
                          <span className={getPriorityColor(task.priority)}>
                            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
                          </span>
                        </div>

                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{task.assignedTo}</span>
                        </div>

                        <Badge className={getStatusColor(task.status)}>
                          {task.status.replace('-', ' ')}
                        </Badge>

                        <span className="text-gray-500 text-xs">
                          {task.relatedTo}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredTasks.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No tasks found matching your criteria.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
