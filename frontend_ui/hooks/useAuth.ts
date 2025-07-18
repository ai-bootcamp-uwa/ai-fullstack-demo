import { useState, useEffect } from 'react';
import { api, setAuthToken, clearAuthToken, getAuthToken } from '@/lib/api';
import { LoginCredentials, AuthResponse } from '@/lib/types';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<{ username: string; is_admin: boolean } | null>(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      // Verify token is still valid
      api.auth.verify()
        .then(() => {
          setIsAuthenticated(true);
        })
        .catch(() => {
          // Token is invalid, clear it
          clearAuthToken();
          setIsAuthenticated(false);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true);
      const response = await api.auth.login(credentials);
      const authData: AuthResponse = response.data;
      
      // Store token
      setAuthToken(authData.access_token);
      
      // Update state
      setIsAuthenticated(true);
      setUser(authData.user);
      
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: 'Invalid username or password' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthToken();
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  // Auto-login with default credentials for demo
  const autoLogin = async () => {
    return await login({ username: 'admin', password: 'admin123' });
  };

  return {
    isAuthenticated,
    isLoading,
    user,
    login,
    logout,
    autoLogin,
  };
}; 