// Email Campaign Manager Component
'use client';

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Mail, Send, BarChart3, FileText, Plus, Play, Pause } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

interface EmailCampaign {
  id: string;
  name: string;
  subject: string;
  status: 'draft' | 'scheduled' | 'running' | 'completed' | 'paused';
  sent_count: number;
  open_count: number;
  click_count: number;
  recipient_count: number;
  scheduled_at?: string;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  html_content: string;
  plain_content: string;
}

export default function EmailCampaignManager() {
  const [campaigns, setCampaigns] = useState<EmailCampaign[]>([]);
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const loadCampaigns = useCallback(async () => {
    try {
      const response = await axios.get('/api/core/email-campaigns/');
      setCampaigns(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load campaigns',
        variant: 'destructive',
      });
    }
  }, [toast]);

  const loadTemplates = useCallback(async () => {
    try {
      const response = await axios.get('/api/core/email-templates/');
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates', error);
    }
  }, []);

  React.useEffect(() => {
    loadCampaigns();
    loadTemplates();
  }, [loadCampaigns, loadTemplates]);

  const sendCampaign = async (campaignId: string) => {
    try {
      await axios.post(`/api/core/email-campaigns/${campaignId}/send/`);
      toast({
        title: 'Success',
        description: 'Campaign started successfully',
      });
      loadCampaigns();
    } catch (_error) {
      toast({
        title: 'Error',
        description: 'Failed to start campaign',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Mail className="h-8 w-8" />
            Email Campaign Manager
          </h1>
          <p className="text-muted-foreground mt-1">Create and manage email campaigns</p>
        </div>
        <CreateCampaignDialog templates={templates} onCreated={loadCampaigns} />
      </div>

      <Tabs defaultValue="campaigns" className="space-y-4">
        <TabsList>
          <TabsTrigger value="campaigns">
            <Send className="h-4 w-4 mr-2" />
            Campaigns
          </TabsTrigger>
          <TabsTrigger value="templates">
            <FileText className="h-4 w-4 mr-2" />
            Templates
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="campaigns" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {campaigns.map(campaign => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                onSend={() => sendCampaign(campaign.id)}
              />
            ))}
          </div>
          {campaigns.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No campaigns yet. Create your first campaign to get started.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map(template => (
              <TemplateCard key={template.id} template={template} />
            ))}
          </div>
          <CreateTemplateDialog onCreated={loadTemplates} />
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <CampaignAnalytics campaigns={campaigns} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Campaign Card Component
function CampaignCard({ campaign, onSend }: { campaign: EmailCampaign; onSend: () => void }) {
  const openRate = campaign.sent_count > 0 
    ? ((campaign.open_count / campaign.sent_count) * 100).toFixed(1)
    : '0';
  const clickRate = campaign.sent_count > 0
    ? ((campaign.click_count / campaign.sent_count) * 100).toFixed(1)
    : '0';

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{campaign.name}</CardTitle>
          <Badge variant={
            campaign.status === 'completed' ? 'default' :
            campaign.status === 'running' ? 'default' :
            campaign.status === 'paused' ? 'secondary' :
            'outline'
          }>
            {campaign.status}
          </Badge>
        </div>
        <CardDescription>{campaign.subject}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Recipients</p>
            <p className="text-2xl font-bold">{campaign.recipient_count}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Sent</p>
            <p className="text-2xl font-bold">{campaign.sent_count}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Open Rate</p>
            <p className="text-xl font-semibold">{openRate}%</p>
          </div>
          <div>
            <p className="text-muted-foreground">Click Rate</p>
            <p className="text-xl font-semibold">{clickRate}%</p>
          </div>
        </div>

        {campaign.status === 'draft' && (
          <Button className="w-full" onClick={onSend}>
            <Play className="h-4 w-4 mr-2" />
            Start Campaign
          </Button>
        )}
        {campaign.status === 'running' && (
          <Button className="w-full" variant="outline">
            <Pause className="h-4 w-4 mr-2" />
            Pause Campaign
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

// Template Card Component
function TemplateCard({ template }: { template: EmailTemplate }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{template.name}</CardTitle>
        <CardDescription>{template.subject}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Button variant="outline" className="w-full">Edit Template</Button>
          <Button variant="outline" className="w-full">Preview</Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Create Campaign Dialog
function CreateCampaignDialog({ templates, onCreated }: { templates: EmailTemplate[]; onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [subject, setSubject] = useState('');
  const [templateId, setTemplateId] = useState('');
  const [recipientType, setRecipientType] = useState('all_contacts');
  const { toast } = useToast();

  const handleCreate = async () => {
    try {
      await axios.post('/api/core/email-campaigns/', {
        name,
        subject,
        template_id: templateId,
        recipient_type: recipientType,
        status: 'draft',
      });
      toast({
        title: 'Success',
        description: 'Campaign created successfully',
      });
      setOpen(false);
      setName('');
      setSubject('');
      onCreated();
    } catch (_error) {
      toast({
        title: 'Error',
        description: 'Failed to create campaign',
        variant: 'destructive',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Campaign
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Email Campaign</DialogTitle>
          <DialogDescription>Set up a new email campaign</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="campaign-name">Campaign Name</Label>
            <Input
              id="campaign-name"
              placeholder="e.g., Q1 Newsletter"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="subject">Email Subject</Label>
            <Input
              id="subject"
              placeholder="Enter email subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="template">Email Template</Label>
            <Select value={templateId} onValueChange={setTemplateId}>
              <SelectTrigger>
                <SelectValue placeholder="Select template" />
              </SelectTrigger>
              <SelectContent>
                {templates.map(template => (
                  <SelectItem key={template.id} value={template.id}>
                    {template.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="recipients">Recipients</Label>
            <Select value={recipientType} onValueChange={setRecipientType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all_contacts">All Contacts</SelectItem>
                <SelectItem value="all_leads">All Leads</SelectItem>
                <SelectItem value="custom">Custom List</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create Campaign</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Create Template Dialog
function CreateTemplateDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [subject, setSubject] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const { toast } = useToast();

  const handleCreate = async () => {
    try {
      await axios.post('/api/core/email-templates/', {
        name,
        subject,
        html_content: htmlContent,
        plain_content: htmlContent.replace(/<[^>]*>/g, ''),
      });
      toast({
        title: 'Success',
        description: 'Template created successfully',
      });
      setOpen(false);
      setName('');
      setSubject('');
      setHtmlContent('');
      onCreated();
    } catch (_error) {
      toast({
        title: 'Error',
        description: 'Failed to create template',
        variant: 'destructive',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Template
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Create Email Template</DialogTitle>
          <DialogDescription>Create a reusable email template</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="template-name">Template Name</Label>
            <Input
              id="template-name"
              placeholder="e.g., Welcome Email"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="template-subject">Subject</Label>
            <Input
              id="template-subject"
              placeholder="Email subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="html-content">HTML Content</Label>
            <Textarea
              id="html-content"
              placeholder="Enter HTML content..."
              value={htmlContent}
              onChange={(e) => setHtmlContent(e.target.value)}
              rows={10}
              className="font-mono text-sm"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create Template</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Campaign Analytics Component
function CampaignAnalytics({ campaigns }: { campaigns: EmailCampaign[] }) {
  const totalSent = campaigns.reduce((sum, c) => sum + c.sent_count, 0);
  const totalOpens = campaigns.reduce((sum, c) => sum + c.open_count, 0);
  const totalClicks = campaigns.reduce((sum, c) => sum + c.click_count, 0);

  const avgOpenRate = totalSent > 0 ? ((totalOpens / totalSent) * 100).toFixed(1) : '0';
  const avgClickRate = totalSent > 0 ? ((totalClicks / totalSent) * 100).toFixed(1) : '0';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{campaigns.length}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Total Emails Sent</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{totalSent.toLocaleString()}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Avg. Open Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{avgOpenRate}%</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Avg. Click Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{avgClickRate}%</p>
        </CardContent>
      </Card>
    </div>
  );
}
