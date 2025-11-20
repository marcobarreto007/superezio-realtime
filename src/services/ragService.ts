import type { Message, MemoryEntry } from '../types';

class RAGService {
  private memory: MemoryEntry[] = [];
  private readonly MAX_MEMORY = 50;

  constructor() {
    console.log('🧠 [RAG] Serviço inicializado')
    console.log(`📊 [RAG] Capacidade máxima: ${this.MAX_MEMORY} entradas`)
  }

  addToMemory(content: string): void {
    this.memory.push({ content, timestamp: Date.now() });
    console.log(`➕ [RAG] Adicionado à memória (${this.memory.length}/${this.MAX_MEMORY})`)
    
    if (this.memory.length > this.MAX_MEMORY) {
      this.memory = this.memory.slice(-this.MAX_MEMORY);
      console.log(`🗑️  [RAG] Memória trimada para ${this.MAX_MEMORY} entradas`)
    }
  }

  searchMemory(query: string, limit: number = 5): MemoryEntry[] {
    console.log(`🔍 [RAG] Buscando: "${query.substring(0, 50)}..."`)
    
    const queryLower = query.toLowerCase();
    const results = this.memory
      .map(entry => {
        const words = queryLower.split(' ').filter(w => w.length > 3);
        const matches = words.filter(w => entry.content.toLowerCase().includes(w)).length;
        const relevance = matches / words.length;
        return { ...entry, relevance };
      })
      .filter(e => (e.relevance || 0) > 0.3)
      .sort((a, b) => (b.relevance || 0) - (a.relevance || 0))
      .slice(0, limit);
    
    console.log(`✅ [RAG] ${results.length} resultados encontrados`)
    return results;
  }

  enhancePrompt(userMessage: string): string {
    const memories = this.searchMemory(userMessage, 3);
    if (memories.length === 0) return userMessage;
    const context = memories.map(m => m.content).join('\n\n');
    return `[CONTEXTO]:\n${context}\n\n[PERGUNTA]:\n${userMessage}`;
  }

  clearMemory(): void {
    this.memory = [];
  }
}

export const ragService = new RAGService();
