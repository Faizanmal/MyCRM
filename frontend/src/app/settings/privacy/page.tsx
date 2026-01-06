'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Eye, Download, Trash2, Save, Loader2 } from 'lucide-react';

export default function PrivacySettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [privacySettings, setPrivacySettings] = useState({
    shareActivityWithTeam: true,
    showOnlineStatus: true,
    allowMentions: true,
    allowComments: true,
    dataExportEnabled: true,
  });

  const handleToggle = (key: keyof typeof privacySettings) => {
    setPrivacySettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch('/api/auth/privacy-settings/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(privacySettings),
      });

      if (!response.ok) throw new Error('Failed to save privacy settings');
      toast.success('Privacy settings updated successfully');
    } catch (error) {
      console.log("Failed to save privacy settings",error);
      toast.error('Failed to save privacy settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDataExport = async () => {
    try {
      const response = await fetch('/api/auth/export-data/', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to export data');
      toast.success('Your data export has been initiated. Check your email soon.');
    } catch (error) {
      console.log("Failed to export data",error);
      toast.error('Failed to export data');
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Are you sure? This action cannot be undone.')) return;

    try {
      const response = await fetch('/api/auth/delete-account/', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to delete account');
      toast.success('Your account has been deleted');
    } catch (error) {
      console.log("Failed to delete account",error);
      toast.error('Failed to delete account');
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Privacy Settings</h1>
            <p className="text-gray-500 mt-1">Control who can see your information and activity</p>
          </div>

          {/* Visibility Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Visibility & Status
              </CardTitle>
              <CardDescription>Control who can see your online status and activity</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <Label className="text-base font-medium text-gray-900 dark:text-white">Show Online Status</Label>
                  <p className="text-sm text-gray-500">Let others see when you&apos;re active</p>
                </div>
                <Switch
                  checked={privacySettings.showOnlineStatus}
                  onCheckedChange={() => handleToggle('showOnlineStatus')}
                />
              </div>

              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <Label className="text-base font-medium text-gray-900 dark:text-white">Share Activity with Team</Label>
                  <p className="text-sm text-gray-500">Allow your team to see your activity</p>
                </div>
                <Switch
                  checked={privacySettings.shareActivityWithTeam}
                  onCheckedChange={() => handleToggle('shareActivityWithTeam')}
                />
              </div>
            </CardContent>
          </Card>

          {/* Interaction Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Interactions</CardTitle>
              <CardDescription>Control who can interact with your content</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <Label className="text-base font-medium text-gray-900 dark:text-white">Allow Mentions</Label>
                  <p className="text-sm text-gray-500">Allow others to mention you in messages</p>
                </div>
                <Switch
                  checked={privacySettings.allowMentions}
                  onCheckedChange={() => handleToggle('allowMentions')}
                />
              </div>

              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <Label className="text-base font-medium text-gray-900 dark:text-white">Allow Comments</Label>
                  <p className="text-sm text-gray-500">Allow others to comment on your posts</p>
                </div>
                <Switch
                  checked={privacySettings.allowComments}
                  onCheckedChange={() => handleToggle('allowComments')}
                />
              </div>
            </CardContent>
          </Card>

          {/* Data Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5" />
                Data Management
              </CardTitle>
              <CardDescription>Control your personal data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <Label className="text-base font-medium text-gray-900 dark:text-white">Data Export</Label>
                  <p className="text-sm text-gray-500">Download a copy of your data</p>
                </div>
                <Switch
                  checked={privacySettings.dataExportEnabled}
                  onCheckedChange={() => handleToggle('dataExportEnabled')}
                />
              </div>

              {privacySettings.dataExportEnabled && (
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={handleDataExport}
                >
                  <Download className="w-4 h-4" />
                  Export My Data
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Dangerous Zone */}
          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <CardTitle className="text-red-600 dark:text-red-400 flex items-center gap-2">
                <Trash2 className="w-5 h-5" />
                Danger Zone
              </CardTitle>
              <CardDescription>Irreversible and destructive actions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 border border-red-200 dark:border-red-900 rounded-lg bg-red-50 dark:bg-red-950">
                <p className="text-sm text-red-800 dark:text-red-200 mb-3">
                  Deleting your account will permanently remove all your data. This action cannot be undone.
                </p>
                <Button
                  variant="destructive"
                  onClick={handleDeleteAccount}
                >
                  Delete My Account
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => window.location.reload()}
            >
              Discard Changes
            </Button>
            <Button
              type="submit"
              disabled={isSaving}
              className="gap-2"
              onClick={handleSave}
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
