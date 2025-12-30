'use client';

import { ReactNode } from 'react';
import SettingsSidebar from '@/components/SettingsSidebar';

export default function SettingsLayout({ children }: { children: ReactNode }) {
    return (
        <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
            <SettingsSidebar />
            <main className="flex-1 overflow-auto">
                {children}
            </main>
        </div>
    );
}
