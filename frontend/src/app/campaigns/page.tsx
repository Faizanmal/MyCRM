'use client';

import { Mail } from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import EmailCampaignManager from '@/components/enterprise/EmailCampaignManager';

export default function CampaignsPage() {
  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Mail className="w-8 h-8 text-blue-600" />
                Email Campaigns
              </h1>
              <p className="text-gray-500 mt-1">Create and manage your email marketing campaigns</p>
            </div>
          </div>

          {/* Campaign Manager */}
          <Card>
            <CardContent className="p-6">
              <EmailCampaignManager />
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

