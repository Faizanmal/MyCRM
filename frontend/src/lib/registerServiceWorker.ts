/**
 * Service Worker Registration
 * Registers the enhanced service worker for PWA support
 */

export function registerServiceWorker(): void {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return;
  }

  window.addEventListener('load', async () => {
    try {
      // Register the enhanced service worker
      const registration = await navigator.serviceWorker.register('/sw-enhanced.js', {
        scope: '/',
      });

      console.warn('Service Worker registered:', registration.scope);

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (!newWorker) return;

        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New service worker available
            console.warn('New service worker available');
            
            // Notify user of update
            if (window.confirm('A new version is available! Reload to update?')) {
              newWorker.postMessage({ type: 'SKIP_WAITING' });
              window.location.reload();
            }
          }
        });
      });

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        const { type, payload } = event.data;

        switch (type) {
          case 'SYNC_REQUIRED':
            // Trigger sync when service worker requests it
            import('./offlineDB').then(({ syncService }) => {
              syncService.sync().then(({ synced, failed }) => {
                if (synced > 0) {
                  console.warn(`Synced ${synced} items`);
                }
                if (failed > 0) {
                  console.warn(`Failed to sync ${failed} items`);
                }
              });
            });
            break;

          case 'CACHE_UPDATED':
            console.warn('Cache updated:', payload);
            break;

          case 'NOTIFICATION_CLICKED':
            // Handle notification clicks
            console.warn('Notification clicked:', payload);
            break;
        }
      });

      // Handle controller change (when new SW takes over)
      let refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (!refreshing) {
          refreshing = true;
          window.location.reload();
        }
      });

      // Periodic sync for background updates (if supported)
      if ('periodicSync' in registration) {
        try {
          // @ts-expect-error Periodic sync API is not in standard ServiceWorkerRegistration types
          await registration.periodicSync.register('sync-contacts', {
            minInterval: 24 * 60 * 60 * 1000, // 24 hours
          });
          console.warn('Periodic sync registered');
        } catch (error) {
          console.warn('Periodic sync not available:', error);
        }
      }

      // Check for updates every hour
      setInterval(() => {
        registration.update();
      }, 60 * 60 * 1000);

    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  });

  // Unregister on unload (for development)
  if (process.env.NODE_ENV === 'development') {
    window.addEventListener('beforeunload', async () => {
      // const registrations = await navigator.serviceWorker.getRegistrations();
      // Don't unregister in dev - keep for testing
      // for (const registration of registrations) {
      //   await registration.unregister();
      // }
    });
  }
}

// Helper to check if app is running as PWA
export function isPWA(): boolean {
  if (typeof window === 'undefined') return false;
  
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    // @ts-expect-error Navigator standalone property is iOS-specific and not in standard types
    window.navigator.standalone === true ||
    document.referrer.includes('android-app://')
  );
}

// Helper to get SW registration
export async function getServiceWorkerRegistration(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) return null;
  
  try {
    return await navigator.serviceWorker.ready;
  } catch (error) {
    console.error('Failed to get SW registration:', error);
    return null;
  }
}

