'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

// ==================== Types ====================

export type Role = 'admin' | 'manager' | 'sales_rep' | 'viewer' | 'guest';

export type Permission =
    // Dashboard
    | 'view_dashboard'
    | 'view_admin_dashboard'
    | 'view_analytics'

    // Contacts
    | 'view_contacts'
    | 'create_contacts'
    | 'edit_contacts'
    | 'delete_contacts'
    | 'export_contacts'
    | 'import_contacts'

    // Deals
    | 'view_deals'
    | 'create_deals'
    | 'edit_deals'
    | 'delete_deals'
    | 'close_deals'

    // Tasks
    | 'view_tasks'
    | 'create_tasks'
    | 'edit_tasks'
    | 'delete_tasks'
    | 'assign_tasks'

    // Team
    | 'view_team'
    | 'manage_team'
    | 'invite_users'
    | 'remove_users'
    | 'assign_roles'

    // Settings
    | 'view_settings'
    | 'manage_settings'
    | 'manage_integrations'
    | 'view_billing'
    | 'manage_billing'

    // Reports
    | 'view_reports'
    | 'create_reports'
    | 'export_reports'

    // Admin
    | 'access_admin'
    | 'manage_organization'
    | 'view_audit_log';

export interface User {
    id: string;
    email: string;
    name: string;
    role: Role;
    permissions?: Permission[];
    avatar?: string;
    teamId?: string;
}

export interface RBACContextType {
    user: User | null;
    role: Role | null;
    permissions: Permission[];
    isLoading: boolean;
    hasPermission: (permission: Permission) => boolean;
    hasAnyPermission: (permissions: Permission[]) => boolean;
    hasAllPermissions: (permissions: Permission[]) => boolean;
    hasRole: (role: Role) => boolean;
    hasMinimumRole: (minimumRole: Role) => boolean;
    canAccessRoute: (route: string) => boolean;
    setUser: (user: User | null) => void;
}

// ==================== Role Hierarchy ====================

const roleHierarchy: Record<Role, number> = {
    guest: 0,
    viewer: 1,
    sales_rep: 2,
    manager: 3,
    admin: 4,
};

// ==================== Role Permissions ====================

const rolePermissions: Record<Role, Permission[]> = {
    guest: [
        'view_dashboard',
    ],

    viewer: [
        'view_dashboard',
        'view_contacts',
        'view_deals',
        'view_tasks',
        'view_reports',
    ],

    sales_rep: [
        'view_dashboard',
        'view_contacts',
        'create_contacts',
        'edit_contacts',
        'view_deals',
        'create_deals',
        'edit_deals',
        'close_deals',
        'view_tasks',
        'create_tasks',
        'edit_tasks',
        'view_reports',
        'view_settings',
    ],

    manager: [
        'view_dashboard',
        'view_analytics',
        'view_contacts',
        'create_contacts',
        'edit_contacts',
        'delete_contacts',
        'export_contacts',
        'import_contacts',
        'view_deals',
        'create_deals',
        'edit_deals',
        'delete_deals',
        'close_deals',
        'view_tasks',
        'create_tasks',
        'edit_tasks',
        'delete_tasks',
        'assign_tasks',
        'view_team',
        'manage_team',
        'invite_users',
        'view_reports',
        'create_reports',
        'export_reports',
        'view_settings',
        'manage_settings',
    ],

    admin: [
        'view_dashboard',
        'view_admin_dashboard',
        'view_analytics',
        'view_contacts',
        'create_contacts',
        'edit_contacts',
        'delete_contacts',
        'export_contacts',
        'import_contacts',
        'view_deals',
        'create_deals',
        'edit_deals',
        'delete_deals',
        'close_deals',
        'view_tasks',
        'create_tasks',
        'edit_tasks',
        'delete_tasks',
        'assign_tasks',
        'view_team',
        'manage_team',
        'invite_users',
        'remove_users',
        'assign_roles',
        'view_reports',
        'create_reports',
        'export_reports',
        'view_settings',
        'manage_settings',
        'manage_integrations',
        'view_billing',
        'manage_billing',
        'access_admin',
        'manage_organization',
        'view_audit_log',
    ],
};

// ==================== Route Permissions ====================

