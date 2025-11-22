'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone?: string;
  avatar?: string;
  department?: string;
  is_active: boolean;
  two_factor_enabled: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: { username: string; password: string }) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // TEMPORARY: Authentication disabled - always authenticated with mock user
  const [user] = useState<User | null>({
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    first_name: 'Admin',
    last_name: 'User',
    role: 'admin',
    is_active: true,
    two_factor_enabled: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  });
  const [isLoading] = useState(false);

  const isAuthenticated = true; // TEMPORARY: Always authenticated

  const login = async (credentials: { username: string; password: string }) => {
    // TEMPORARY: Skip actual authentication - auto-login
    console.log('TEMP: Authentication bypassed for:', credentials.username);
    return Promise.resolve();
  };

  const logout = () => {
    console.log('TEMP: Logout bypassed - authentication disabled');
    // authAPI.logout();
    // setUser(null);
  };

  const refreshUser = useCallback(async () => {
    // TEMPORARY: Skip user refresh
    console.log('TEMP: User refresh bypassed - authentication disabled');
    return Promise.resolve();
  }, []);

  // TEMPORARY: Skip auth initialization
  // useEffect removed

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
