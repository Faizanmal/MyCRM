/**
 * Enterprise Compliance Dashboard Page
 * =====================================
 * 
 * GDPR, SOC2, and regulatory compliance monitoring
 */

'use client';

import React from 'react';
import { ComplianceDashboard } from '@/components/enterprise/ComplianceDashboard';

export default function CompliancePage() {
  return (
    <div className="container mx-auto py-8">
      <ComplianceDashboard />
    </div>
  );
}
