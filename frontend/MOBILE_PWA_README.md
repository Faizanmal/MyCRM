# 📱 Mobile-First & PWA Features

## Overview

MyCRM now includes comprehensive mobile-first design and Progressive Web App (PWA) capabilities, providing a native app-like experience on mobile devices with offline support, push notifications, and optimized performance.

## Features Implemented

### 🎨 Mobile UI Components

#### Navigation & Layout
- **MobileNav** - Bottom navigation bar with safe area support
- **MobileShell** - App shell structure for consistent mobile layout
- **MobileHeader** - Optimized header component with actions
- **FloatingActionButton (FAB)** - Quick action button with mobile positioning

#### Interactive Components
- **PullToRefresh** - Native pull-to-refresh functionality
- **SwipeableCard** - Swipeable cards with left/right actions
- **BottomSheet** - Modal bottom sheets for mobile
- **ActionSheet** - Native action sheet menus
- **MobileSearchBar** - Touch-optimized search interface
- **MobileListItem** - Optimized list items for touch targets

#### PWA Components
- **PWAInstallPrompt** - Smart install prompt for Android/PWA
- **IOSInstallPrompt** - iOS-specific installation instructions
- **OfflineIndicator** - Online/offline status display
- **UpdatePrompt** - New version available notification

### 🪝 Custom Hooks

Located in `src/hooks/useMobile.ts`:

- **useDevice()** - Device detection (mobile/tablet/desktop, orientation, PWA mode)
- **useOnlineStatus()** - Real-time online/offline detection with auto-sync
- **usePWAInstall()** - PWA installation prompt management
- **usePushNotifications()** - Push notification subscription handling
- **useOfflineSync()** - Automatic offline data synchronization
- **useSwipeGesture()** - Touch gesture detection (swipe left/right/up/down)
- **useWakeLock()** - Keep screen awake during important tasks
- **useShare()** - Native share API integration

### 💾 Offline Data Management

#### IndexedDB Wrapper (`src/lib/offlineDB.ts`)

```typescript
import { offlineDB, STORES } from '@/lib/offlineDB';

// Store data for offline access
await offlineDB.put(STORES.CONTACTS, contact);

// Retrieve offline data
const contacts = await offlineDB.getAll(STORES.CONTACTS);

// Search with filters
const activeLeads = await offlineDB.filter(
  STORES.LEADS,
  (lead) => lead.status === 'active'
);

// Paginated queries
const { items, total } = await offlineDB.getPaginated(STORES.CONTACTS, {
  page: 1,
  limit: 20,
  sortBy: 'updated_at',
  sortOrder: 'desc'
});
```

#### Sync Queue

Changes made offline are automatically queued and synced when connection is restored:

```typescript
import { offlineDB, syncService } from '@/lib/offlineDB';

// Queue an offline change
await offlineDB.addToSyncQueue({
  store: STORES.CONTACTS,
  operation: 'update',
  data: updatedContact,
});

// Manually trigger sync
const result = await syncService.sync();
console.log(`Synced ${result.synced} items, ${result.failed} failed`);
```

### 🔔 Service Worker Features

Enhanced service worker (`public/sw-enhanced.js`) provides:

- **Offline Caching**: Static assets, API responses, and images
- **Background Sync**: Automatic sync when connection is restored
- **Push Notifications**: Real-time notifications with action buttons
- **Update Detection**: Automatic app updates with user prompt
- **Cache Strategies**:
  - Static assets: Cache-first with stale-while-revalidate
  - API calls: Network-first with cache fallback
  - Images: Cache-first with lazy loading

### 🎯 Usage Examples

#### Basic Mobile Page

```typescript
'use client';

import { useState } from 'react';
import { MobileShell, MobileHeader } from '@/components/mobile';
import { useDevice } from '@/hooks/useMobile';

export default function MyMobilePage() {
  const device = useDevice();
  const [showMenu, setShowMenu] = useState(false);

  return (
    <MobileShell
      showFAB={true}
      onFABClick={() => setShowMenu(true)}
      fabLabel="Add New"
    >
      <MobileHeader
        title="My Page"
        leftAction={<BackButton />}
        rightAction={<MenuButton />}
      />
      
      {/* Your content */}
    </MobileShell>
  );
}
```

#### Offline-First Data Fetching

```typescript
'use client';

import { useOfflineSync } from '@/hooks/useMobile';

export default function ContactsList() {
  const { data, loading, sync } = useOfflineSync(
    'contacts',
    async () => {
      const res = await fetch('/api/v1/contacts/');
      return res.json();
    },
    { syncInterval: 5 * 60 * 1000 } // Sync every 5 minutes
  );

  return (
    <div>
      <button onClick={sync}>Refresh</button>
      {loading ? <Skeleton /> : <ContactList contacts={data} />}
    </div>
  );
}
```

#### Swipeable List Items

```typescript
import { SwipeableCard } from '@/components/mobile';
import { TrashIcon, ArchiveIcon } from '@heroicons/react/24/outline';

<SwipeableCard
  onSwipeLeft={() => deleteItem(item.id)}
  onSwipeRight={() => archiveItem(item.id)}
  leftAction={<ArchiveIcon className="w-6 h-6 text-white" />}
  rightAction={<TrashIcon className="w-6 h-6 text-white" />}
>
  <ItemContent item={item} />
</SwipeableCard>
```

#### Push Notifications

