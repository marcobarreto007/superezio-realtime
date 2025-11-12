export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: number;
}

export interface ChatResponse {
  content: string;
  tool_calls?: any;
}

export interface MemoryEntry {
  content: string;
  timestamp: number;
  relevance?: number;
}
