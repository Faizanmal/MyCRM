'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Mail, Send, Save, Loader2 } from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';

export default function EmailSettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [emailSettings, setEmailSettings] = useState({
    emailAddress: 'your@email.com',
    displayName: 'Your Name',
    signatureEnabled: true,
    signature: 'Best regards,\nYour Name',
    autoResponderEnabled: false,
    autoResponderMessage: 'I am currently out of the office.',
    trackEmailOpens: true,
    trackEmailClicks: true,
    enableEmailReminders: true,
    reminderTime: '9:00',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEmailSettings(prev => ({ ...prev, [name]: value }));
  };

  const handleToggle = (key: keyof typeof emailSettings) => {
    setEmailSettings(prev => ({
      ...prev,
      [key]: typeof prev[key] === 'boolean' ? !prev[key] : prev[key]
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const response = await fetch('/api/v1/email/settings/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailSettings),
      });

      if (!response.ok) throw new Error('Failed to update email settings');
      
      toast.success('Email settings updated successfully');
    } catch (error) {
      console.warn("Failed to update email settings",error);
      toast.error('Failed to update email settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Email Settings</h1>
            <p className="text-gray-500 mt-1">Configure your email preferences and settings</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Account */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5" />
                  Email Account
                </CardTitle>
                <CardDescription>Your email account information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="emailAddress">Email Address</Label>
                  <Input
                    id="emailAddress"
                    name="emailAddress"
                    type="email"
                    value={emailSettings.emailAddress}
                    onChange={handleInputChange}
                    disabled
                    className="bg-gray-50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="displayName">Display Name</Label>
                  <Input
                    id="displayName"
                    name="displayName"
                    value={emailSettings.displayName}
                    onChange={handleInputChange}
                    placeholder="Your Name"
                  />
                </div>

                <Button type="button" variant="outline">
                  <Send className="w-4 h-4 mr-2" />
                  Send Test Email
                </Button>
              </CardContent>
            </Card>

            {/* Email Signature */}
            <Card>
              <CardHeader>
                <CardTitle>Email Signature</CardTitle>
                <CardDescription>Add a signature to your outgoing emails</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Enable Signature</Label>
                  <Switch
                    checked={emailSettings.signatureEnabled}
                    onCheckedChange={() => handleToggle('signatureEnabled')}
                  />
                </div>

                {emailSettings.signatureEnabled && (
                  <div className="space-y-2">
                    <Label htmlFor="signature">Signature</Label>
                    <textarea
                      id="signature"
                      name="signature"
                      value={emailSettings.signature}
                      onChange={handleInputChange}
                      className="w-full p-3 border rounded-lg min-h-24 font-mono text-sm dark:bg-gray-900"
                      placeholder="Your email signature"
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Auto Responder */}
            <Card>
              <CardHeader>
                <CardTitle>Auto Responder</CardTitle>
                <CardDescription>Set up automatic responses for incoming emails</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Enable Auto Responder</Label>
                  <Switch
                    checked={emailSettings.autoResponderEnabled}
                    onCheckedChange={() => handleToggle('autoResponderEnabled')}
                  />
                </div>

                {emailSettings.autoResponderEnabled && (
                  <div className="space-y-2">
                    <Label htmlFor="autoResponderMessage">Auto Responder Message</Label>
                    <textarea
                      id="autoResponderMessage"
                      name="autoResponderMessage"
                      value={emailSettings.autoResponderMessage}
                      onChange={handleInputChange}
                      className="w-full p-3 border rounded-lg min-h-24 dark:bg-gray-900"
                      placeholder="Message to automatically send..."
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Email Tracking */}
            <Card>
              <CardHeader>
                <CardTitle>Email Tracking</CardTitle>
                <CardDescription>Track email opens and clicks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <Label>Track Email Opens</Label>
                  <Switch
                    checked={emailSettings.trackEmailOpens}
                    onCheckedChange={() => handleToggle('trackEmailOpens')}
                  />
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <Label>Track Email Clicks</Label>
                  <Switch
                    checked={emailSettings.trackEmailClicks}
                    onCheckedChange={() => handleToggle('trackEmailClicks')}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Email Reminders */}
            <Card>
              <CardHeader>
                <CardTitle>Email Reminders</CardTitle>
                <CardDescription>Get reminders about unanswered emails</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Enable Email Reminders</Label>
                  <Switch
                    checked={emailSettings.enableEmailReminders}
                    onCheckedChange={() => handleToggle('enableEmailReminders')}
                  />
                </div>

                {emailSettings.enableEmailReminders && (
                  <div className="space-y-2">
                    <Label htmlFor="reminderTime">Reminder Time</Label>
                    <Input
                      id="reminderTime"
                      name="reminderTime"
                      type="time"
                      value={emailSettings.reminderTime}
                      onChange={handleInputChange}
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end gap-3">
              <Button type="button" variant="outline">Cancel</Button>
              <Button type="submit" disabled={isSaving} className="gap-2">
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

