// Serviço RAG - Recuperação Aumentada por Geração
// Combina embeddings com busca semântica para memória de longo prazo

import { generateEmbedding, cosineSimilarity } from './embeddings';
import { memoryDB } from './memoryDB';
import { Message } from '@/types';

export class RAGService {
  async addToMemory(message: Message): Promise<void> {
    try {
      const embedding = await generateEmbedding(message.content);
      
      await memoryDB.saveMemory({
        id: message.id,
        embedding,
        text: message.content,
        role: message.role,
        timestamp: message.timestamp,
        metadata: {
          author: message.author,
        },
      });
    } catch (error) {
      console.error('Error adding to memory:', error);
    }
  }

  async searchRelevantContext(query: string, limit: number = 3): Promise<string[]> {
    try {
      const queryEmbedding = await generateEmbedding(query);
      const relevantMemories = await memoryDB.searchSimilar(queryEmbedding, limit);
      
      return relevantMemories.map(m => m.text);
    } catch (error) {
      console.error('Error searching context:', error);
      return [];
    }
  }

  async enhancePrompt(userMessage: string, conversationHistory: Message[]): Promise<string> {
    // Buscar contexto relevante da memória
    const relevantContext = await this.searchRelevantContext(userMessage);
    
    if (relevantContext.length === 0) {
      return userMessage; // Sem contexto adicional
    }

    // Construir prompt aumentado
    const contextText = relevantContext
      .map((text, i) => `[Contexto ${i + 1}]: ${text}`)
      .join('\n\n');

    return `Contexto relevante de conversas anteriores:\n${contextText}\n\nPergunta atual: ${userMessage}`;
  }
}

export const ragService = new RAGService();

