/**
 * Tipos do SuperEzio Chat
 * Memória eterna + RAG + Streaming
 */

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  ragContext?: string[] // Documentos usados via RAG
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
}

export interface ChatState {
  conversations: Conversation[]
  currentConversationId: string | null
  isLoading: boolean
  isStreaming: boolean
}

export interface RAGDocument {
  id: string
  content: string
  metadata: {
    source: string
    timestamp: number
    tags?: string[]
  }
}

export interface ChatRequest {
  messages: Array<{
    role: string
    content: string
  }>
  temperature?: number
  max_tokens?: number
  stream?: boolean
}

export interface ChatResponse {
  content: string
  error?: string
}
