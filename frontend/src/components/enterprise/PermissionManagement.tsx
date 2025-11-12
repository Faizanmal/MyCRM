// Permission Management Component
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Shield, Users, Lock, Settings, Search, Plus, Edit, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

interface Permission {
  id: string;
  user: number;
  permission: string;
  is_granted: boolean;
  granted_by: number;
  reason: string;
  is_active: boolean;
  expires_at?: string;
}

interface PermissionGroup {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  is_active: boolean;
  user_count: number;
}

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

export default function PermissionManagement() {
  const [activeTab, setActiveTab] = useState('permissions');
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [groups, setGroups] = useState<PermissionGroup[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState<number | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<Set<string>>(new Set());
  const [groupEditOpen, setGroupEditOpen] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const { toast } = useToast();

  const PERMISSION_CATEGORIES = {
    'Contacts': ['contacts.view', 'contacts.create', 'contacts.edit', 'contacts.delete', 'contacts.export'],
    'Leads': ['leads.view', 'leads.create', 'leads.edit', 'leads.delete', 'leads.assign', 'leads.convert'],
    'Opportunities': ['opportunities.view', 'opportunities.create', 'opportunities.edit', 'opportunities.delete'],
    'Tasks': ['tasks.view', 'tasks.create', 'tasks.edit', 'tasks.delete', 'tasks.assign'],
    'Reports': ['reports.view', 'reports.create', 'reports.export', 'reports.schedule'],
    'System': ['system.settings', 'system.audit', 'system.integrations', 'system.security'],
  };

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [permsRes, groupsRes, usersRes] = await Promise.all([
        axios.get('/api/core/user-permissions/'),
        axios.get('/api/core/permission-groups/'),
        axios.get('/api/users/'),
      ]);
      setPermissions(permsRes.data.results || permsRes.data);
      setGroups(groupsRes.data.results || groupsRes.data);
      setUsers(usersRes.data.results || usersRes.data);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load permissions data';
      console.error('Fetch data error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const grantPermission = async (userId: number, permission: string, reason: string) => {
    try {
      await axios.post('/api/core/user-permissions/', {
        user: userId,
        permission,
        is_granted: true,
        reason,
      });
      toast({
        title: 'Success',
        description: 'Permission granted successfully',
      });
      fetchData();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to grant permission';
      console.error('Grant permission error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const revokePermission = async (permissionId: string) => {
    try {
      await axios.delete(`/api/core/user-permissions/${permissionId}/`);
      toast({
        title: 'Success',
        description: 'Permission revoked successfully',
      });
      fetchData();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to revoke permission';
      console.error('Revoke permission error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const createGroup = async (groupData: Partial<PermissionGroup>) => {
    try {
      await axios.post('/api/core/permission-groups/', groupData);
      toast({
        title: 'Success',
        description: 'Permission group created successfully',
      });
      fetchData();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create permission group';
      console.error('Create group error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const togglePermissionSelection = (permission: string) => {
    const newSet = new Set(selectedPermissions);
    if (newSet.has(permission)) {
      newSet.delete(permission);
    } else {
      newSet.add(permission);
    }
    setSelectedPermissions(newSet);
  };

  const handleEditGroup = async () => {
    if (selectedPermissions.size === 0 || !newGroupName) {
      toast({
        title: 'Error',
        description: 'Please enter a group name and select permissions',
        variant: 'destructive',
      });
      return;
    }
    
    await createGroup({
      name: newGroupName,
      description: `Group with selected permissions`,
      permissions: Array.from(selectedPermissions),
    });
    
    setGroupEditOpen(false);
    setNewGroupName('');
    setSelectedPermissions(new Set());
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Permission Management
            {loading && <span className="text-sm text-muted-foreground ml-2">(Loading...)</span>}
          </h1>
          <p className="text-muted-foreground mt-1">Manage user permissions and access control</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="permissions">
            <Lock className="h-4 w-4 mr-2" />
            Permissions
          </TabsTrigger>
          <TabsTrigger value="groups">
            <Users className="h-4 w-4 mr-2" />
            Permission Groups
          </TabsTrigger>
          <TabsTrigger value="users">
            <Users className="h-4 w-4 mr-2" />
            User Permissions
          </TabsTrigger>
        </TabsList>

        {/* Permissions Tab */}
        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Available Permissions</CardTitle>
              <CardDescription>All system permissions organized by category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {Object.entries(PERMISSION_CATEGORIES).map(([category, perms]) => (
                  <div key={category} className="space-y-2">
                    <h3 className="font-semibold text-lg">{category}</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                      {perms.map((perm) => (
                        <div key={perm} className="flex items-center gap-2">
                          <Checkbox 
                            id={perm}
                            checked={selectedPermissions.has(perm)}
                            onCheckedChange={() => togglePermissionSelection(perm)}
                          />
                          <Badge variant="outline" className="text-xs cursor-pointer">
                            {perm}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              {selectedPermissions.size > 0 && (
                <div className="mt-6 pt-6 border-t">
                  <Dialog open={groupEditOpen} onOpenChange={setGroupEditOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <Edit className="h-4 w-4 mr-2" />
                        Create Group with Selected ({selectedPermissions.size})
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Create Permission Group</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="group-name">Group Name</Label>
                          <Input
                            id="group-name"
                            value={newGroupName}
                            onChange={(e) => setNewGroupName(e.target.value)}
                            placeholder="e.g., Sales Manager"
                          />
                        </div>
                        <Button onClick={handleEditGroup} className="w-full">
                          Create Group
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permission Groups Tab */}
        <TabsContent value="groups" className="space-y-4">
          <div className="flex justify-between items-center gap-2">
            <div className="flex-1 max-w-sm relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search groups..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8"
              />
            </div>
            <CreateGroupDialog onSuccess={fetchData} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {groups
              .filter((g) => g.name.toLowerCase().includes(searchTerm.toLowerCase()))
              .map((group) => (
                <Card key={group.id}>
                  <CardHeader>
                    <CardTitle className="flex justify-between items-center">
                      {group.name}
                      <Badge>{group.user_count} users</Badge>
                    </CardTitle>
                    <CardDescription>{group.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Permissions:</p>
                      <div className="flex flex-wrap gap-1">
                        {group.permissions.slice(0, 5).map((perm) => (
                          <Badge key={perm} variant="secondary" className="text-xs">
                            {perm}
                          </Badge>
                        ))}
                        {group.permissions.length > 5 && (
                          <Badge variant="secondary" className="text-xs">
                            +{group.permissions.length - 5} more
                          </Badge>
                        )}
                      </div>
                      <Button variant="outline" size="sm" className="w-full mt-4">
                        <Edit className="h-4 w-4 mr-2" />
                        Edit Group
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        {/* User Permissions Tab */}
        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Permissions</CardTitle>
              <CardDescription>Manage individual user permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <Select onValueChange={(value) => setSelectedUser(Number(value))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a user" />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredUsers.map((user) => (
                      <SelectItem key={user.id} value={user.id.toString()}>
                        {user.username} ({user.role})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {selectedUser && (
                  <UserPermissionsEditor
                    userId={selectedUser}
                    permissions={permissions.filter((p) => p.user === selectedUser)}
                    onGrant={grantPermission}
                    onRevoke={revokePermission}
                  />
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Create Group Dialog Component
function CreateGroupDialog({ onSuccess }: { onSuccess: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post('/api/core/permission-groups/', {
        name,
        description,
        permissions: selectedPermissions,
        is_active: true,
      });
      toast({
        title: 'Success',
        description: 'Permission group created successfully',
      });
      setOpen(false);
      setName('');
      setDescription('');
      setSelectedPermissions([]);
      onSuccess();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create permission group';
      console.error('Create group error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Group
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Permission Group</DialogTitle>
          <DialogDescription>Create a new permission group to manage access control</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Group Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Sales Team"
              required
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of this group"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Group</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// User Permissions Editor Component
function UserPermissionsEditor({
  userId,
  permissions,
  onGrant,
  onRevoke,
}: {
  userId: number;
  permissions: Permission[];
  onGrant: (userId: number, permission: string, reason: string) => void;
  onRevoke: (permissionId: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Current Permissions</h3>
      <div className="space-y-2">
        {permissions.map((perm) => (
          <div key={perm.id} className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex-1">
              <p className="font-medium">{perm.permission}</p>
              {perm.reason && <p className="text-sm text-muted-foreground">{perm.reason}</p>}
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={perm.is_granted ? 'default' : 'destructive'}>
                {perm.is_granted ? 'Granted' : 'Revoked'}
              </Badge>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => {
                  onRevoke(perm.id);
                  onGrant(userId, perm.permission, 'User action to revoke');
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
        {permissions.length === 0 && (
          <p className="text-center text-muted-foreground py-8">No custom permissions assigned</p>
        )}
      </div>
    </div>
  );
}
