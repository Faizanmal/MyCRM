'use client';

import React from 'react';
import {
  Accessibility,
  Eye,
  EyeOff,
  Keyboard,
  Mic,
  MicOff,
  Monitor,
  Type,
  Brain,
  Contrast,
  Palette,
  ZoomIn,
  Focus,
  PlayCircle,
  Timer,
  BookOpen,
  CheckCircle,
  Info,
} from 'lucide-react';

import { useAccessibility } from '@/lib/accessibility/AccessibilityProvider';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

// Visual Settings Tab
const VisualSettingsTab: React.FC = () => {
  const { settings, updateSettings } = useAccessibility();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Contrast className="h-5 w-5" />
            Display Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-black flex items-center justify-center">
                <span className="text-white font-bold">A</span>
              </div>
              <div>
                <Label>High Contrast Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Increase contrast for better visibility
                </p>
              </div>
            </div>
            <Switch
              checked={settings.highContrastMode}
              onCheckedChange={(checked) => updateSettings({ highContrastMode: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                <EyeOff className="h-5 w-5" />
              </div>
              <div>
                <Label>Reduce Transparency</Label>
                <p className="text-sm text-muted-foreground">
                  Minimize transparent elements
                </p>
              </div>
            </div>
            <Switch
              checked={settings.reduceTransparency}
              onCheckedChange={(checked) => updateSettings({ reduceTransparency: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                <PlayCircle className="h-5 w-5" />
              </div>
              <div>
                <Label>Reduce Motion</Label>
                <p className="text-sm text-muted-foreground">
                  Minimize animations and transitions
                </p>
              </div>
            </div>
            <Switch
              checked={settings.reduceMotion}
              onCheckedChange={(checked) => updateSettings({ reduceMotion: checked })}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Color Vision
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Color Blind Mode</Label>
            <Select
              value={settings.colorBlindMode}
              onValueChange={(value) =>
                updateSettings({ colorBlindMode: value as typeof settings.colorBlindMode })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                <SelectItem value="protanopia">Protanopia (Red-blind)</SelectItem>
                <SelectItem value="deuteranopia">Deuteranopia (Green-blind)</SelectItem>
                <SelectItem value="tritanopia">Tritanopia (Blue-blind)</SelectItem>
                <SelectItem value="achromatopsia">Achromatopsia (Monochrome)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {settings.colorBlindMode !== 'none' && (
            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 text-sm">
                <Info className="h-4 w-4" />
                <span>Color filters are applied to improve visibility</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ZoomIn className="h-5 w-5" />
            Text Size
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex justify-between">
              <Label>Font Size</Label>
              <span className="text-sm font-medium">
                {Math.round(settings.fontSizeMultiplier * 100)}%
              </span>
            </div>
            <Slider
              value={[settings.fontSizeMultiplier]}
              onValueChange={([value]) => updateSettings({ fontSizeMultiplier: value })}
              min={0.75}
              max={2}
              step={0.05}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>75%</span>
              <span>100%</span>
              <span>200%</span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4">
            <div className="flex items-center gap-3">
              <Type className="h-5 w-5" />
              <div>
                <Label>Dyslexia-Friendly Font</Label>
                <p className="text-sm text-muted-foreground">
                  Use OpenDyslexic font
                </p>
              </div>
            </div>
            <Switch
              checked={settings.dyslexiaFont}
              onCheckedChange={(checked) => updateSettings({ dyslexiaFont: checked })}
            />
          </div>

          {/* Preview */}
          <div className="mt-4 p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground mb-2">Preview:</p>
            <p
              style={{
                fontSize: `${settings.fontSizeMultiplier}rem`,
                fontFamily: settings.dyslexiaFont ? 'OpenDyslexic, sans-serif' : 'inherit',
              }}
            >
              The quick brown fox jumps over the lazy dog.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Navigation Settings Tab
const NavigationSettingsTab: React.FC = () => {
  const { settings, updateSettings } = useAccessibility();

  const keyboardShortcuts = [
    { keys: 'Ctrl + /', action: 'Open command palette' },
    { keys: 'Ctrl + K', action: 'Quick search' },
    { keys: 'Ctrl + N', action: 'New contact' },
    { keys: 'Ctrl + S', action: 'Save current item' },
    { keys: 'Escape', action: 'Close modal/cancel' },
    { keys: 'Tab', action: 'Navigate forward' },
    { keys: 'Shift + Tab', action: 'Navigate backward' },
    { keys: 'Enter', action: 'Activate focused element' },
    { keys: 'Arrow Keys', action: 'Navigate within components' },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Keyboard className="h-5 w-5" />
            Keyboard Navigation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label>Keyboard Shortcuts</Label>
              <p className="text-sm text-muted-foreground">
                Enable keyboard shortcuts for quick actions
              </p>
            </div>
            <Switch
              checked={settings.keyboardShortcutsEnabled}
              onCheckedChange={(checked) =>
                updateSettings({ keyboardShortcutsEnabled: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Skip Links</Label>
              <p className="text-sm text-muted-foreground">
                Show skip navigation links
              </p>
            </div>
            <Switch
              checked={settings.skipLinksEnabled}
              onCheckedChange={(checked) => updateSettings({ skipLinksEnabled: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Focus className="h-5 w-5" />
              <div>
                <Label>Enhanced Focus Indicators</Label>
                <p className="text-sm text-muted-foreground">
                  Make focus outlines more visible
                </p>
              </div>
            </div>
            <Switch
              checked={settings.enhancedFocusIndicators}
              onCheckedChange={(checked) =>
                updateSettings({ enhancedFocusIndicators: checked })
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Keyboard Shortcuts Reference</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {keyboardShortcuts.map((shortcut) => (
              <div
                key={shortcut.keys}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <span className="text-sm text-muted-foreground">{shortcut.action}</span>
                <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">
                  {shortcut.keys}
                </kbd>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Screen Reader Settings Tab
const ScreenReaderSettingsTab: React.FC = () => {
  const { settings, updateSettings, announce } = useAccessibility();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Monitor className="h-5 w-5" />
            Screen Reader Settings
          </CardTitle>
          <CardDescription>
            Optimize the interface for screen reader users
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label>Screen Reader Mode</Label>
              <p className="text-sm text-muted-foreground">
                Enable additional screen reader optimizations
              </p>
            </div>
            <Switch
              checked={settings.screenReaderMode}
              onCheckedChange={(checked) => updateSettings({ screenReaderMode: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Announce Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Read out notifications automatically
              </p>
            </div>
            <Switch
              checked={settings.announceNotifications}
              onCheckedChange={(checked) =>
                updateSettings({ announceNotifications: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Announce Page Changes</Label>
              <p className="text-sm text-muted-foreground">
                Announce when navigating to new pages
              </p>
            </div>
            <Switch
              checked={settings.announcePageChanges}
              onCheckedChange={(checked) =>
                updateSettings({ announcePageChanges: checked })
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Test Announcements</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Test screen reader announcements to ensure they work correctly
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => announce('This is a polite announcement', 'polite')}
            >
              Test Polite
            </Button>
            <Button
              variant="outline"
              onClick={() => announce('This is an important announcement!', 'assertive')}
            >
              Test Assertive
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Screen Reader Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>Use heading navigation (H key) to jump between sections</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>Use landmarks (D key) to navigate between regions</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>Press Tab to move between interactive elements</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>Use form mode (F key) to navigate form controls</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

// Voice Control Settings Tab
const VoiceControlSettingsTab: React.FC = () => {
  const {
    settings,
    updateSettings,
    isVoiceListening,
    startVoiceListening,
    stopVoiceListening,
  } = useAccessibility();

  const voiceCommands = [
    { phrase: 'Go to dashboard', action: 'Navigate to dashboard' },
    { phrase: 'Go to contacts', action: 'Navigate to contacts' },
    { phrase: 'New contact', action: 'Create new contact' },
    { phrase: 'Search', action: 'Open search' },
    { phrase: 'Save', action: 'Save current item' },
    { phrase: 'Close', action: 'Close current modal' },
    { phrase: 'Scroll down', action: 'Scroll page down' },
    { phrase: 'Scroll up', action: 'Scroll page up' },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="h-5 w-5" />
            Voice Control
          </CardTitle>
          <CardDescription>
            Control the application using voice commands
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label>Enable Voice Commands</Label>
              <p className="text-sm text-muted-foreground">
                Use voice to navigate and perform actions
              </p>
            </div>
            <Switch
              checked={settings.voiceCommandsEnabled}
              onCheckedChange={(checked) =>
                updateSettings({ voiceCommandsEnabled: checked })
              }
            />
          </div>

          {settings.voiceCommandsEnabled && (
            <>
              <div className="space-y-2">
                <Label>Voice Language</Label>
                <Select
                  value={settings.voiceLanguage}
                  onValueChange={(value) => updateSettings({ voiceLanguage: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en-US">English (US)</SelectItem>
                    <SelectItem value="en-GB">English (UK)</SelectItem>
                    <SelectItem value="es-ES">Spanish</SelectItem>
                    <SelectItem value="fr-FR">French</SelectItem>
                    <SelectItem value="de-DE">German</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={isVoiceListening ? stopVoiceListening : startVoiceListening}
                  variant={isVoiceListening ? 'destructive' : 'default'}
                  className="flex-1"
                >
                  {isVoiceListening ? (
                    <>
                      <MicOff className="h-4 w-4 mr-2" />
                      Stop Listening
                    </>
                  ) : (
                    <>
                      <Mic className="h-4 w-4 mr-2" />
                      Start Listening
                    </>
                  )}
                </Button>
              </div>

              {isVoiceListening && (
                <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-green-700">
                      Listening for commands...
                    </span>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Available Voice Commands</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {voiceCommands.map((cmd) => (
              <div
                key={cmd.phrase}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <span className="text-sm font-medium">&quot;{cmd.phrase}&quot;</span>
                <span className="text-sm text-muted-foreground">{cmd.action}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Cognitive Settings Tab
const CognitiveSettingsTab: React.FC = () => {
  const { settings, updateSettings } = useAccessibility();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Cognitive Accessibility
          </CardTitle>
          <CardDescription>
            Settings to help with focus and comprehension
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label>Simplified Interface</Label>
              <p className="text-sm text-muted-foreground">
                Reduce visual complexity and distractions
              </p>
            </div>
            <Switch
              checked={settings.simplifiedInterface}
              onCheckedChange={(checked) =>
                updateSettings({ simplifiedInterface: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Timer className="h-5 w-5" />
              <div>
                <Label>Extended Timeouts</Label>
                <p className="text-sm text-muted-foreground">
                  Allow more time for timed actions
                </p>
              </div>
            </div>
            <Switch
              checked={settings.extendedTimeouts}
              onCheckedChange={(checked) => updateSettings({ extendedTimeouts: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="h-5 w-5" />
              <div>
                <Label>Reading Mask</Label>
                <p className="text-sm text-muted-foreground">
                  Highlight current reading line
                </p>
              </div>
            </div>
            <Switch
              checked={settings.readingMask}
              onCheckedChange={(checked) => updateSettings({ readingMask: checked })}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reading & Focus Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3 text-sm">
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>
                Use the reading mask to focus on one line at a time
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>
                Enable simplified interface to reduce distractions
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>
                Increase font size for easier reading
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>
                Use keyboard shortcuts to navigate without distractions
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

// Main Component
export default function AccessibilitySettings() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Accessibility className="h-8 w-8" />
            Accessibility Settings
          </h1>
          <p className="text-muted-foreground mt-1">
            Customize the interface to meet your accessibility needs
          </p>
        </div>
        <Badge variant="outline" className="gap-1">
          <CheckCircle className="h-3 w-3" />
          WCAG 2.1 AA Compliant
        </Badge>
      </div>

      <Tabs defaultValue="visual">
        <TabsList>
          <TabsTrigger value="visual" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Visual
          </TabsTrigger>
          <TabsTrigger value="navigation" className="flex items-center gap-2">
            <Keyboard className="h-4 w-4" />
            Navigation
          </TabsTrigger>
          <TabsTrigger value="screen-reader" className="flex items-center gap-2">
            <Monitor className="h-4 w-4" />
            Screen Reader
          </TabsTrigger>
          <TabsTrigger value="voice" className="flex items-center gap-2">
            <Mic className="h-4 w-4" />
            Voice Control
          </TabsTrigger>
          <TabsTrigger value="cognitive" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Cognitive
          </TabsTrigger>
        </TabsList>

        <TabsContent value="visual" className="mt-4">
          <VisualSettingsTab />
        </TabsContent>

        <TabsContent value="navigation" className="mt-4">
          <NavigationSettingsTab />
        </TabsContent>

        <TabsContent value="screen-reader" className="mt-4">
          <ScreenReaderSettingsTab />
        </TabsContent>

        <TabsContent value="voice" className="mt-4">
          <VoiceControlSettingsTab />
        </TabsContent>

        <TabsContent value="cognitive" className="mt-4">
          <CognitiveSettingsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

