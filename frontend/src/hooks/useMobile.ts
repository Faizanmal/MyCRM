/**
 * Mobile-First Utilities and Hooks
 * PWA support, offline detection, and mobile optimizations
 */

import { useState, useEffect, useCallback } from 'react';

// Wake Lock API types
interface WakeLockSentinel {
  release: () => Promise<void>;
  addEventListener: (type: string, listener: () => void) => void;
}

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

// Device detection hook
export function useDevice() {
  const [device, setDevice] = useState({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    isTouch: false,
    isStandalone: false, // PWA mode
    orientation: 'portrait' as 'portrait' | 'landscape',
  });

  useEffect(() => {
    const updateDevice = () => {
      const width = window.innerWidth;
      const isMobile = width < 768;
      const isTablet = width >= 768 && width < 1024;
      const isDesktop = width >= 1024;
      const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      const orientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';

      setDevice({
        isMobile,
        isTablet,
        isDesktop,
        isTouch,
        isStandalone,
        orientation,
      });
    };

    updateDevice();
    window.addEventListener('resize', updateDevice);
    window.addEventListener('orientationchange', updateDevice);

    return () => {
      window.removeEventListener('resize', updateDevice);
      window.removeEventListener('orientationchange', updateDevice);
    };
  }, []);

  return device;
}

// Online/Offline detection hook
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      if (wasOffline) {
        // Trigger sync when coming back online
        if ('serviceWorker' in navigator && 'sync' in window) {
          navigator.serviceWorker.ready.then((registration) => {
            // @ts-expect-error Service worker sync API is not in standard types
            registration.sync?.register('sync-data');
          });
        }
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      setWasOffline(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [wasOffline]);

  return { isOnline, wasOffline };
}

// PWA install prompt hook
export function usePWAInstall() {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(() => window.matchMedia('(display-mode: standalone)').matches);
  const [isInstallable, setIsInstallable] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as BeforeInstallPromptEvent);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setInstallPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const promptInstall = useCallback(async () => {
    if (!installPrompt) return false;

    installPrompt.prompt();
    const { outcome } = await installPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setInstallPrompt(null);
      setIsInstallable(false);
      return true;
    }
    
    return false;
  }, [installPrompt]);

  return { isInstalled, isInstallable, promptInstall };
}

// Push notifications hook
export function usePushNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>(() => 'Notification' in window ? Notification.permission : 'default');
  const [subscription, setSubscription] = useState<PushSubscription | null>(null);

  useEffect(() => {
    // No need to set permission here, it's initialized
  }, []);

  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      return false;
    }

    const result = await Notification.requestPermission();
    setPermission(result);
    return result === 'granted';
  }, []);

  const subscribe = useCallback(async () => {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      return null;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      
      // Get VAPID public key from server
      const response = await fetch('/api/v1/notifications/vapid-key');
      const { publicKey } = await response.json();

      const sub = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: publicKey,
      });

      setSubscription(sub);
      
      // Send subscription to server
      await fetch('/api/v1/notifications/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sub),
      });

      return sub;
    } catch (error) {
      console.error('Push subscription failed:', error);
      return null;
    }
  }, []);

  const unsubscribe = useCallback(async () => {
    if (subscription) {
      await subscription.unsubscribe();
      setSubscription(null);
      
      // Notify server
      await fetch('/api/v1/notifications/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
      });
    }
  }, [subscription]);

  return {
    permission,
    isSubscribed: !!subscription,
    requestPermission,
    subscribe,
    unsubscribe,
  };
}

