"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  FileSignature, FileText, Upload, Send, Clock, CheckCircle, 
  XCircle, AlertCircle, Eye, Download, PenTool, 
  FilePlus, Search, MoreHorizontal, Calendar, Mail, Shield
} from "lucide-react";

interface Document {
  id: number;
  title: string;
  status: "draft" | "sent" | "viewed" | "signed" | "completed" | "declined" | "expired";
  created_at: string;
  sent_at: string | null;
  expires_at: string | null;
  signers: Signer[];
  document_type: string;
}

interface Signer {
  id: number;
  name: string;
  email: string;
  status: "pending" | "viewed" | "signed" | "declined";
  signed_at: string | null;
  order: number;
}

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  usage_count: number;
  fields_count: number;
}

export default function DocumentEsignPage() {
  const [documents] = useState<Document[]>([
    {
      id: 1,
      title: "Sales Agreement - TechCorp Inc.",
      status: "completed",
      created_at: "2025-11-25T10:00:00Z",
      sent_at: "2025-11-25T10:30:00Z",
      expires_at: null,
      document_type: "Contract",
      signers: [
        { id: 1, name: "John Smith", email: "john@techcorp.com", status: "signed", signed_at: "2025-11-26T14:30:00Z", order: 1 },
        { id: 2, name: "Jane Doe", email: "jane@company.com", status: "signed", signed_at: "2025-11-27T09:15:00Z", order: 2 },
      ]
    },
    {
      id: 2,
      title: "NDA - Startup XYZ",
      status: "sent",
      created_at: "2025-11-28T09:00:00Z",
      sent_at: "2025-11-28T09:30:00Z",
      expires_at: "2025-12-05T23:59:59Z",
      document_type: "NDA",
      signers: [
        { id: 3, name: "Mike Johnson", email: "mike@startupxyz.com", status: "viewed", signed_at: null, order: 1 },
      ]
    },
    {
      id: 3,
      title: "Partnership Agreement - Global Partners",
      status: "viewed",
      created_at: "2025-11-27T14:00:00Z",
      sent_at: "2025-11-27T15:00:00Z",
      expires_at: "2025-12-10T23:59:59Z",
      document_type: "Contract",
      signers: [
        { id: 4, name: "Sarah Wilson", email: "sarah@globalpartners.com", status: "viewed", signed_at: null, order: 1 },
        { id: 5, name: "Tom Brown", email: "tom@globalpartners.com", status: "pending", signed_at: null, order: 2 },
      ]
    },
    {
      id: 4,
      title: "Service Level Agreement",
      status: "draft",
      created_at: "2025-11-29T08:00:00Z",
      sent_at: null,
      expires_at: null,
      document_type: "SLA",
      signers: []
    },
  ]);

  const [templates] = useState<Template[]>([
    { id: 1, name: "Standard NDA", description: "Non-disclosure agreement for business discussions", category: "Legal", usage_count: 45, fields_count: 8 },
    { id: 2, name: "Sales Contract", description: "Standard sales agreement with payment terms", category: "Sales", usage_count: 32, fields_count: 15 },
    { id: 3, name: "Service Agreement", description: "Service level agreement template", category: "Services", usage_count: 28, fields_count: 12 },
    { id: 4, name: "Employment Offer", description: "Job offer letter template", category: "HR", usage_count: 18, fields_count: 10 },
  ]);

  const stats = {
    total: documents.length,
    completed: documents.filter(d => d.status === "completed").length,
    pending: documents.filter(d => ["sent", "viewed"].includes(d.status)).length,
    drafts: documents.filter(d => d.status === "draft").length,
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "signed": return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "sent": return <Send className="w-4 h-4 text-blue-500" />;
      case "viewed": return <Eye className="w-4 h-4 text-purple-500" />;
      case "pending": return <Clock className="w-4 h-4 text-yellow-500" />;
      case "declined": return <XCircle className="w-4 h-4 text-red-500" />;
      case "expired": return <AlertCircle className="w-4 h-4 text-gray-500" />;
      case "draft": return <FileText className="w-4 h-4 text-gray-400" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
      case "signed": return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
      case "sent": return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
      case "viewed": return "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400";
      case "pending": return "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400";
      case "declined": return "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
      case "expired": return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400";
      case "draft": return "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const getSignerProgress = (signers: Signer[]) => {
    if (signers.length === 0) return 0;
    const signed = signers.filter(s => s.status === "signed").length;
    return (signed / signers.length) * 100;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Document & E-Sign
          </h1>
          <p className="text-muted-foreground mt-1">
            Create, send, and track documents for electronic signatures
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </Button>
          <Button className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700">
            <FilePlus className="w-4 h-4 mr-2" />
            New Document
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Documents</p>
                <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{stats.total}</p>
              </div>
              <FileText className="w-10 h-10 text-blue-500 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-green-200 dark:border-green-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600 dark:text-green-400">Completed</p>
                <p className="text-3xl font-bold text-green-700 dark:text-green-300">{stats.completed}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-500 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-950/50 dark:to-yellow-900/30 border-yellow-200 dark:border-yellow-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-600 dark:text-yellow-400">Pending</p>
                <p className="text-3xl font-bold text-yellow-700 dark:text-yellow-300">{stats.pending}</p>
              </div>
              <Clock className="w-10 h-10 text-yellow-500 opacity-80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950/50 dark:to-gray-900/30 border-gray-200 dark:border-gray-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Drafts</p>
                <p className="text-3xl font-bold text-gray-700 dark:text-gray-300">{stats.drafts}</p>
              </div>
              <FileText className="w-10 h-10 text-gray-500 opacity-80" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="documents" className="space-y-4">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>All Documents</CardTitle>
                  <CardDescription>Manage and track your documents</CardDescription>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input placeholder="Search documents..." className="pl-9 w-[250px]" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-4 rounded-lg border bg-card hover:shadow-md transition-all">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                          <FileSignature className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{doc.title}</h3>
                            <Badge className={getStatusColor(doc.status)}>
                              <span className="flex items-center gap-1">
                                {getStatusIcon(doc.status)}
                                {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                              </span>
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              Created: {new Date(doc.created_at).toLocaleDateString()}
                            </span>
                            <Badge variant="outline">{doc.document_type}</Badge>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="ghost">
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {doc.signers.length > 0 && (
                      <div className="mt-4 pt-4 border-t">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Signers ({doc.signers.filter(s => s.status === "signed").length}/{doc.signers.length})</span>
                          <Progress value={getSignerProgress(doc.signers)} className="w-32 h-2" />
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {doc.signers.map((signer) => (
                            <div key={signer.id} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50">
                              <Avatar className="w-6 h-6">
                                <AvatarFallback className="text-xs">
                                  {signer.name.split(" ").map(n => n[0]).join("")}
                                </AvatarFallback>
                              </Avatar>
                              <span className="text-sm">{signer.name}</span>
                              {getStatusIcon(signer.status)}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {doc.expires_at && (
                      <div className="mt-3 flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
                        <AlertCircle className="w-4 h-4" />
                        Expires: {new Date(doc.expires_at).toLocaleDateString()}
                      </div>
                    )}
                    
                    {doc.status === "draft" && (
                      <div className="mt-4 flex gap-2">
                        <Button size="sm" variant="outline">
                          <PenTool className="w-4 h-4 mr-2" />
                          Edit
                        </Button>
                        <Button size="sm" className="bg-gradient-to-r from-indigo-600 to-purple-600">
                          <Send className="w-4 h-4 mr-2" />
                          Send for Signature
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                      <FileText className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <Badge variant="outline">{template.category}</Badge>
                  </div>
                  
                  <h3 className="font-semibold mb-1">{template.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{template.description}</p>
                  
                  <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                    <span>{template.fields_count} fields</span>
                    <span>Used {template.usage_count} times</span>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Eye className="w-4 h-4 mr-2" />
                      Preview
                    </Button>
                    <Button size="sm" className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600">
                      Use Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            <Card className="border-dashed hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6 flex flex-col items-center justify-center min-h-[250px]">
                <FilePlus className="w-12 h-12 text-muted-foreground mb-4" />
                <p className="font-medium">Create Template</p>
                <p className="text-sm text-muted-foreground text-center mt-1">
                  Build reusable document templates
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Activity Tab */}
        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Track all document events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { action: "Document signed", doc: "Sales Agreement - TechCorp Inc.", user: "Jane Doe", time: "2 hours ago", icon: <CheckCircle className="w-4 h-4 text-green-500" /> },
                  { action: "Document viewed", doc: "NDA - Startup XYZ", user: "Mike Johnson", time: "4 hours ago", icon: <Eye className="w-4 h-4 text-purple-500" /> },
                  { action: "Document sent", doc: "Partnership Agreement", user: "You", time: "Yesterday", icon: <Send className="w-4 h-4 text-blue-500" /> },
                  { action: "Reminder sent", doc: "NDA - Startup XYZ", user: "System", time: "Yesterday", icon: <Mail className="w-4 h-4 text-yellow-500" /> },
                  { action: "Document created", doc: "Service Level Agreement", user: "You", time: "Today", icon: <FilePlus className="w-4 h-4 text-gray-500" /> },
                ].map((activity, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="p-2 rounded-full bg-muted">
                      {activity.icon}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-sm text-muted-foreground">{activity.doc}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{activity.user}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Security Banner */}
      <Card className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border-green-200 dark:border-green-800">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/50">
              <Shield className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="font-semibold text-green-700 dark:text-green-300">Bank-Level Security</h3>
              <p className="text-sm text-green-600/80 dark:text-green-400/80">
                All documents are encrypted with AES-256 and signatures are legally binding with audit trails
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
