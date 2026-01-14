'use client';

/**
 * PWA Initializer Component
 * Registers service worker and sets up PWA features
 */

import { useEffect } from 'react';

import { registerServiceWorker } from '@/lib/registerServiceWorker';

export function PWAInitializer() {
  useEffect(() => {
    // Register service worker
    registerServiceWorker();

    // Prevent default iOS Safari behaviors for PWA
    if ('standalone' in window.navigator) {
      // Prevent zoom on double-tap
      let lastTouchEnd = 0;
      document.addEventListener('touchend', (event) => {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
          event.preventDefault();
        }
        lastTouchEnd = now;
      }, { passive: false });

      // Prevent pull-to-refresh on iOS
      let startY = 0;
      document.addEventListener('touchstart', (e) => {
        startY = e.touches[0].pageY;
      }, { passive: true });

      document.addEventListener('touchmove', (e) => {
        const y = e.touches[0].pageY;
        // Only prevent if at top of page
        if (window.scrollY === 0 && y > startY) {
          e.preventDefault();
        }
      }, { passive: false });
    }

    // Handle app visibility changes for sync
    document.addEventListener('visibilitychange', async () => {
      if (!document.hidden && navigator.onLine) {
        // App became visible and we're online - sync
        try {
          const { syncService } = await import('@/lib/offlineDB');
          await syncService.sync();
        } catch (error) {
          console.error('Sync failed:', error);
        }
      }
    });

    // Listen for online status changes
    window.addEventListener('online', async () => {
      console.warn('App is online - syncing...');
      try {
        const { syncService } = await import('@/lib/offlineDB');
        const result = await syncService.sync();
        if (result.synced > 0) {
          // Could show a toast notification here
          console.warn(`Successfully synced ${result.synced} items`);
        }
      } catch (error) {
        console.error('Sync failed:', error);
      }
    });

    window.addEventListener('offline', () => {
      console.warn('App is offline - changes will be queued');
    });

  }, []);

  return null;
}

