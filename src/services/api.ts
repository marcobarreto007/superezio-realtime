import type { ToolCall } from './agentService';

/**
 * Cliente API SuperEzio
 * Streaming + RAG integrado + Tool Calling
 */

import type { ChatRequest, ChatResponse, Message } from '../types/chat'

// Usar env var em produção, fallback pra proxy local em dev
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/hf`
  : '/api/hf' // Dev local: Proxy via Express (porta 8080) -> Python (porta 8000)

class APIClient {
  constructor() {
    console.log('🚀 [APIClient] Inicializado')
    console.log(`📍 [APIClient] Base URL: ${API_BASE}`)
  }

  async chat(messages: Message[], stream: boolean = false): Promise<ChatResponse> {
    console.log('📤 [APIClient] Enviando chat request (não-streaming)')
    console.log(`📊 [APIClient] ${messages.length} mensagens`)
    
    const request: ChatRequest = {
      messages: messages.map(m => ({
        role: m.role,
        content: m.content
      })),
      temperature: 0.2, // Reduced temp for better tool use
      max_tokens: 512,
      stream: false
    }

    console.log('🔗 [APIClient] POST', `${API_BASE}/chat`)
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    console.log(`📥 [APIClient] Response status: ${response.status}`)
    
    if (!response.ok) {
      console.error('❌ [APIClient] Erro na API:', response.statusText)
      throw new Error(`API error: ${response.statusText}`)
    }

    const data = await response.json()
    console.log('✅ [APIClient] Resposta recebida', data)
    return data as ChatResponse
  }

  async *chatStream(messages: Message[]): AsyncGenerator<string | { tool_calls: ToolCall[] }> {
    console.log('📤 [APIClient] Iniciando streaming')
    console.log(`📊 [APIClient] ${messages.length} mensagens no histórico`)
    
    const request: ChatRequest = {
      messages: messages.map(m => ({
        role: m.role,
        content: m.content
      })),
      temperature: 0.2,
      max_tokens: 512,
      stream: true
    }

    console.log('🔗 [APIClient] POST', `${API_BASE}/chat/stream`)
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    console.log(`📥 [APIClient] Stream status: ${response.status}`)
    
    if (!response.ok) {
      console.error('❌ [APIClient] Erro no streaming:', response.statusText)
      throw new Error(`API error: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      console.error('❌ [APIClient] Reader não disponível')
      throw new Error('No reader available')
    }
    
    console.log('🌊 [APIClient] Stream reader iniciado')

    const decoder = new TextDecoder()
    let chunkCount = 0
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log(`✅ [APIClient] Stream finalizado (${chunkCount} chunks)`)
        break
      }

      chunkCount++
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6)
          try {
            const parsed = JSON.parse(data)

            // Handle normal content
            if (parsed.content) {
              yield parsed.content
            }

            // Handle tool calls (if they come in stream - depends on backend implementation)
            // Note: Current Python backend sends tool calls in non-streaming mode usually,
            // but if it sends in stream, we catch it here.
            if (parsed.tool_calls) {
                yield { tool_calls: parsed.tool_calls }
            }

            if (parsed.done) {
              console.log('🏁 [APIClient] Stream done signal recebido')
              return
            }
          } catch (e) {
            // Ignorar linhas mal formatadas
          }
        }
      }
    }
  }

  async ragSearch(query: string): Promise<string[]> {
    // Integração futura com serviço RAG
    // Por enquanto retorna vazio
    return []
  }
}

export const apiClient = new APIClient()
