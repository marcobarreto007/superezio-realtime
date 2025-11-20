# RAG Service
@'
import type { Message, MemoryEntry } from '../types';

class RAGService {
  private memory: MemoryEntry[] = [];
  private readonly MAX_MEMORY = 50;

  addToMemory(content: string): void {
    this.memory.push({ content, timestamp: Date.now() });
    if (this.memory.length > this.MAX_MEMORY) {
      this.memory = this.memory.slice(-this.MAX_MEMORY);
    }
  }

  searchMemory(query: string, limit: number = 5): MemoryEntry[] {
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
'@ | Out-File -FilePath "src\services\ragService.ts" -Encoding utf8

# useChat Hook
@'
import { useState, useCallback } from 'react';
import type { Message } from '../types';
import { sendMessage } from '../services/apiClient';
import { ragService } from '../services/ragService';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendChatMessage = useCallback(async (content: string) => {
    const userMsg: Message = { role: 'user', content, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      ragService.addToMemory(content);
      const enhanced = ragService.enhancePrompt(content);
      const response = await sendMessage([...messages, { role: 'user', content: enhanced }]);
      
      const assistantMsg: Message = { role: 'assistant', content: response, timestamp: Date.now() };
      setMessages(prev => [...prev, assistantMsg]);
      ragService.addToMemory(response);
    } catch (error) {
      console.error('Erro:', error);
      const errorMsg: Message = { role: 'assistant', content: 'Erro ao enviar mensagem', timestamp: Date.now() };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    ragService.clearMemory();
  }, []);

  return { messages, isLoading, sendMessage: sendChatMessage, clearChat };
}
'@ | Out-File -FilePath "src\hooks\useChat.ts" -Encoding utf8

# Message Component
@'
import React from 'react';
import type { Message as MessageType } from '../types';

interface Props {
  message: MessageType;
}

export function Message({ message }: Props) {
  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] rounded-lg px-4 py-2 ${
        message.role === 'user' 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-200 text-gray-900'
      }`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
'@ | Out-File -FilePath "src\components\Message.tsx" -Encoding utf8

# Chat Component
@'
import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { Message } from './Message';

export function Chat() {
  const { messages, isLoading, sendMessage, clearChat } = useChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">SuperEzio</h1>
          <button onClick={clearChat} className="px-3 py-1 bg-blue-700 rounded hover:bg-blue-800">
            Limpar
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <Message key={idx} message={msg} />
        ))}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-200 rounded-lg px-4 py-2">
              <span className="animate-pulse">Pensando...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 bg-white border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}
'@ | Out-File -FilePath "src\components\Chat.tsx" -Encoding utf8

# App Component
@'
import React from 'react';
import { Chat } from './components/Chat';

function App() {
  return <Chat />;
}

export default App;
'@ | Out-File -FilePath "src\App.tsx" -Encoding utf8

# Main Entry Point
@'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'@ | Out-File -FilePath "src\main.tsx" -Encoding utf8

# CSS with Tailwind
@'
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
'@ | Out-File -FilePath "src\index.css" -Encoding utf8

Write-Host "✅ Todos arquivos criados com sucesso!" -ForegroundColor Green
