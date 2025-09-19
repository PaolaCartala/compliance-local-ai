/**
 * API Configuration and Authentication Context
 * 
 * Manages API configuration, authentication state, and token handling
 * for the Baker Compliant AI frontend.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

// API Configuration interface
export interface APIConfig {
  baseURL: string;
  healthURL: string;
  timeout: number;
  retries: number;
}

// Authentication state interface
export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: any | null;
  isLoading: boolean;
}

// API Context interface
export interface APIContextType {
  config: APIConfig;
  auth: AuthState;
  setAuthToken: (token: string | null) => void;
  setUser: (user: any | null) => void;
  logout: () => void;
}

// Default API configuration
const DEFAULT_API_CONFIG: APIConfig = {
  baseURL: 'http://localhost:8000/api/v1',
  healthURL: 'http://localhost:8000/health',
  timeout: 30000,
  retries: 3,
};

// Create the context
const APIContext = createContext<APIContextType | undefined>(undefined);

/**
 * API Context Provider
 * Provides API configuration and authentication state to child components
 */
export function APIProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({
    isAuthenticated: false,
    token: null,
    user: null,
    isLoading: true,
  });

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initializeAuth = () => {
      try {
        let token = localStorage.getItem('auth_token');
        let userStr = localStorage.getItem('auth_user');
        let user = userStr ? JSON.parse(userStr) : null;

        // For development: use Sarah Johnson's token if no token is set
        if (!token) {
          token = 'sarah.johnson';
          user = {
            id: '18bb4a9058d8c05b52445bdfee3b9eaa',  // Real DB ID
            email: 'sarah.johnson@bakergroup.com',  // Matches actual DB
            azure_user_id: 'auth0|sarah.johnson',   // Matches mock auth
            role: 'financial_advisor',
            name: 'Sarah Johnson, CFP'
          };
          // Save to localStorage for persistence
          localStorage.setItem('auth_token', token);
          localStorage.setItem('auth_user', JSON.stringify(user));
          console.log('🔧 Dev Mode - Set default token for Sarah Johnson:', token);
          console.log('🔧 Dev Mode - User config:', user);
        } else {
          console.log('🔐 Auth Context - Using existing token:', token);
        }

        setAuth({
          isAuthenticated: !!token,
          token,
          user,
          isLoading: false,
        });
      } catch (error) {
        console.error('Failed to initialize auth state:', error);
        setAuth({
          isAuthenticated: false,
          token: null,
          user: null,
          isLoading: false,
        });
      }
    };

    initializeAuth();
  }, []);

  // Set authentication token
  const setAuthToken = (token: string | null) => {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }

    setAuth(prev => ({
      ...prev,
      token,
      isAuthenticated: !!token,
    }));
  };

  // Set user data
  const setUser = (user: any | null) => {
    if (user) {
      localStorage.setItem('auth_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('auth_user');
    }

    setAuth(prev => ({
      ...prev,
      user,
    }));
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    
    setAuth({
      isAuthenticated: false,
      token: null,
      user: null,
      isLoading: false,
    });
  };

  const contextValue: APIContextType = {
    config: DEFAULT_API_CONFIG,
    auth,
    setAuthToken,
    setUser,
    logout,
  };

  return (
    <APIContext.Provider value={contextValue}>
      {children}
    </APIContext.Provider>
  );
}

/**
 * Hook to use API context
 */
export function useAPI() {
  const context = useContext(APIContext);
  if (context === undefined) {
    throw new Error('useAPI must be used within an APIProvider');
  }
  return context;
}

/**
 * Hook to get current auth token
 */
export function useAuthToken() {
  const { auth } = useAPI();
  return auth.token;
}

/**
 * Hook to get current user
 */
export function useCurrentUser() {
  const { auth } = useAPI();
  return auth.user;
}

/**
 * Hook to check if user is authenticated
 */
export function useIsAuthenticated() {
  const { auth } = useAPI();
  return auth.isAuthenticated;
}