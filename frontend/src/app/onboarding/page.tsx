'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Users, 
  Upload, 
  Settings, 
  CheckCircle2, 
  ArrowRight,
  ArrowLeft,
  Sparkles
} from 'lucide-react';

interface OrganizationData {
  name: string;
  industry: string;
  size: string;
  website: string;
  description: string;
}

interface TeamMember {
  email: string;
  role: string;
}

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Step 1: Organization Setup
  const [orgData, setOrgData] = useState<OrganizationData>({
    name: '',
    industry: '',
    size: '',
    website: '',
    description: ''
  });

  // Step 2: Team Members
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([
    { email: '', role: 'sales_rep' }
  ]);

  // Step 3: Data Import
  const [importChoice, setImportChoice] = useState<'skip' | 'csv' | 'import'>('skip');

  // Step 4: Preferences
  const [preferences, setPreferences] = useState({
    currency: 'USD',
    timezone: 'UTC',
    dateFormat: 'MM/DD/YYYY',
    language: 'en'
  });

  const totalSteps = 5;
  const progress = (currentStep / totalSteps) * 100;

  const addTeamMember = () => {
    setTeamMembers([...teamMembers, { email: '', role: 'sales_rep' }]);
  };

  const removeTeamMember = (index: number) => {
    setTeamMembers(teamMembers.filter((_, i) => i !== index));
  };

  const updateTeamMember = (index: number, field: 'email' | 'role', value: string) => {
    const updated = [...teamMembers];
    updated[index][field] = value;
    setTeamMembers(updated);
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    // Simulate API call to save onboarding data
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mark onboarding as complete in localStorage
    localStorage.setItem('onboarding_complete', 'true');
    
    // Redirect to dashboard
    router.push('/dashboard');
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return orgData.name && orgData.industry && orgData.size;
      case 2:
        return teamMembers.every(tm => tm.email.includes('@'));
      case 3:
        return true; // Import is optional
      case 4:
        return true; // Preferences have defaults
      case 5:
        return true; // Summary
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Welcome to MyCRM</h1>
          </div>
          <p className="text-gray-600">
            Let's get your account set up in just a few steps
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Step {currentStep} of {totalSteps}
            </span>
            <span className="text-sm font-medium text-gray-700">
              {Math.round(progress)}% Complete
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Step Content */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              {currentStep === 1 && <Building2 className="h-6 w-6 text-blue-600" />}
              {currentStep === 2 && <Users className="h-6 w-6 text-blue-600" />}
              {currentStep === 3 && <Upload className="h-6 w-6 text-blue-600" />}
              {currentStep === 4 && <Settings className="h-6 w-6 text-blue-600" />}
              {currentStep === 5 && <CheckCircle2 className="h-6 w-6 text-green-600" />}
              
              <div>
                <CardTitle>
                  {currentStep === 1 && 'Organization Details'}
                  {currentStep === 2 && 'Invite Team Members'}
                  {currentStep === 3 && 'Import Your Data'}
                  {currentStep === 4 && 'Set Preferences'}
                  {currentStep === 5 && 'Ready to Go!'}
                </CardTitle>
                <CardDescription>
                  {currentStep === 1 && 'Tell us about your organization'}
                  {currentStep === 2 && 'Add your team to collaborate'}
                  {currentStep === 3 && 'Import existing contacts and leads'}
                  {currentStep === 4 && 'Customize your experience'}
                  {currentStep === 5 && 'Your account is ready'}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            {/* Step 1: Organization */}
            {currentStep === 1 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="orgName">Organization Name *</Label>
                  <Input
                    id="orgName"
                    placeholder="Acme Corporation"
                    value={orgData.name}
                    onChange={(e) => setOrgData({ ...orgData, name: e.target.value })}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="industry">Industry *</Label>
                    <select
                      id="industry"
                      className="w-full p-2 border rounded-md"
                      value={orgData.industry}
                      onChange={(e) => setOrgData({ ...orgData, industry: e.target.value })}
                    >
                      <option value="">Select...</option>
                      <option value="technology">Technology</option>
                      <option value="finance">Finance</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="retail">Retail</option>
                      <option value="manufacturing">Manufacturing</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="size">Company Size *</Label>
                    <select
                      id="size"
                      className="w-full p-2 border rounded-md"
                      value={orgData.size}
                      onChange={(e) => setOrgData({ ...orgData, size: e.target.value })}
                    >
                      <option value="">Select...</option>
                      <option value="1-10">1-10 employees</option>
                      <option value="11-50">11-50 employees</option>
                      <option value="51-200">51-200 employees</option>
                      <option value="201-500">201-500 employees</option>
                      <option value="500+">500+ employees</option>
                    </select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="website">Website</Label>
                  <Input
                    id="website"
                    type="url"
                    placeholder="https://example.com"
                    value={orgData.website}
                    onChange={(e) => setOrgData({ ...orgData, website: e.target.value })}
                  />
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Tell us about your organization..."
                    rows={3}
                    value={orgData.description}
                    onChange={(e) => setOrgData({ ...orgData, description: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Step 2: Team Members */}
            {currentStep === 2 && (
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Invite your team members to collaborate. They'll receive an email invitation.
                </p>

                {teamMembers.map((member, index) => (
                  <div key={index} className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        type="email"
                        placeholder="teammate@example.com"
                        value={member.email}
                        onChange={(e) => updateTeamMember(index, 'email', e.target.value)}
                      />
                    </div>
                    <div className="w-40">
                      <select
                        className="w-full p-2 border rounded-md"
                        value={member.role}
                        onChange={(e) => updateTeamMember(index, 'role', e.target.value)}
                      >
                        <option value="admin">Admin</option>
                        <option value="sales_rep">Sales Rep</option>
                        <option value="marketing">Marketing</option>
                        <option value="support">Support</option>
                      </select>
                    </div>
                    {teamMembers.length > 1 && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => removeTeamMember(index)}
                      >
                        ×
                      </Button>
                    )}
                  </div>
                ))}

                <Button
                  variant="outline"
                  onClick={addTeamMember}
                  className="w-full"
                >
                  + Add Another Team Member
                </Button>

                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
                  <strong>Tip:</strong> You can always invite more team members later from the settings page.
                </div>
              </div>
            )}

            {/* Step 3: Data Import */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Do you have existing data you'd like to import?
                </p>

                <div className="space-y-3">
                  <div
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      importChoice === 'skip' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setImportChoice('skip')}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">Start Fresh</h3>
                        <p className="text-sm text-gray-600">Begin with an empty CRM</p>
                      </div>
                      {importChoice === 'skip' && (
                        <CheckCircle2 className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>

                  <div
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      importChoice === 'csv' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setImportChoice('csv')}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">Upload CSV File</h3>
                        <p className="text-sm text-gray-600">Import contacts and leads from CSV</p>
                      </div>
                      {importChoice === 'csv' && (
                        <CheckCircle2 className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>

                  <div
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      importChoice === 'import' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setImportChoice('import')}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">Import from Another CRM</h3>
                        <p className="text-sm text-gray-600">Connect to Salesforce, HubSpot, or others</p>
                        <Badge variant="secondary" className="mt-1">Coming Soon</Badge>
                      </div>
                      {importChoice === 'import' && (
                        <CheckCircle2 className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>
                </div>

                {importChoice === 'csv' && (
                  <div className="mt-4 p-4 border-2 border-dashed rounded-lg">
                    <Input type="file" accept=".csv" className="mb-2" />
                    <p className="text-xs text-gray-500">
                      Upload a CSV file with columns: name, email, phone, company
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Step 4: Preferences */}
            {currentStep === 4 && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="currency">Currency</Label>
                    <select
                      id="currency"
                      className="w-full p-2 border rounded-md"
                      value={preferences.currency}
                      onChange={(e) => setPreferences({ ...preferences, currency: e.target.value })}
                    >
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="GBP">GBP (£)</option>
                      <option value="JPY">JPY (¥)</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="timezone">Timezone</Label>
                    <select
                      id="timezone"
                      className="w-full p-2 border rounded-md"
                      value={preferences.timezone}
                      onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time (ET)</option>
                      <option value="America/Chicago">Central Time (CT)</option>
                      <option value="America/Denver">Mountain Time (MT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PT)</option>
                      <option value="Europe/London">London (GMT)</option>
                      <option value="Asia/Tokyo">Tokyo (JST)</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="dateFormat">Date Format</Label>
                    <select
                      id="dateFormat"
                      className="w-full p-2 border rounded-md"
                      value={preferences.dateFormat}
                      onChange={(e) => setPreferences({ ...preferences, dateFormat: e.target.value })}
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="language">Language</Label>
                    <select
                      id="language"
                      className="w-full p-2 border rounded-md"
                      value={preferences.language}
                      onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                      <option value="ja">Japanese</option>
                    </select>
                  </div>
                </div>

                <div className="p-4 bg-gray-50 border rounded-lg text-sm text-gray-600">
                  <strong>Note:</strong> You can change these settings anytime from your account preferences.
                </div>
              </div>
            )}

            {/* Step 5: Summary */}
            {currentStep === 5 && (
              <div className="space-y-6">
                <div className="text-center py-6">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="h-8 w-8 text-green-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    You're All Set!
                  </h2>
                  <p className="text-gray-600">
                    Your MyCRM account is ready to use
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 className="font-semibold text-blue-900 mb-2">What's Next?</h3>
                    <ul className="space-y-2 text-sm text-blue-700">
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>Explore your personalized dashboard</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>Add your first contacts and leads</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>Set up workflows to automate tasks</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>Customize your sales pipeline</span>
                      </li>
                    </ul>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-semibold mb-1">Organization</h4>
                      <p className="text-sm text-gray-600">{orgData.name}</p>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-semibold mb-1">Team Size</h4>
                      <p className="text-sm text-gray-600">{teamMembers.length} member(s)</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 1 || loading}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          {currentStep < totalSteps ? (
            <Button
              onClick={handleNext}
              disabled={!isStepValid() || loading}
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleComplete}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700"
            >
              {loading ? 'Setting up...' : 'Complete Setup'}
              <CheckCircle2 className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>

        {/* Skip Button */}
        {currentStep < totalSteps && (
          <div className="text-center mt-4">
            <button
              className="text-sm text-gray-500 hover:text-gray-700"
              onClick={() => router.push('/dashboard')}
            >
              Skip onboarding
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
