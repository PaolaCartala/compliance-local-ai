import React, { createContext, useContext, useState, useEffect } from 'react';

export interface User {
  id: string;
  email: string;
  name: string;
  department: string;
  role: 'CCO' | 'Analyst' | 'Administrator' | 'Financial Planner';
  employeeId: string;
  lastLogin: string;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock users for demonstration
const mockUsers: Record<string, User> = {
  'sarah.johnson@wealthfirm.com': {
    id: '1',
    email: 'sarah.johnson@wealthfirm.com',
    name: 'Sarah Johnson',
    department: 'Wealth Management',
    role: 'Financial Planner',
    employeeId: 'WF001',
    lastLogin: new Date().toISOString(),
  },
  'jennifer.walsh@wealthfirm.com': {
    id: '2',
    email: 'jennifer.walsh@wealthfirm.com',
    name: 'Jennifer Walsh',
    department: 'Compliance',
    role: 'CCO',
    employeeId: 'WF002',
    lastLogin: new Date().toISOString(),
  },
  'michael.chen@wealthfirm.com': {
    id: '3',
    email: 'michael.chen@wealthfirm.com',
    name: 'Michael Chen',
    department: 'Technology',
    role: 'Administrator',
    employeeId: 'WF003',
    lastLogin: new Date().toISOString(),
  },
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = () => {
    const storedUser = localStorage.getItem('mock_auth_user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
      } catch (error) {
        localStorage.removeItem('mock_auth_user');
      }
    }
    setIsLoading(false);
  };

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const mockUser = mockUsers[email.toLowerCase()];
    
    if (!mockUser || password !== 'demo123') {
      setIsLoading(false);
      throw new Error('Invalid email or password');
    }
    
    const updatedUser = {
      ...mockUser,
      lastLogin: new Date().toISOString(),
    };
    
    setUser(updatedUser);
    localStorage.setItem('mock_auth_user', JSON.stringify(updatedUser));
    setIsLoading(false);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('mock_auth_user');
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};