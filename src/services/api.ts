/**
 * Cliente API SuperEzio
 * Streaming + RAG integrado
 */

import type { ChatRequest, ChatResponse, Message } from '../types/chat'

const API_BASE = '/api' // Proxy via Express (porta 8080)

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
      temperature: 0.7,
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
    console.log('✅ [APIClient] Resposta recebida')
    return data as ChatResponse
  }

  async *chatStream(messages: Message[]): AsyncGenerator<string> {
    console.log('📤 [APIClient] Iniciando streaming')
    console.log(`📊 [APIClient] ${messages.length} mensagens no histórico`)
    
    const request: ChatRequest = {
      messages: messages.map(m => ({
        role: m.role,
        content: m.content
      })),
      temperature: 0.7,
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

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log(`✅ [APIClient] Stream finalizado (${chunkCount} chunks)`)
        break
      }

      chunkCount++
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6)
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              yield parsed.content
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