const routePermissions: Record<string, Permission[]> = {
    '/admin': ['access_admin'],
    '/admin/dashboard': ['view_admin_dashboard'],
    '/admin/users': ['manage_team'],
    '/admin/audit': ['view_audit_log'],
    '/settings/billing': ['view_billing'],
    '/settings/team': ['view_team'],
    '/settings/integrations': ['manage_integrations'],
    '/settings/organization': ['manage_organization'],
    '/contacts': ['view_contacts'],
    '/deals': ['view_deals'],
    '/tasks': ['view_tasks'],
    '/reports': ['view_reports'],
    '/analytics': ['view_analytics'],
};

// ==================== Context ====================

const RBACContext = createContext<RBACContextType | undefined>(undefined);

// ==================== Provider ====================

export function RBACProvider({ children }: { children: ReactNode }): React.JSX.Element {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Get effective permissions (role + custom)
    const permissions = useMemo(() => user
        ? [...rolePermissions[user.role], ...(user.permissions || [])]
        : [], [user]);

    // Load user from storage/API on mount
    useEffect(() => {
        const loadUser = async () => {
            try {
                // Try to load from localStorage first
                const stored = localStorage.getItem('crm_user');
                if (stored) {
                    setUser(JSON.parse(stored));
                }

                // Then verify with API (mock)
                // const response = await fetch('/api/auth/me');
                // if (response.ok) {
                //     const userData = await response.json();
                //     setUser(userData);
                // }
            } catch (error) {
                console.error('Failed to load user:', error);
            } finally {
                setIsLoading(false);
            }
        };

        loadUser();
    }, []);

    // Check if user has a specific permission
    const hasPermission = useCallback((permission: Permission): boolean => {
        return permissions.includes(permission);
    }, [permissions]);

    // Check if user has any of the given permissions
    const hasAnyPermission = useCallback((perms: Permission[]): boolean => {
        return perms.some(p => permissions.includes(p));
    }, [permissions]);

    // Check if user has all of the given permissions
    const hasAllPermissions = useCallback((perms: Permission[]): boolean => {
        return perms.every(p => permissions.includes(p));
    }, [permissions]);

    // Check if user has a specific role
    const hasRole = useCallback((role: Role): boolean => {
        return user?.role === role;
    }, [user]);

    // Check if user has at least the minimum role level
    const hasMinimumRole = useCallback((minimumRole: Role): boolean => {
        if (!user) return false;
        return roleHierarchy[user.role] >= roleHierarchy[minimumRole];
    }, [user]);

    // Check if user can access a route
    const canAccessRoute = useCallback((route: string): boolean => {
        // Find matching route pattern
        const matchingRoute = Object.keys(routePermissions).find(pattern => {
            if (pattern === route) return true;
            if (route.startsWith(pattern)) return true;
            return false;
        });

        if (!matchingRoute) return true; // Route not protected

        const requiredPermissions = routePermissions[matchingRoute];
        return hasAnyPermission(requiredPermissions);
    }, [hasAnyPermission]);

    // Update user and persist
    const handleSetUser = useCallback((newUser: User | null) => {
        setUser(newUser);
        if (newUser) {
            localStorage.setItem('crm_user', JSON.stringify(newUser));
        } else {
            localStorage.removeItem('crm_user');
        }
    }, []);

    return (
        <RBACContext.Provider value={{
            user,
            role: user?.role || null,
            permissions,
            isLoading,
            hasPermission,
            hasAnyPermission,
            hasAllPermissions,
            hasRole,
            hasMinimumRole,
            canAccessRoute,
            setUser: handleSetUser,
        }}>
            {children}
        </RBACContext.Provider>
    );
}

// ==================== Hook ====================

export function useRBAC(): RBACContextType {
    const context = useContext(RBACContext);
    if (context === undefined) {
        throw new Error('useRBAC must be used within a RBACProvider');
    }
    return context;
}

// ==================== Higher-Order Components ====================

interface WithPermissionProps {
    permission: Permission;
    fallback?: ReactNode;
    children: ReactNode;
}

export function WithPermission({ permission, fallback = null, children }: WithPermissionProps): React.ReactNode {
    const { hasPermission, isLoading } = useRBAC();

    if (isLoading) return null;
    if (!hasPermission(permission)) return <>{fallback}</>;

    return <>{children}</>;
}

