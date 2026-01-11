'use client';

/**
 * PWA Install Prompt Component
 * Shows install prompt for adding app to home screen
 */

import React, { useEffect, useState } from 'react';
import { usePWAInstall } from '@/hooks/useMobile';
import { XMarkIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline';

interface PWAInstallPromptProps {
  delay?: number; // Delay before showing prompt (ms)
}

export function PWAInstallPrompt({ delay = 5000 }: PWAInstallPromptProps) {
  const { isInstalled, isInstallable, promptInstall } = usePWAInstall();
  const [show, setShow] = useState(false);
  const [dismissed, setDismissed] = useState(() => {
    const wasDismissed = localStorage.getItem('pwa-install-dismissed');
    if (wasDismissed) {
      const dismissedAt = new Date(wasDismissed);
      const daysSince = (Date.now() - dismissedAt.getTime()) / (1000 * 60 * 60 * 24);
      return daysSince < 7;
    }
    return false;
  });

  useEffect(() => {
    // Show prompt after delay if not dismissed
    if (isInstallable && !isInstalled && !dismissed) {
      const timer = setTimeout(() => setShow(true), delay);
      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled, dismissed, delay]);

  const handleInstall = async () => {
    const installed = await promptInstall();
    if (installed) {
      setShow(false);
    }
  };

  const handleDismiss = () => {
    setShow(false);
    setDismissed(true);
    localStorage.setItem('pwa-install-dismissed', new Date().toISOString());
  };

  if (!show || dismissed || isInstalled || !isInstallable) {
    return null;
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 md:left-auto md:right-6 md:bottom-6 md:w-80">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-4">
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>

        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-xl flex items-center justify-center">
            <DevicePhoneMobileIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Install MyCRM
            </h3>
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Add to your home screen for quick access and offline support.
            </p>
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          <button
            onClick={handleDismiss}
            className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Not now
          </button>
          <button
            onClick={handleInstall}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Install
          </button>
        </div>
      </div>
    </div>
  );
}

// iOS-specific install instructions
export function IOSInstallPrompt() {
  const [show, setShow] = useState(false);
  const isIOS = (() => {
    const ua = window.navigator.userAgent;
    const iOS = !!ua.match(/iPad/i) || !!ua.match(/iPhone/i);
    const webkit = !!ua.match(/WebKit/i);
    const isSafari = iOS && webkit && !ua.match(/CriOS/i);
    const isStandalone = ('standalone' in window.navigator) && (window.navigator as Navigator & { standalone?: boolean }).standalone;
    return iOS && isSafari && !isStandalone && !localStorage.getItem('ios-install-dismissed');
  })();

  useEffect(() => {
    if (isIOS) {
      setTimeout(() => setShow(true), 5000);
    }
  }, [isIOS]);

  const handleDismiss = () => {
    setShow(false);
    localStorage.setItem('ios-install-dismissed', 'true');
  };

  if (!show || !isIOS) {
    return null;
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-4">
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>

        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          Install MyCRM
        </h3>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          To install this app on your iPhone:
        </p>
        
        <ol className="mt-3 space-y-2 text-xs text-gray-600 dark:text-gray-300">
          <li className="flex items-center gap-2">
            <span className="flex-shrink-0 w-5 h-5 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center text-xs font-medium">
              1
            </span>
            Tap the share button
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
            </svg>
          </li>
          <li className="flex items-center gap-2">
            <span className="flex-shrink-0 w-5 h-5 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center text-xs font-medium">
              2
            </span>
            Scroll down and tap &quot;Add to Home Screen&quot;
          </li>
          <li className="flex items-center gap-2">
            <span className="flex-shrink-0 w-5 h-5 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center text-xs font-medium">
              3
            </span>
            Tap &quot;Add&quot; to confirm
          </li>
        </ol>
      </div>

      {/* Arrow pointing to share button */}
      <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2">
        <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-white dark:border-t-gray-800" />
      </div>
    </div>
  );
}

// Offline indicator
export function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white text-center py-2 text-sm font-medium">
      <div className="flex items-center justify-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
        </svg>
        You&apos;re offline. Some features may be limited.
      </div>
    </div>
  );
}

// Update available prompt
export function UpdatePrompt() {
  const [updateAvailable, setUpdateAvailable] = useState(false);

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        setUpdateAvailable(true);
      });
    }
  }, []);

  const handleUpdate = () => {
    window.location.reload();
  };

  if (!updateAvailable) return null;

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 md:left-auto md:right-6 md:w-80">
      <div className="bg-green-600 text-white rounded-xl shadow-lg p-4 flex items-center justify-between">
        <span className="text-sm font-medium">A new version is available</span>
        <button
          onClick={handleUpdate}
          className="ml-4 px-3 py-1 bg-white text-green-600 text-sm font-medium rounded-lg hover:bg-green-50 transition-colors"
        >
          Update
        </button>
      </div>
    </div>
  );
}
