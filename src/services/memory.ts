/**
 * Memória Eterna - IndexedDB
 * Histórico persistente de todas as conversas
 */

import type { Conversation, Message } from '../types/chat'

const DB_NAME = 'superezio_memory'
const DB_VERSION = 1
const STORE_NAME = 'conversations'

class MemoryService {
  private db: IDBDatabase | null = null

  async init(): Promise<void> {
    console.log('💾 [Memory] Inicializando IndexedDB...')
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('❌ [Memory] Erro ao abrir DB:', request.error)
        reject(request.error)
      }
      
      request.onsuccess = () => {
        this.db = request.result
        console.log('✅ [Memory] IndexedDB pronto')
        resolve()
      }

      request.onupgradeneeded = (event) => {
        console.log('🔄 [Memory] Upgrade do banco de dados')
        const db = (event.target as IDBOpenDBRequest).result

        if (!db.objectStoreNames.contains(STORE_NAME)) {
          console.log(`📦 [Memory] Criando object store: ${STORE_NAME}`)
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' })
          store.createIndex('updatedAt', 'updatedAt', { unique: false })
          store.createIndex('createdAt', 'createdAt', { unique: false })
          console.log('✅ [Memory] Índices criados')
        }
      }
    })
  }

  async saveConversation(conversation: Conversation): Promise<void> {
    if (!this.db) await this.init()

    console.log(`💾 [Memory] Salvando conversa: ${conversation.id}`)
    console.log(`📝 [Memory] ${conversation.messages.length} mensagens`)

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.put(conversation)

      request.onerror = () => {
        console.error('❌ [Memory] Erro ao salvar:', request.error)
        reject(request.error)
      }
      
      request.onsuccess = () => {
        console.log('✅ [Memory] Conversa salva com sucesso')
        resolve()
      }
    })
  }

  async getConversation(id: string): Promise<Conversation | null> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readonly')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.get(id)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result || null)
    })
  }

  async getAllConversations(): Promise<Conversation[]> {
    if (!this.db) await this.init()

    console.log('📚 [Memory] Carregando todas as conversas')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readonly')
      const store = transaction.objectStore(STORE_NAME)
      const index = store.index('updatedAt')
      const request = index.openCursor(null, 'prev') // Mais recentes primeiro

      const conversations: Conversation[] = []

      request.onerror = () => {
        console.error('❌ [Memory] Erro ao carregar:', request.error)
        reject(request.error)
      }
      
      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result
        if (cursor) {
          conversations.push(cursor.value)
          cursor.continue()
        } else {
          console.log(`✅ [Memory] ${conversations.length} conversas carregadas`)
          resolve(conversations)
        }
      }
    })
  }

  async deleteConversation(id: string): Promise<void> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.delete(id)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve()
    })
  }

  async searchMessages(query: string): Promise<Message[]> {
    const conversations = await this.getAllConversations()
    const results: Message[] = []

    for (const conv of conversations) {
      for (const msg of conv.messages) {
        if (msg.content.toLowerCase().includes(query.toLowerCase())) {
          results.push(msg)
        }
      }
    }

    return results
  }

  async clearAll(): Promise<void> {
    if (!this.db) await this.init()

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.clear()

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve()
    })
  }
}

export const memoryService = new MemoryService()
