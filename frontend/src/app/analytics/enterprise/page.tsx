/**
 * Enterprise Analytics Dashboard Page
 * =====================================
 * 
 * Sales intelligence and performance analytics
 */

'use client';

import React from 'react';
import { AnalyticsDashboard } from '@/components/enterprise/AnalyticsDashboard';

export default function EntAnalyticsPage() {
  return (
    <div className="container mx-auto py-8">
      <AnalyticsDashboard />
    </div>
  );
}
