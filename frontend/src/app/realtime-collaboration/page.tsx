'use client';

import { useState, useEffect } from 'react';
import { 
  FileEdit, 
  Plus, 
  Search, 
  Share2,
  Clock, 
  Eye, 
  Edit3,
  Trash2,
  Copy,
  Link,
  Lock,
  Globe,
  FileText,
  FolderOpen,
  History,
  UserPlus,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
// import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { realtimeCollabAPI } from '@/lib/api';

interface CollabDocument {
  id: string;
  title: string;
  content: string;
  document_type: string;
  owner: {
    id: string;
    name: string;
    avatar: string;
  };
  collaborators: {
    id: string;
    name: string;
    avatar: string;
    permission: 'view' | 'edit' | 'admin';
    online: boolean;
  }[];
  created_at: string;
  updated_at: string;
  is_public: boolean;
  version: number;
}

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  preview: string;
}

interface Collaboration {
  id: string;
  document: CollabDocument;
  role: 'owner' | 'editor' | 'viewer';
  last_accessed: string;
}

export default function RealtimeCollaborationPage() {
  const [documents, setDocuments] = useState<CollabDocument[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [myCollaborations, setMyCollaborations] = useState<Collaboration[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState<CollabDocument | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocType, setNewDocType] = useState('document');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [docsData, templatesData, collabsData] = await Promise.all([
        realtimeCollabAPI.getDocuments(),
        realtimeCollabAPI.getTemplates(),
        realtimeCollabAPI.getMyCollaborations(),
      ]);
      setDocuments(docsData.results || docsData || []);
      setTemplates(templatesData.results || templatesData || []);
      setMyCollaborations(collabsData.results || collabsData || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      // Demo data
      setDocuments([
        {
          id: '1',
          title: 'Q1 Sales Strategy',
          content: 'Strategic planning document for Q1 2026...',
          document_type: 'document',
          owner: { id: '1', name: 'John Doe', avatar: '' },
          collaborators: [
            { id: '2', name: 'Jane Smith', avatar: '', permission: 'edit', online: true },
            { id: '3', name: 'Bob Wilson', avatar: '', permission: 'view', online: false },
          ],
          created_at: '2026-01-05T10:00:00Z',
          updated_at: '2026-01-12T14:30:00Z',
          is_public: false,
          version: 12,
        },
        {
          id: '2',
          title: 'Product Launch Proposal',
          content: 'Proposal for new product launch in Q2...',
          document_type: 'proposal',
          owner: { id: '1', name: 'John Doe', avatar: '' },
          collaborators: [
            { id: '4', name: 'Alice Brown', avatar: '', permission: 'edit', online: true },
            { id: '5', name: 'Charlie Davis', avatar: '', permission: 'edit', online: true },
          ],
          created_at: '2026-01-08T09:00:00Z',
          updated_at: '2026-01-12T11:00:00Z',
          is_public: false,
          version: 8,
        },
        {
          id: '3',
          title: 'Customer Onboarding Guide',
          content: 'Step-by-step guide for customer onboarding...',
          document_type: 'guide',
          owner: { id: '2', name: 'Jane Smith', avatar: '' },
          collaborators: [
            { id: '1', name: 'John Doe', avatar: '', permission: 'edit', online: false },
          ],
          created_at: '2026-01-10T14:00:00Z',
          updated_at: '2026-01-11T16:00:00Z',
          is_public: true,
          version: 5,
        },
      ]);
      setTemplates([
        { id: '1', name: 'Sales Proposal', description: 'Professional sales proposal template', category: 'Sales', preview: '' },
        { id: '2', name: 'Meeting Notes', description: 'Structured meeting notes template', category: 'Meetings', preview: '' },
        { id: '3', name: 'Project Plan', description: 'Comprehensive project planning template', category: 'Projects', preview: '' },
        { id: '4', name: 'Customer Report', description: 'Customer status report template', category: 'Reports', preview: '' },
      ]);
      setMyCollaborations([
        {
          id: '1',
          document: {
            id: '1',
            title: 'Q1 Sales Strategy',
            content: '',
            document_type: 'document',
            owner: { id: '1', name: 'John Doe', avatar: '' },
            collaborators: [],
            created_at: '2026-01-05T10:00:00Z',
            updated_at: '2026-01-12T14:30:00Z',
            is_public: false,
            version: 12,
          },
          role: 'owner',
          last_accessed: '2026-01-12T14:30:00Z',
        },
        {
          id: '2',
          document: {
            id: '2',
            title: 'Product Launch Proposal',
            content: '',
            document_type: 'proposal',
            owner: { id: '1', name: 'John Doe', avatar: '' },
            collaborators: [],
            created_at: '2026-01-08T09:00:00Z',
            updated_at: '2026-01-12T11:00:00Z',
            is_public: false,
            version: 8,
          },
          role: 'owner',
          last_accessed: '2026-01-12T11:00:00Z',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const createDocument = async () => {
    try {
      const newDoc = await realtimeCollabAPI.createDocument({
        title: newDocTitle,
        document_type: newDocType,
        content: '',
      });
      setDocuments([newDoc, ...documents]);
      setIsCreateDialogOpen(false);
      setNewDocTitle('');
    } catch (error) {
      console.error('Failed to create document:', error);
      // Demo: add locally
      const demoDoc: CollabDocument = {
        id: Date.now().toString(),
        title: newDocTitle,
        content: '',
        document_type: newDocType,
        owner: { id: '1', name: 'You', avatar: '' },
        collaborators: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_public: false,
        version: 1,
      };
      setDocuments([demoDoc, ...documents]);
      setIsCreateDialogOpen(false);
      setNewDocTitle('');
    }
  };

  const deleteDocument = async (id: string) => {
    try {
      await realtimeCollabAPI.deleteDocument(id);
      setDocuments(documents.filter(d => d.id !== id));
    } catch (error) {
      console.error('Failed to delete document:', error);
      setDocuments(documents.filter(d => d.id !== id));
    }
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'proposal':
        return <FileText className="h-5 w-5 text-blue-500" />;
      case 'guide':
        return <FolderOpen className="h-5 w-5 text-green-500" />;
      default:
        return <FileEdit className="h-5 w-5 text-purple-500" />;
    }
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <FileEdit className="h-8 w-8" />
            Realtime Collaboration
          </h1>
          <p className="text-muted-foreground">
            Create and collaborate on documents in real-time
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Document
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Document</DialogTitle>
              <DialogDescription>
                Start a new collaborative document from scratch or use a template.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Document Title</Label>
                <Input
                  placeholder="Enter document title..."
                  value={newDocTitle}
                  onChange={(e) => setNewDocTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Document Type</Label>
                <Select value={newDocType} onValueChange={setNewDocType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="document">Document</SelectItem>
                    <SelectItem value="proposal">Proposal</SelectItem>
                    <SelectItem value="guide">Guide</SelectItem>
                    <SelectItem value="report">Report</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
              <Button onClick={createDocument} disabled={!newDocTitle.trim()}>Create Document</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search documents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      <Tabs defaultValue="documents">
        <TabsList>
          <TabsTrigger value="documents">All Documents</TabsTrigger>
          <TabsTrigger value="recent">Recent</TabsTrigger>
          <TabsTrigger value="shared">Shared with Me</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="mt-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredDocuments.map((doc) => (
                <Card key={doc.id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedDocument(doc)}>
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        {getDocumentTypeIcon(doc.document_type)}
                        <div>
                          <CardTitle className="text-base">{doc.title}</CardTitle>
                          <p className="text-xs text-muted-foreground">
                            by {doc.owner.name}
                          </p>
                        </div>
                      </div>
                      {doc.is_public ? (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <Globe className="h-3 w-3" />
                          Public
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="flex items-center gap-1">
                          <Lock className="h-3 w-3" />
                          Private
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {doc.content || 'No content yet...'}
                    </p>
                    
                    {/* Collaborators */}
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center -space-x-2">
                        {doc.collaborators.slice(0, 4).map((collab) => (
                          <Avatar key={collab.id} className="h-8 w-8 border-2 border-background">
                            <AvatarImage src={collab.avatar} />
                            <AvatarFallback className={collab.online ? 'bg-green-100' : ''}>
                              {getInitials(collab.name)}
                            </AvatarFallback>
                          </Avatar>
                        ))}
                        {doc.collaborators.length > 4 && (
                          <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-xs border-2 border-background">
                            +{doc.collaborators.length - 4}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {new Date(doc.updated_at).toLocaleDateString()}
                      </div>
                    </div>

                    {/* Online indicators */}
                    {doc.collaborators.some(c => c.online) && (
                      <div className="flex items-center gap-1 mt-2">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        <span className="text-xs text-green-600">
                          {doc.collaborators.filter(c => c.online).length} online
                        </span>
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="pt-2">
                    <div className="flex gap-2 w-full">
                      <Button variant="outline" size="sm" className="flex-1" onClick={(e) => { e.stopPropagation(); setSelectedDocument(doc); }}>
                        <Edit3 className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setSelectedDocument(doc); setIsShareDialogOpen(true); }}>
                        <Share2 className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="recent" className="mt-6">
          <div className="space-y-4">
            {myCollaborations.map((collab) => (
              <Card key={collab.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {getDocumentTypeIcon(collab.document.document_type)}
                      <div>
                        <p className="font-medium">{collab.document.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">{collab.role}</Badge>
                          <span className="text-xs text-muted-foreground">
                            Last accessed: {new Date(collab.last_accessed).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Edit3 className="h-4 w-4 mr-1" />
                        Open
                      </Button>
                      <Button variant="ghost" size="sm">
                        <History className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="shared" className="mt-6">
          <div className="space-y-4">
            {documents.filter(d => d.collaborators.length > 0).map((doc) => (
              <Card key={doc.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {getDocumentTypeIcon(doc.document_type)}
                      <div>
                        <p className="font-medium">{doc.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-sm text-muted-foreground">
                            Shared by {doc.owner.name}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            • {doc.collaborators.length} collaborators
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center -space-x-2">
                        {doc.collaborators.slice(0, 3).map((collab) => (
                          <Avatar key={collab.id} className="h-8 w-8 border-2 border-background">
                            <AvatarFallback>{getInitials(collab.name)}</AvatarFallback>
                          </Avatar>
                        ))}
                      </div>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="templates" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  <div className="bg-muted rounded-lg h-32 flex items-center justify-center mb-4">
                    <FileText className="h-12 w-12 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium mb-1">{template.name}</h3>
                  <p className="text-sm text-muted-foreground mb-2">{template.description}</p>
                  <Badge variant="outline" className="text-xs">{template.category}</Badge>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" className="w-full" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Use Template
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Share Dialog */}
      <Dialog open={isShareDialogOpen} onOpenChange={setIsShareDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Share Document</DialogTitle>
            <DialogDescription>
              Invite others to collaborate on this document.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex gap-2">
              <Input placeholder="Enter email addresses..." className="flex-1" />
              <Select defaultValue="edit">
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="view">Can view</SelectItem>
                  <SelectItem value="edit">Can edit</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
              <Button>
                <UserPlus className="h-4 w-4" />
              </Button>
            </div>

            <div className="border rounded-lg p-4">
              <p className="text-sm font-medium mb-3">People with access</p>
              {selectedDocument?.collaborators.map((collab) => (
                <div key={collab.id} className="flex items-center justify-between py-2">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>{getInitials(collab.name)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-medium">{collab.name}</p>
                      <p className="text-xs text-muted-foreground">{collab.permission}</p>
                    </div>
                  </div>
                  <Select defaultValue={collab.permission}>
                    <SelectTrigger className="w-28 h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="view">Can view</SelectItem>
                      <SelectItem value="edit">Can edit</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="remove">Remove</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
              <Link className="h-4 w-4 text-muted-foreground" />
              <Input 
                value={`https://crm.example.com/collab/${selectedDocument?.id}`} 
                readOnly 
                className="text-sm"
              />
              <Button variant="outline" size="sm">
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsShareDialogOpen(false)}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

