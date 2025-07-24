// Authentication types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    username: string;
    is_admin: boolean;
  };
}

// Geological data types
export interface GeologicalSite {
  id: string;
  ANUMBER: string;
  PNAME: string;
  PTYPE: string;
  PSTATUS: string;
  PMETHOD: string;
  PSIZE: string;
  PDATE: string;
  POPERATOR: string;
  POWNER: string;
  PCOMMODITY: string;
  PDEPTYPE: string;
  PGRADE: string;
  POREMIN: string;
  PGANGMIN: string;
  PALTMIN: string;
  PHOST: string;
  PSTRUCTURE: string;
  PGEOLOGY: string;
  PCOMMENTS: string;
  EASTING: number;
  NORTHING: number;
  LATITUDE: number;
  LONGITUDE: number;
  ELEVATION: number;
  DATUM: string;
  ZONE: string;
  REFERENCES: string;
  UPDATED: string;
}

export interface GeologicalSiteGeometry {
  type: string;
  coordinates: [number, number];
  properties: {
    ANUMBER: string;
    PNAME: string;
    PTYPE: string;
    LATITUDE: number;
    LONGITUDE: number;
  };
}

export interface FilterCriteria {
  ptype?: string;
  pstatus?: string;
  pcommodity?: string;
  powner?: string;
  poperator?: string;
  min_elevation?: number;
  max_elevation?: number;
  date_from?: string;
  date_to?: string;
}

// Chat types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  tools_available?: string[];
  context?: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ApiError {
  error: string;
  details?: string;
  code?: string;
}

// Health check types
export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  modules?: {
    data_foundation: boolean;
    cortex_engine: boolean;
    backend_gateway: boolean;
  };
}

// Tool execution types
export interface ToolResult {
  success: boolean;
  data?: unknown;
  error?: string;
}

export interface GeologicalTool {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, unknown>;
    required: string[];
  };
  execute: (params: unknown) => Promise<ToolResult>;
} 