'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
// import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Keyboard, Edit2, Save, Loader2 } from 'lucide-react';

interface Shortcut {
  id: string;
  action: string;
  keys: string;
  custom: boolean;
}

export default function ShortcutsSettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [shortcuts, setShortcuts] = useState<Shortcut[]>([
    { id: '1', action: 'Search Contacts', keys: 'Ctrl + K', custom: false },
    { id: '2', action: 'Create New Contact', keys: 'Ctrl + N', custom: false },
    { id: '3', action: 'Create New Deal', keys: 'Ctrl + Shift + D', custom: false },
    { id: '4', action: 'Create New Task', keys: 'Ctrl + Shift + T', custom: false },
    { id: '5', action: 'Open Help', keys: 'Ctrl + ?', custom: false },
    { id: '6', action: 'Quick Save', keys: 'Ctrl + S', custom: false },
  ]);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingKeys, setEditingKeys] = useState('');

  const handleEditShortcut = (shortcut: Shortcut) => {
    setEditingId(shortcut.id);
    setEditingKeys(shortcut.keys);
  };

  const handleSaveShortcut = async (shortcut: Shortcut) => {
    setIsSaving(true);
    try {
      const response = await fetch(`/api/v1/shortcuts/${shortcut.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keys: editingKeys }),
      });

      if (!response.ok) throw new Error('Failed to update shortcut');

      setShortcuts(prev =>
        prev.map(s => s.id === shortcut.id ? { ...s, keys: editingKeys } : s)
      );

      toast.success('Shortcut updated');
      setEditingId(null);
    } catch (error) {
      console.log("Failed to update shortcut",error);
      toast.error('Failed to update shortcut');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetShortcuts = async () => {
    if (!window.confirm('Reset all shortcuts to defaults?')) return;

    try {
      const response = await fetch('/api/v1/shortcuts/reset/', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to reset shortcuts');

      setShortcuts(prev =>
        prev.map(s => ({ ...s, keys: s.id === '1' ? 'Ctrl + K' : s.keys, custom: false }))
      );

      toast.success('Shortcuts reset to defaults');
    } catch (error) {
      console.log("Failed to reset shortcuts",error);
      toast.error('Failed to reset shortcuts');
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Keyboard Shortcuts</h1>
              <p className="text-gray-500 mt-1">Customize keyboard shortcuts for faster navigation</p>
            </div>
            <Button
              onClick={handleResetShortcuts}
              variant="outline"
              className="gap-2"
            >
              Reset to Defaults
            </Button>
          </div>

          {/* Shortcuts List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Keyboard className="w-5 h-5" />
                Available Shortcuts
              </CardTitle>
              <CardDescription>Customize your keyboard shortcuts below</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {shortcuts.map((shortcut) => (
                  <div
                    key={shortcut.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white">{shortcut.action}</p>
                      {shortcut.custom && (
                        <Badge className="mt-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          Custom
                        </Badge>
                      )}
                    </div>

                    {editingId === shortcut.id ? (
                      <div className="flex gap-2">
                        <Input
                          value={editingKeys}
                          onChange={(e) => setEditingKeys(e.target.value)}
                          placeholder="e.g., Ctrl + K"
                          className="w-32"
                        />
                        <Button
                          size="sm"
                          onClick={() => handleSaveShortcut(shortcut)}
                          disabled={isSaving}
                          className="gap-1"
                        >
                          {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                          Save
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditingId(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3">
                        <kbd className="px-3 py-1 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded font-mono text-sm">
                          {shortcut.keys}
                        </kbd>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEditShortcut(shortcut)}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle>Tips for Creating Shortcuts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">Modifier Keys:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Windows/Linux: Ctrl, Shift, Alt</li>
                  <li>Mac: Cmd, Shift, Option</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">Examples:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Ctrl + K (Search)</li>
                  <li>Ctrl + Shift + N (New item)</li>
                  <li>Alt + D (Delete)</li>
                </ul>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900 rounded">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  Avoid conflicts with your browser&apos;s built-in shortcuts
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Platform-Specific */}
          <Card>
            <CardHeader>
              <CardTitle>Platform-Specific Shortcuts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Windows/Linux</h3>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><kbd className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Ctrl + Tab</kbd> - Next window</p>
                  <p><kbd className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Ctrl + Shift + Tab</kbd> - Previous window</p>
                  <p><kbd className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Alt + Tab</kbd> - Switch application</p>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Mac</h3>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p><kbd className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Cmd + Tab</kbd> - Next window</p>
                  <p><kbd className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Cmd + Shift + Tab</kbd> - Previous window</p>
                  <p><kbd className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Cmd + Space</kbd> - Spotlight search</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
