'use client';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import DeveloperPortal from '@/components/developer/DeveloperPortal';

export default function DeveloperPage() {
  return (
    <ProtectedRoute>
      <MainLayout>
        <DeveloperPortal />
      </MainLayout>
    </ProtectedRoute>
  );
}

