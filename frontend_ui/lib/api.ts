import axios from 'axios';
import { 
  LoginCredentials, 
  AuthResponse, 
  GeologicalSite, 
  GeologicalSiteGeometry, 
  FilterCriteria, 
  ChatResponse, 
  HealthStatus 
} from './types';

// Backend Gateway API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3003';

// Create axios instance with default configuration
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth token on unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Authentication
  auth: {
    login: (credentials: LoginCredentials) =>
      apiClient.post<AuthResponse>('/auth/login', credentials),
    logout: () => apiClient.post('/auth/logout'),
    verify: () => apiClient.get('/auth/verify'),
  },

  // Chat with AI (Module 2 - Cortex Engine via Backend Gateway)
  chat: {
    send: (message: string, conversationId?: string) =>
      apiClient.post<ChatResponse>('/api/backend/chat', {
        message,
        conversation_id: conversationId || 'geological-chat',
      }),
    history: (conversationId?: string) =>
      apiClient.get<ChatResponse[]>(`/api/backend/chat/history/${conversationId || 'geological-chat'}`),
  },

  // Geological data (Module 1 - Data Foundation via Backend Gateway)
  geological: {
    getSites: () => apiClient.get<GeologicalSite[]>('/api/data/reports'),
    getSite: (id: string) => apiClient.get<GeologicalSite>(`/api/data/reports/${id}`),
    getSiteGeometry: (id: string) => apiClient.get<GeologicalSiteGeometry>(`/api/data/reports/${id}/geometry`),
    filterSites: (filters: FilterCriteria) =>
      apiClient.post<GeologicalSite[]>('/api/data/reports/filter', filters),
  },

  // Health checks
  health: {
    check: () => apiClient.get<HealthStatus>('/health'),
    modules: () => apiClient.get<HealthStatus>('/health/modules'),
  },
};

// Helper function to get auth token
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
};

// Helper function to set auth token
export const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
};

// Helper function to clear auth token
export const clearAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
  }
}; 