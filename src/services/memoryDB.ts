// Memória infinita no SSD usando IndexedDB
// Armazena embeddings e conversas para RAG

interface MemoryEntry {
  id: string;
  embedding: number[];
  text: string;
  role: 'user' | 'assistant';
  timestamp: string;
  conversationId?: string;
  metadata?: Record<string, any>;
}

class MemoryDB {
  private dbName = 'SuperEzioMemory';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Store para embeddings e memórias
        if (!db.objectStoreNames.contains('memories')) {
          const store = db.createObjectStore('memories', { keyPath: 'id' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('conversationId', 'conversationId', { unique: false });
        }

        // Store para conversas completas
        if (!db.objectStoreNames.contains('conversations')) {
          const store = db.createObjectStore('conversations', { keyPath: 'id' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  async saveMemory(entry: MemoryEntry): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['memories'], 'readwrite');
      const store = transaction.objectStore('memories');
      const request = store.put(entry);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async searchSimilar(embedding: number[], limit: number = 5): Promise<MemoryEntry[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['memories'], 'readonly');
      const store = transaction.objectStore('memories');
      const request = store.getAll();

      request.onsuccess = () => {
        const allMemories = request.result as MemoryEntry[];
        
        // Calcular similaridade com todos
        const similarities = allMemories.map(memory => ({
          memory,
          similarity: this.cosineSimilarity(embedding, memory.embedding),
        }));

        // Ordenar por similaridade e pegar top N
        const top = similarities
          .sort((a, b) => b.similarity - a.similarity)
          .slice(0, limit)
          .filter(item => item.similarity > 0.5) // Threshold mínimo
          .map(item => item.memory);

        resolve(top);
      };

      request.onerror = () => reject(request.error);
    });
  }

  async saveConversation(conversationId: string, messages: any[]): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['conversations'], 'readwrite');
      const store = transaction.objectStore('conversations');
      const request = store.put({
        id: conversationId,
        messages,
        timestamp: new Date().toISOString(),
      });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async loadConversation(conversationId: string): Promise<any[] | null> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['conversations'], 'readonly');
      const store = transaction.objectStore('conversations');
      const request = store.get(conversationId);

      request.onsuccess = () => {
        const result = request.result;
        resolve(result ? result.messages : null);
      };

      request.onerror = () => reject(request.error);
    });
  }

  async getAllConversations(): Promise<Array<{ id: string; timestamp: string; messageCount: number }>> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['conversations'], 'readonly');
      const store = transaction.objectStore('conversations');
      const request = store.getAll();

      request.onsuccess = () => {
        const conversations = request.result.map((conv: any) => ({
          id: conv.id,
          timestamp: conv.timestamp,
          messageCount: conv.messages?.length || 0,
        }));
        resolve(conversations);
      };

      request.onerror = () => reject(request.error);
    });
  }

  async clearAll(): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['memories', 'conversations'], 'readwrite');
      transaction.objectStore('memories').clear();
      transaction.objectStore('conversations').clear();
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0;
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

export const memoryDB = new MemoryDB();

