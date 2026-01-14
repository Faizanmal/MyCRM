/**
 * IndexedDB Wrapper for Offline Storage
 * Provides type-safe access to IndexedDB for CRM data
 */

const DB_NAME = 'mycrm-offline';
const DB_VERSION = 1;

// Store names
export const STORES = {
  CONTACTS: 'contacts',
  LEADS: 'leads',
  OPPORTUNITIES: 'opportunities',
  TASKS: 'tasks',
  COMMUNICATIONS: 'communications',
  SYNC_QUEUE: 'sync-queue',
  CACHE_META: 'cache-meta',
} as const;

type StoreName = (typeof STORES)[keyof typeof STORES];

interface SyncQueueItem {
  id: string;
  store: StoreName;
  operation: 'create' | 'update' | 'delete';
  data: Record<string, unknown>;
  timestamp: number;
  retries: number;
}

interface CacheMeta {
  store: StoreName;
  lastSync: number;
  etag?: string;
}

class OfflineDB {
  private db: IDBDatabase | null = null;
  private dbPromise: Promise<IDBDatabase> | null = null;

  private async openDB(): Promise<IDBDatabase> {
    if (this.db) return this.db;
    if (this.dbPromise) return this.dbPromise;

    this.dbPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(request.result);
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create stores
        if (!db.objectStoreNames.contains(STORES.CONTACTS)) {
          const contactStore = db.createObjectStore(STORES.CONTACTS, { keyPath: 'id' });
          contactStore.createIndex('email', 'email', { unique: false });
          contactStore.createIndex('company', 'company', { unique: false });
          contactStore.createIndex('updatedAt', 'updated_at', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.LEADS)) {
          const leadStore = db.createObjectStore(STORES.LEADS, { keyPath: 'id' });
          leadStore.createIndex('status', 'status', { unique: false });
          leadStore.createIndex('score', 'score', { unique: false });
          leadStore.createIndex('updatedAt', 'updated_at', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.OPPORTUNITIES)) {
          const oppStore = db.createObjectStore(STORES.OPPORTUNITIES, { keyPath: 'id' });
          oppStore.createIndex('stage', 'stage', { unique: false });
          oppStore.createIndex('value', 'value', { unique: false });
          oppStore.createIndex('closeDate', 'close_date', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.TASKS)) {
          const taskStore = db.createObjectStore(STORES.TASKS, { keyPath: 'id' });
          taskStore.createIndex('status', 'status', { unique: false });
          taskStore.createIndex('dueDate', 'due_date', { unique: false });
          taskStore.createIndex('priority', 'priority', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.COMMUNICATIONS)) {
          const commStore = db.createObjectStore(STORES.COMMUNICATIONS, { keyPath: 'id' });
          commStore.createIndex('contactId', 'contact_id', { unique: false });
          commStore.createIndex('type', 'type', { unique: false });
          commStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: 'id' });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncStore.createIndex('store', 'store', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.CACHE_META)) {
          db.createObjectStore(STORES.CACHE_META, { keyPath: 'store' });
        }
      };
    });

    return this.dbPromise;
  }

  // Get all items from a store
  async getAll<T>(storeName: StoreName): Promise<T[]> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Get a single item by ID
  async get<T>(storeName: StoreName, id: string | number): Promise<T | undefined> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Get items by index
  async getByIndex<T>(
    storeName: StoreName,
    indexName: string,
    value: IDBValidKey
  ): Promise<T[]> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const index = store.index(indexName);
      const request = index.getAll(value);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Put (upsert) an item
  async put<T extends { id: string | number }>(storeName: StoreName, item: T): Promise<T> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(item);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(item);
    });
  }

  // Put multiple items
  async putMany<T extends { id: string | number }>(storeName: StoreName, items: T[]): Promise<void> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);

      items.forEach((item) => store.put(item));

      transaction.onerror = () => reject(transaction.error);
      transaction.oncomplete = () => resolve();
    });
  }

  // Delete an item
  async delete(storeName: StoreName, id: string | number): Promise<void> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  // Clear all items from a store
  async clear(storeName: StoreName): Promise<void> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  // Count items in a store
  async count(storeName: StoreName): Promise<number> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.count();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Sync queue operations
  async addToSyncQueue(item: Omit<SyncQueueItem, 'id' | 'timestamp' | 'retries'>): Promise<void> {
    const syncItem: SyncQueueItem = {
      ...item,
      id: `${item.store}-${item.operation}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      retries: 0,
    };
    await this.put(STORES.SYNC_QUEUE, syncItem);
  }

  async getSyncQueue(): Promise<SyncQueueItem[]> {
    const items = await this.getAll<SyncQueueItem>(STORES.SYNC_QUEUE);
    return items.sort((a, b) => a.timestamp - b.timestamp);
  }

  async removeSyncItem(id: string): Promise<void> {
    await this.delete(STORES.SYNC_QUEUE, id);
  }

  async updateSyncItemRetries(id: string, retries: number): Promise<void> {
    const item = await this.get<SyncQueueItem>(STORES.SYNC_QUEUE, id);
    if (item) {
      await this.put(STORES.SYNC_QUEUE, { ...item, retries });
    }
  }

  // Cache metadata operations
  async getCacheMeta(storeName: StoreName): Promise<CacheMeta | undefined> {
    return this.get<CacheMeta>(STORES.CACHE_META, storeName);
  }

  async setCacheMeta(meta: CacheMeta): Promise<void> {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORES.CACHE_META, 'readwrite');
      const store = transaction.objectStore(STORES.CACHE_META);
      const request = store.put(meta);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  // Search items with a filter function
  async filter<T>(storeName: StoreName, predicate: (item: T) => boolean): Promise<T[]> {
    const items = await this.getAll<T>(storeName);
    return items.filter(predicate);
  }

  // Paginated get
  async getPaginated<T extends Record<string, unknown>>(
    storeName: StoreName,
    options: { page: number; limit: number; sortBy?: string; sortOrder?: 'asc' | 'desc' }
  ): Promise<{ items: T[]; total: number }> {
    const allItems = await this.getAll<T>(storeName);
    const total = allItems.length;

    // Sort if needed
    const sorted = [...allItems];
    if (options.sortBy) {
      sorted.sort((a: T, b: T) => {
        const aVal = a[options.sortBy!] as string | number;
        const bVal = b[options.sortBy!] as string | number;
        if (options.sortOrder === 'desc') {
          return bVal > aVal ? 1 : -1;
        }
        return aVal > bVal ? 1 : -1;
      });
    }

    // Paginate
    const start = (options.page - 1) * options.limit;
    const items = sorted.slice(start, start + options.limit);

    return { items, total };
  }
}

// Singleton instance
export const offlineDB = new OfflineDB();

// Sync service
export class SyncService {
  private isSyncing = false;

  async sync(): Promise<{ synced: number; failed: number }> {
    if (this.isSyncing) {
      return { synced: 0, failed: 0 };
    }

    if (!navigator.onLine) {
      return { synced: 0, failed: 0 };
    }

    this.isSyncing = true;
    let synced = 0;
    let failed = 0;

    try {
      const queue = await offlineDB.getSyncQueue();

      for (const item of queue) {
        try {
          await this.processSyncItem(item);
          await offlineDB.removeSyncItem(item.id);
          synced++;
        } catch (error) {
          console.error('Sync failed for item:', item.id, error);
          
          if (item.retries >= 3) {
            // Give up after 3 retries
            await offlineDB.removeSyncItem(item.id);
            failed++;
          } else {
            await offlineDB.updateSyncItemRetries(item.id, item.retries + 1);
          }
        }
      }
    } finally {
      this.isSyncing = false;
    }

    return { synced, failed };
  }

  private async processSyncItem(item: SyncQueueItem): Promise<void> {
    const endpoint = this.getEndpoint(item.store);
    const token = localStorage.getItem('token');

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    switch (item.operation) {
      case 'create':
        await fetch(endpoint, {
          method: 'POST',
          headers,
          body: JSON.stringify(item.data),
        });
        break;

      case 'update':
        await fetch(`${endpoint}${item.data.id}/`, {
          method: 'PATCH',
          headers,
          body: JSON.stringify(item.data),
        });
        break;

      case 'delete':
        await fetch(`${endpoint}${item.data.id}/`, {
          method: 'DELETE',
          headers,
        });
        break;
    }
  }

  private getEndpoint(store: StoreName): string {
    const endpoints: Record<StoreName, string> = {
      [STORES.CONTACTS]: '/api/v1/contacts/',
      [STORES.LEADS]: '/api/v1/leads/',
      [STORES.OPPORTUNITIES]: '/api/v1/opportunities/',
      [STORES.TASKS]: '/api/v1/tasks/',
      [STORES.COMMUNICATIONS]: '/api/v1/communications/',
      [STORES.SYNC_QUEUE]: '',
      [STORES.CACHE_META]: '',
    };
    return endpoints[store] || '';
  }

  // Full sync for a store (download all data)
  async fullSync(storeName: StoreName): Promise<void> {
    const endpoint = this.getEndpoint(storeName);
    if (!endpoint) return;

    const token = localStorage.getItem('token');
    const headers: HeadersInit = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(endpoint, { headers });
    
    if (response.ok) {
      const data = await response.json();
      const items = Array.isArray(data) ? data : data.results || [];
      
      await offlineDB.clear(storeName);
      await offlineDB.putMany(storeName, items);
      await offlineDB.setCacheMeta({
        store: storeName,
        lastSync: Date.now(),
        etag: response.headers.get('etag') || undefined,
      });
    }
  }
}

export const syncService = new SyncService();

// Register background sync if supported
if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
  window.addEventListener('online', () => {
    syncService.sync().then(({ synced, failed }) => {
      if (synced > 0 || failed > 0) {
        console.warn(`Sync complete: ${synced} synced, ${failed} failed`);
      }
    });
  });
}

