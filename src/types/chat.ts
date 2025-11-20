/**
 * Tipos do SuperEzio Chat
 * Memória eterna + RAG + Streaming
 */

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  image?: string // URL da imagem para mensagens do usuário
  ragContext?: string[] // Documentos usados via RAG
  expert?: string
  loraAdapter?: string
  mode?: string
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

export interface ChatRequestMessage {
  role: string
  content: string
  ragContext?: string[]
}

export interface ChatRequest {
  messages: ChatRequestMessage[]
  temperature?: number
  max_tokens?: number
  stream?: boolean
}

export interface ChatResponse {
  content: string
  error?: string
  expert?: string
  lora_adapter?: string
  mode?: string
  tool_calls?: Array<{
    name: string
    parameters: Record<string, any>
  }>
  tool_results?: Array<{
    tool: string
    result: any
  }>
}
