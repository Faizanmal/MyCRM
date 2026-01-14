'use client';

import React, { useState } from 'react';
import {
  Globe,
  Languages,
  Clock,
  DollarSign,
  Calendar,
  Check,
  Sparkles,
  Upload,
  Download,
  Search,
  RefreshCw
} from 'lucide-react';

import { useI18n } from '@/lib/i18n/I18nProvider';
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
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

// Language Settings Component
const LanguageSettings: React.FC = () => {
  const { locale, languages, setLanguage, t } = useI18n();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredLanguages = languages.filter(
    (lang) =>
      lang.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lang.nativeName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Languages className="h-5 w-5" />
            {t('settings.language')}
          </CardTitle>
          <CardDescription>
            Select your preferred language for the interface
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search languages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            {filteredLanguages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={`p-4 rounded-lg border text-left transition-all ${
                  locale.language === lang.code
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium">{lang.name}</p>
                    <p className="text-sm text-muted-foreground">{lang.nativeName}</p>
                  </div>
                  {locale.language === lang.code && (
                    <Check className="h-5 w-5 text-primary" />
                  )}
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <Progress value={lang.coverage} className="h-1.5 flex-1" />
                  <span className="text-xs text-muted-foreground">{lang.coverage}%</span>
                </div>
                <div className="mt-2 flex gap-2">
                  {lang.isRtl && (
                    <Badge variant="outline" className="text-xs">
                      RTL
                    </Badge>
                  )}
                  {lang.coverage < 80 && (
                    <Badge variant="secondary" className="text-xs">
                      Partial
                    </Badge>
                  )}
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Translation Coverage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { namespace: 'Dashboard', coverage: 100 },
              { namespace: 'Contacts', coverage: 95 },
              { namespace: 'Deals', coverage: 92 },
              { namespace: 'Reports', coverage: 88 },
              { namespace: 'Settings', coverage: 100 },
            ].map((ns) => (
              <div key={ns.namespace} className="flex items-center gap-4">
                <span className="w-24 text-sm">{ns.namespace}</span>
                <Progress value={ns.coverage} className="flex-1" />
                <span className="w-12 text-sm text-right">{ns.coverage}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Timezone Settings Component
const TimezoneSettings: React.FC = () => {
  const { locale, timezones, setTimezone } = useI18n();
  const [autoDetect, setAutoDetect] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTimezones = timezones.filter(
    (tz) =>
      tz.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tz.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group by offset
  const groupedTimezones = filteredTimezones.reduce((acc, tz) => {
    const key = tz.offset;
    if (!acc[key]) acc[key] = [];
    acc[key].push(tz);
    return acc;
  }, {} as Record<string, typeof timezones>);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Timezone Settings
          </CardTitle>
          <CardDescription>
            Configure your timezone for accurate date and time display
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">Auto-detect timezone</p>
                <p className="text-sm text-muted-foreground">
                  Automatically set timezone based on your browser
                </p>
              </div>
            </div>
            <Switch
              checked={autoDetect}
              onCheckedChange={setAutoDetect}
            />
          </div>

          {!autoDetect && (
            <>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search timezones..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              <div className="max-h-64 overflow-y-auto space-y-4">
                {Object.entries(groupedTimezones)
                  .sort(([a], [b]) => a.localeCompare(b))
                  .map(([offset, tzList]) => (
                    <div key={offset}>
                      <p className="text-xs font-medium text-muted-foreground mb-2">
                        UTC {offset}
                      </p>
                      <div className="space-y-1">
                        {tzList.map((tz) => (
                          <button
                            key={tz.name}
                            onClick={() => setTimezone(tz.name)}
                            className={`w-full p-3 rounded-lg text-left transition-all flex items-center justify-between ${
                              locale.timezone === tz.name
                                ? 'bg-primary/10 border border-primary'
                                : 'hover:bg-muted'
                            }`}
                          >
                            <span>{tz.displayName}</span>
                            {locale.timezone === tz.name && (
                              <Check className="h-4 w-4 text-primary" />
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
              </div>
            </>
          )}

          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground mb-1">Current Timezone</p>
            <p className="font-medium">
              {timezones.find((tz) => tz.name === locale.timezone)?.displayName ||
                locale.timezone}
            </p>
            <p className="text-sm text-muted-foreground">
              UTC {locale.timezoneOffset}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Currency Settings Component
const CurrencySettings: React.FC = () => {
  const { locale, currencies, setCurrency, formatCurrency } = useI18n();
  const [showConversion, setShowConversion] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCurrencies = currencies.filter(
    (curr) =>
      curr.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      curr.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Currency Settings
          </CardTitle>
          <CardDescription>
            Set your preferred currency for monetary values
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search currencies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            {filteredCurrencies.map((curr) => (
              <button
                key={curr.code}
                onClick={() => setCurrency(curr.code)}
                className={`p-4 rounded-lg border text-left transition-all ${
                  locale.currency === curr.code
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center font-bold">
                      {curr.symbol}
                    </div>
                    <div>
                      <p className="font-medium">{curr.code}</p>
                      <p className="text-sm text-muted-foreground">{curr.name}</p>
                    </div>
                  </div>
                  {locale.currency === curr.code && (
                    <Check className="h-5 w-5 text-primary" />
                  )}
                </div>
              </button>
            ))}
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
            <div>
              <p className="font-medium">Show currency conversion</p>
              <p className="text-sm text-muted-foreground">
                Display converted values in your currency
              </p>
            </div>
            <Switch
              checked={showConversion}
              onCheckedChange={setShowConversion}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Currency Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1000, 12500.5, 1000000, 0.99].map((amount) => (
              <div key={amount} className="flex justify-between items-center">
                <span className="text-muted-foreground">{amount.toLocaleString()}</span>
                <span className="font-medium">{formatCurrency(amount)}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Date & Time Format Settings
const DateTimeSettings: React.FC = () => {
  const { locale, formatDate, formatTime, formatDateTime } = useI18n();
  const now = new Date();

  const dateFormats = [
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY', example: '12/31/2024' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY', example: '31/12/2024' },
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD', example: '2024-12-31' },
    { value: 'DD.MM.YYYY', label: 'DD.MM.YYYY', example: '31.12.2024' },
  ];

  const timeFormats = [
    { value: '12h', label: '12-hour', example: '2:30 PM' },
    { value: '24h', label: '24-hour', example: '14:30' },
  ];

  const firstDayOptions = [
    { value: 0, label: 'Sunday' },
    { value: 1, label: 'Monday' },
    { value: 6, label: 'Saturday' },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Date & Time Format
          </CardTitle>
          <CardDescription>
            Customize how dates and times are displayed
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label>Date Format</Label>
            <RadioGroup defaultValue={locale.dateFormat}>
              {dateFormats.map((fmt) => (
                <div
                  key={fmt.value}
                  className="flex items-center justify-between p-3 rounded-lg border"
                >
                  <div className="flex items-center gap-3">
                    <RadioGroupItem value={fmt.value} id={fmt.value} />
                    <Label htmlFor={fmt.value} className="cursor-pointer">
                      {fmt.label}
                    </Label>
                  </div>
                  <span className="text-muted-foreground">{fmt.example}</span>
                </div>
              ))}
            </RadioGroup>
          </div>

          <div className="space-y-3">
            <Label>Time Format</Label>
            <RadioGroup defaultValue="12h">
              {timeFormats.map((fmt) => (
                <div
                  key={fmt.value}
                  className="flex items-center justify-between p-3 rounded-lg border"
                >
                  <div className="flex items-center gap-3">
                    <RadioGroupItem value={fmt.value} id={fmt.value} />
                    <Label htmlFor={fmt.value} className="cursor-pointer">
                      {fmt.label}
                    </Label>
                  </div>
                  <span className="text-muted-foreground">{fmt.example}</span>
                </div>
              ))}
            </RadioGroup>
          </div>

          <div className="space-y-3">
            <Label>First Day of Week</Label>
            <Select defaultValue={locale.firstDayOfWeek.toString()}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {firstDayOptions.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value.toString()}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Date</span>
              <span className="font-medium">{formatDate(now)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Time</span>
              <span className="font-medium">{formatTime(now)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Date & Time</span>
              <span className="font-medium">{formatDateTime(now)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main Component
export default function LocaleSettings() {
  const { locale, isLoading } = useI18n();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Globe className="h-8 w-8" />
            Locale & Regional Settings
          </h1>
          <p className="text-muted-foreground mt-1">
            Configure language, timezone, currency, and date formats
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
        </div>
      </div>

      {/* Current Settings Summary */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Languages className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Language</p>
                <p className="font-medium">{locale.languageName || locale.language}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Timezone</p>
                <p className="font-medium">UTC {locale.timezoneOffset}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <DollarSign className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Currency</p>
                <p className="font-medium">
                  {locale.currency} ({locale.currencySymbol})
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Date Format</p>
                <p className="font-medium">{locale.dateFormat}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="language">
        <TabsList>
          <TabsTrigger value="language" className="flex items-center gap-2">
            <Languages className="h-4 w-4" />
            Language
          </TabsTrigger>
          <TabsTrigger value="timezone" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Timezone
          </TabsTrigger>
          <TabsTrigger value="currency" className="flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Currency
          </TabsTrigger>
          <TabsTrigger value="datetime" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Date & Time
          </TabsTrigger>
        </TabsList>

        <TabsContent value="language" className="mt-4">
          <LanguageSettings />
        </TabsContent>

        <TabsContent value="timezone" className="mt-4">
          <TimezoneSettings />
        </TabsContent>

        <TabsContent value="currency" className="mt-4">
          <CurrencySettings />
        </TabsContent>

        <TabsContent value="datetime" className="mt-4">
          <DateTimeSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}