```typescript
'use client';

import { usePushNotifications } from '@/hooks/useMobile';

export default function NotificationSettings() {
  const { permission, isSubscribed, requestPermission, subscribe } = 
    usePushNotifications();

  const handleEnable = async () => {
    if (permission !== 'granted') {
      const granted = await requestPermission();
      if (!granted) return;
    }
    await subscribe();
  };

  return (
    <button onClick={handleEnable} disabled={isSubscribed}>
      {isSubscribed ? 'Notifications Enabled' : 'Enable Notifications'}
    </button>
  );
}
```

## Mobile-First CSS Classes

New utility classes in `globals.css`:

```css
/* Safe area insets for notches */
.safe-area-top
.safe-area-bottom
.safe-area-left
.safe-area-right
.safe-area-inset

/* Touch optimizations */
.touch-target       /* Min 44x44px tap targets */
.momentum-scroll    /* Smooth iOS scrolling */
.no-select         /* Disable text selection */

/* Mobile animations */
.animate-slide-up
.haptic-feedback

/* Mobile layouts */
.mobile-card
.bottom-sheet
.mobile-nav
.fab

/* Loading states */
.skeleton
```

## PWA Configuration

### Manifest (`public/manifest.json`)

Already configured with:
- App name and branding
- Icons (192x192, 512x512)
- Shortcuts (Dashboard, Contacts, Deals)
- Display mode: standalone
- Theme color and background

### Installation

The app automatically prompts users to install on:
- **Android/Chrome**: Native install banner + custom prompt
- **iOS Safari**: Step-by-step instructions modal

Users can install by:
1. Clicking "Install" in browser menu
2. Accepting the install prompt
3. Following iOS-specific instructions

## Offline Support

### What Works Offline:

✅ View cached contacts, leads, and deals
✅ Create/edit records (queued for sync)
✅ Browse previously viewed pages
✅ Access static assets and UI
✅ View cached images

### Auto-Sync Triggers:

- App becomes online
- App visibility change (tab focus)
- Manual refresh action
- Service worker background sync

## Performance Optimizations

1. **Code Splitting**: Mobile components loaded on-demand
2. **Image Optimization**: WebP format with fallbacks
3. **Cache Strategies**: Intelligent caching per resource type
4. **Lazy Loading**: Components and routes lazy-loaded
5. **Bundle Size**: Mobile-specific bundles

## Testing

### Test PWA Features:

1. **Offline Mode**:
   ```bash
   # In DevTools Network tab
   - Set throttling to "Offline"
   - Reload page (should show offline.html)
   - Try creating/editing data (should queue)
   ```

2. **Install Prompt**:
   ```bash
   # Desktop Chrome
   - Open DevTools > Application > Manifest
   - Click "Add to home screen"
   
   # Mobile
   - Visit from mobile browser
   - Accept install prompt
   ```

3. **Service Worker**:
   ```bash
   # DevTools > Application > Service Workers
   - Verify registration
   - Test "Update on reload"
   - Check cache storage
   ```

4. **Push Notifications**:
   ```bash
   # DevTools > Application > Notifications
   - Request permission
   - Send test notification
   - Verify receipt
   ```

## Browser Support

| Feature | Chrome | Safari | Firefox | Edge |
|---------|--------|--------|---------|------|
| Service Worker | ✅ | ✅ | ✅ | ✅ |
| PWA Install | ✅ | ✅* | ✅ | ✅ |
| Push Notifications | ✅ | ✅** | ✅ | ✅ |
| Background Sync | ✅ | ❌ | ❌ | ✅ |
| IndexedDB | ✅ | ✅ | ✅ | ✅ |

*Safari iOS 16.4+
**Safari iOS 16.4+, requires user permission

## Deployment Checklist

- [ ] HTTPS enabled (required for PWA)
- [ ] manifest.json accessible at root
- [ ] Service worker registered
- [ ] Icons generated (192x192, 512x512)
- [ ] Offline fallback page created
- [ ] Push notification VAPID keys configured
- [ ] Cache versioning implemented
- [ ] Analytics tracking offline events

## Future Enhancements

Potential additions:
- [ ] Periodic background sync for automatic updates
- [ ] Advanced offline conflict resolution
- [ ] Biometric authentication (Face ID/Touch ID)
- [ ] App shortcuts API
- [ ] File System Access API for exports
- [ ] Badging API for notification counts
- [ ] Screen Wake Lock for presentations
- [ ] Clipboard API integration

## Troubleshooting

### Service Worker Not Registering

```typescript
// Check registration
navigator.serviceWorker.getRegistrations().then(regs => {
  console.log('Registered SWs:', regs);
});

// Force update
navigator.serviceWorker.getRegistration().then(reg => {
  reg?.update();
});
```

### Offline Data Not Syncing

```typescript
import { offlineDB } from '@/lib/offlineDB';

// Check sync queue
const queue = await offlineDB.getSyncQueue();
console.log('Pending sync items:', queue);

// Clear corrupted queue
await offlineDB.clear(STORES.SYNC_QUEUE);
```

### Cache Issues

```bash
# Clear all caches
Application > Storage > Clear site data

# Or programmatically:
caches.keys().then(names => {
  names.forEach(name => caches.delete(name));
});
```

## Resources

- [Web.dev PWA Guide](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [IndexedDB Guide](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [Push Notifications](https://web.dev/push-notifications-overview/)
