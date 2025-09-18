// TypeScript interfaces for the chat system with CustomGPT management

export interface CustomGPT {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  specialization: 'crm' | 'portfolio' | 'compliance' | 'general' | 'retirement' | 'tax';
  color: string;
  icon: string;
  mcpToolsEnabled: {
    redtailCRM: boolean;
    albridgePortfolio: boolean;
    blackDiamond: boolean;
  };
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Thread {
  id: string;
  title: string;
  customGPTId: string;
  createdAt: string;
  updatedAt: string;
  lastMessage?: string;
  messageCount: number;
  isArchived: boolean;
  tags?: string[];
}

export interface Message {
  id: string;
  threadId: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  customGPTId?: string;
  attachments?: FileAttachment[];
  mcpToolInteractions?: MCPToolInteraction[];
  complianceFlags?: string[];
}

export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  uploadedAt: string;
}

export interface MCPToolInteraction {
  toolName: 'redtail-crm' | 'albridge-portfolio' | 'black-diamond';
  action: string;
  data: any;
  timestamp: string;
  success: boolean;
}

export interface SystemPromptTemplate {
  id: string;
  name: string;
  description: string;
  specialization: CustomGPT['specialization'];
  prompt: string;
  mcpToolsRecommended: {
    redtailCRM: boolean;
    albridgePortfolio: boolean;
    blackDiamond: boolean;
  };
}