// Offline data sync hook
export function useOfflineSync<T>(
  key: string,
  fetchFn: () => Promise<T>,
  options?: { syncInterval?: number }
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);
  const { isOnline } = useOnlineStatus();

  // Load from cache first
  useEffect(() => {
    const loadCached = async () => {
      try {
        const cached = localStorage.getItem(`offline_${key}`);
        if (cached) {
          const { data, timestamp } = JSON.parse(cached);
          setData(data);
          setLastSynced(new Date(timestamp));
        }
      } catch (e) {
        console.error('Failed to load cached data:', e);
      }
      setLoading(false);
    };

    loadCached();
  }, [key]);

  // Fetch fresh data when online
  const sync = useCallback(async () => {
    if (!isOnline) return;

    try {
      setLoading(true);
      const freshData = await fetchFn();
      setData(freshData);
      setLastSynced(new Date());
      
      // Cache the data
      localStorage.setItem(`offline_${key}`, JSON.stringify({
        data: freshData,
        timestamp: new Date().toISOString(),
      }));
      
      setError(null);
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, [key, fetchFn, isOnline]);

  // Auto-sync on mount and when coming online
  useEffect(() => {
    sync();
  }, [isOnline]); // eslint-disable-line react-hooks/exhaustive-deps

  // Optional interval sync
  useEffect(() => {
    if (options?.syncInterval && isOnline) {
      const interval = setInterval(sync, options.syncInterval);
      return () => clearInterval(interval);
    }
  }, [options?.syncInterval, isOnline, sync]);

  return { data, loading, error, lastSynced, sync };
}

// Touch gestures hook
export function useSwipeGesture(
  onSwipeLeft?: () => void,
  onSwipeRight?: () => void,
  onSwipeUp?: () => void,
  onSwipeDown?: () => void,
  threshold = 50
) {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    setTouchStart({
      x: e.touches[0].clientX,
      y: e.touches[0].clientY,
    });
  }, []);

  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    if (!touchStart) return;

    const touchEnd = {
      x: e.changedTouches[0].clientX,
      y: e.changedTouches[0].clientY,
    };

    const deltaX = touchEnd.x - touchStart.x;
    const deltaY = touchEnd.y - touchStart.y;

    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      // Horizontal swipe
      if (deltaX > threshold && onSwipeRight) {
        onSwipeRight();
      } else if (deltaX < -threshold && onSwipeLeft) {
        onSwipeLeft();
      }
    } else {
      // Vertical swipe
      if (deltaY > threshold && onSwipeDown) {
        onSwipeDown();
      } else if (deltaY < -threshold && onSwipeUp) {
        onSwipeUp();
      }
    }

    setTouchStart(null);
  }, [touchStart, threshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown]);

  return { handleTouchStart, handleTouchEnd };
}

// Screen wake lock hook (keep screen on)
export function useWakeLock() {
  const [wakeLock, setWakeLock] = useState<WakeLockSentinel | null>(null);
  const [isActive, setIsActive] = useState(false);

  const request = useCallback(async () => {
    if ('wakeLock' in navigator) {
      try {
        const lock = await (navigator as Navigator & { wakeLock?: { request: (type: string) => Promise<WakeLockSentinel> } }).wakeLock?.request('screen');
        setWakeLock(lock);
        setIsActive(true);
        
        lock.addEventListener('release', () => {
          setIsActive(false);
        });
        
        return true;
      } catch (e) {
        console.error('Wake lock request failed:', e);
        return false;
      }
    }
    return false;
  }, []);

  const release = useCallback(async () => {
    if (wakeLock) {
      await wakeLock.release();
      setWakeLock(null);
      setIsActive(false);
    }
  }, [wakeLock]);

  // Re-acquire on visibility change
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && isActive && !wakeLock) {
        await request();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [isActive, wakeLock, request]);

  return { isActive, request, release };
}

// Share API hook
export function useShare() {
  const [canShare] = useState(() => 'share' in navigator);

  useEffect(() => {
    // No need to set canShare, it's initialized
  }, []);

  const share = useCallback(async (data: ShareData) => {
    if (!canShare) return false;

    try {
      await navigator.share(data);
      return true;
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        console.error('Share failed:', e);
      }
      return false;
    }
  }, [canShare]);

  return { canShare, share };
}
