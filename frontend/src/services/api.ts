/**
 * API Service Layer for Baker Compliant AI Frontend
 * 
 * Handles all communication with the FastAPI backend, including
 * authentication, error handling, and data transformation.
 */

// Types for API responses
export interface APIResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
  offset: number;
}

// API Configuration
const API_CONFIG = {
  baseURL: 'http://localhost:8000/api/v1',
  healthURL: 'http://localhost:8000/health',
  timeout: 30000,
  retries: 3
};

/**
 * Base API client with authentication and error handling
 */
class BaseAPIClient {
  private baseURL: string;
  private healthURL: string;

  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.healthURL = API_CONFIG.healthURL;
  }

  /**
   * Get authentication token from local storage or auth context
   */
  private getAuthToken(): string | null {
    // Get token from localStorage
    // TODO: Replace with auth context when integrated
    return localStorage.getItem('auth_token');
  }

  /**
   * Create headers for API requests
   */
  private createHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log('🔐 API Request - Token being sent:', token);
      } else {
        console.warn('⚠️ API Request - No auth token found in localStorage');
      }
    }

    return headers;
  }

  /**
   * Generic API request handler with error handling
   */
  protected async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.createHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Handle responses with no content (like 204 No Content)
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return {} as T;
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  /**
   * Handle FormData requests (for file uploads)
   */
  protected async makeFormRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getAuthToken();
    
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    // Note: Don't set Content-Type for FormData, let browser set it

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Form request failed: ${endpoint}`, error);
      throw error;
    }
  }

  /**
   * Health check endpoint (uses different base URL)
   */
  async healthCheck(): Promise<any> {
    try {
      const response = await fetch(this.healthURL, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

/**
 * Chat API Service
 * Handles chat messages, threads, and related operations
 */
export class ChatAPIService extends BaseAPIClient {
  
  /**
   * Send a new message in a thread
   */
  async sendMessage(
    content: string,
    threadId: string,
    customGptId?: string,
    files?: File[]
  ): Promise<APIResponse<any>> {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('thread_id', threadId);
    
    if (customGptId) {
      formData.append('custom_gpt_id', customGptId);
    }

    if (files && files.length > 0) {
      files.forEach((file) => {
        formData.append('files', file);
      });
    }

    return this.makeFormRequest<APIResponse<any>>('/chat/messages', formData);
  }

  /**
   * Get messages for a specific thread
   */
  async getThreadMessages(
    threadId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<PaginatedResponse<any>> {
    return this.makeRequest<PaginatedResponse<any>>(
      `/chat/messages/${threadId}?limit=${limit}&offset=${offset}`
    );
  }

  /**
   * Get user's threads
   */
  async getUserThreads(
    limit: number = 20,
    offset: number = 0
  ): Promise<PaginatedResponse<any>> {
    return this.makeRequest<PaginatedResponse<any>>(
      `/threads?limit=${limit}&offset=${offset}`
    );
  }

  /**
   * Create a new thread
   */
  async createThread(
    title: string,
    customGptId: string
  ): Promise<APIResponse<any>> {
    return this.makeRequest<APIResponse<any>>('/threads', {
      method: 'POST',
      body: JSON.stringify({
        title,
        custom_gpt_id: customGptId,
      }),
    });
  }

  /**
   * Update thread (rename, archive, etc.)
   */
  async updateThread(
    threadId: string,
    updates: { title?: string; is_archived?: boolean }
  ): Promise<APIResponse<any>> {
    return this.makeRequest<APIResponse<any>>(`/threads/${threadId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete/archive a thread
   */
  async deleteThread(threadId: string): Promise<APIResponse<any>> {
    return this.makeRequest<APIResponse<any>>(`/threads/${threadId}`, {
      method: 'DELETE',
    });
  }
}

/**
 * Custom GPT API Service
 * Handles Custom GPT management operations
 */
export class CustomGPTAPIService extends BaseAPIClient {
  
  /**
   * Get user's Custom GPTs
   */
  async getCustomGPTs(
    limit: number = 20,
    offset: number = 0
  ): Promise<PaginatedResponse<any>> {
    return this.makeRequest<PaginatedResponse<any>>(
      `/custom-gpts?limit=${limit}&offset=${offset}`
    );
  }

  /**
   * Create a new Custom GPT
   */
  async createCustomGPT(customGPTData: {
    name: string;
    description: string;
    system_prompt: string;
    specialization: string;
    color?: string;
    icon?: string;
    mcp_tools_enabled?: {
      redtail_crm: boolean;
      albridge_portfolio: boolean;
      black_diamond: boolean;
    };
  }): Promise<APIResponse<any>> {
    return this.makeRequest<APIResponse<any>>('/custom-gpts', {
      method: 'POST',
      body: JSON.stringify(customGPTData),
    });
  }

  /**
   * Update a Custom GPT
   */
  async updateCustomGPT(
    customGptId: string,
    updates: Partial<{
      name: string;
      description: string;
      system_prompt: string;
      specialization: string;
      color: string;
      icon: string;
      mcp_tools_enabled: {
        redtail_crm: boolean;
        albridge_portfolio: boolean;
        black_diamond: boolean;
      };
      is_active: boolean;
    }>
  ): Promise<APIResponse<any>> {
    return this.makeRequest<APIResponse<any>>(`/custom-gpts/${customGptId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a Custom GPT
   */
  async deleteCustomGPT(customGptId: string): Promise<APIResponse<any>> {
    return this.makeRequest<APIResponse<any>>(`/custom-gpts/${customGptId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instances
export const chatAPI = new ChatAPIService();
export const customGPTAPI = new CustomGPTAPIService();

// Export base client for other services
export { BaseAPIClient };