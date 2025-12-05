/**
 * Enterprise Health Dashboard Page
 * =================================
 * 
 * System health monitoring and observability
 */

'use client';

import React from 'react';
import { HealthDashboard } from '@/components/enterprise/HealthDashboard';

export default function HealthPage() {
  return (
    <div className="container mx-auto py-8">
      <HealthDashboard />
    </div>
  );
}