interface WithRoleProps {
    role: Role;
    minimum?: boolean;
    fallback?: ReactNode;
    children: ReactNode;
}

export function WithRole({ role, minimum = false, fallback = null, children }: WithRoleProps): React.ReactNode {
    const { hasRole, hasMinimumRole, isLoading } = useRBAC();

    if (isLoading) return null;

    const hasAccess = minimum ? hasMinimumRole(role) : hasRole(role);
    if (!hasAccess) return <>{fallback}</>;

    return <>{children}</>;
}

// ==================== Protected Route Component ====================

interface ProtectedRouteProps {
    permission?: Permission;
    permissions?: Permission[];
    requireAll?: boolean;
    role?: Role;
    minimumRole?: Role;
    redirectTo?: string;
    fallback?: ReactNode;
    children: ReactNode;
}

export function ProtectedRoute({
    permission,
    permissions,
    requireAll = false,
    role,
    minimumRole,
    redirectTo = '/dashboard',
    fallback,
    children,
}: ProtectedRouteProps): React.ReactNode {
    const router = useRouter();
    const {
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
        hasRole,
        hasMinimumRole,
        isLoading,
    } = useRBAC();

    useEffect(() => {
        if (isLoading) return;

        let hasAccess = true;

        // Check single permission
        if (permission) {
            hasAccess = hasPermission(permission);
        }

        // Check multiple permissions
        if (permissions && permissions.length > 0) {
            hasAccess = requireAll
                ? hasAllPermissions(permissions)
                : hasAnyPermission(permissions);
        }

        // Check role
        if (role) {
            hasAccess = hasAccess && hasRole(role);
        }

        // Check minimum role
        if (minimumRole) {
            hasAccess = hasAccess && hasMinimumRole(minimumRole);
        }

        // Redirect if no access
        if (!hasAccess && !fallback) {
            router.push(redirectTo);
        }
    }, [
        isLoading,
        permission,
        permissions,
        requireAll,
        role,
        minimumRole,
        redirectTo,
        fallback,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
        hasRole,
        hasMinimumRole,
        router,
    ]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            </div>
        );
    }

    // Check access
    let hasAccess = true;

    if (permission) {
        hasAccess = hasPermission(permission);
    }

    if (permissions && permissions.length > 0) {
        hasAccess = requireAll
            ? hasAllPermissions(permissions)
            : hasAnyPermission(permissions);
    }

    if (role) {
        hasAccess = hasAccess && hasRole(role);
    }

    if (minimumRole) {
        hasAccess = hasAccess && hasMinimumRole(minimumRole);
    }

    if (!hasAccess) {
        if (fallback) {
            return <>{fallback}</>;
        }
        return null;
    }

    return <>{children}</>;
}

// ==================== Access Denied Component ====================

export function AccessDenied(): React.JSX.Element {
    const router = useRouter();

    return (
        <div className="flex flex-col items-center justify-center min-h-screen px-4">
            <div className="text-center">
                <h1 className="text-6xl font-bold text-gray-200">403</h1>
                <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mt-4">Access Denied</h2>
                <p className="text-gray-500 mt-2">
                    You don&apos;t have permission to access this page.
                </p>
                <div className="mt-6 space-x-4">
                    <button
                        onClick={() => router.back()}
                        className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                        Go Back
                    </button>
                    <button
                        onClick={() => router.push('/dashboard')}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-lg hover:bg-blue-600"
                    >
                        Go to Dashboard
                    </button>
                </div>
            </div>
        </div>
    );
}

// ==================== Utility Functions ====================

export function getPermissionsForRole(role: Role): Permission[] {
    return rolePermissions[role] || [];
}

export function getRoleName(role: Role): string {
    const names: Record<Role, string> = {
        admin: 'Administrator',
        manager: 'Manager',
        sales_rep: 'Sales Representative',
        viewer: 'Viewer',
        guest: 'Guest',
    };
    return names[role] || role;
}

export function getRoleColor(role: Role): string {
    const colors: Record<Role, string> = {
        admin: 'bg-purple-100 text-purple-700',
        manager: 'bg-blue-100 text-blue-700',
        sales_rep: 'bg-green-100 text-green-700',
        viewer: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
        guest: 'bg-yellow-100 text-yellow-700',
    };
    return colors[role] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
}

