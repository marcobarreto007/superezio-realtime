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

  async enhancePrompt(userMessage: string, conversationHistory: Message[], webSearchResults?: string): Promise<string> {
    // Buscar contexto relevante da memória
    const relevantContext = await this.searchRelevantContext(userMessage);
    
    let enhancedMessage = userMessage;
    
    // Adicionar contexto da memória
    if (relevantContext.length > 0) {
      const contextText = relevantContext
        .map((text, i) => `[Contexto Memória ${i + 1}]: ${text}`)
        .join('\n\n');
      enhancedMessage = `Contexto relevante de conversas anteriores:\n${contextText}\n\nPergunta atual: ${enhancedMessage}`;
    }
    
    // Adicionar resultados de busca web se disponíveis
    if (webSearchResults) {
      enhancedMessage += `\n\n${webSearchResults}`;
    }
    
    return enhancedMessage;
  }
  
  // Salvar resultados de busca web na memória
  async addWebSearchToMemory(query: string, results: string): Promise<void> {
    try {
      const searchMemory: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        author: 'SuperEzio',
        content: `[Busca Web] Query: ${query}\n\nResultados:\n${results}`,
        timestamp: new Date().toISOString(),
      };
      await this.addToMemory(searchMemory);
    } catch (error) {
      console.error('Error saving web search to memory:', error);
    }
  }
}

export const ragService = new RAGService();

