import { useState, useEffect } from 'react';
import { Message } from '@/types';
import { sendMessageToOllama } from '@/services/ollamaClient';
import { memoryDB } from '@/services/memoryDB';
import { getOllamaModel } from '@/config/env';

const CONVERSATION_ID_KEY = 'superezio_conversation_id';
const CURRENT_MODEL_KEY = 'superezio_current_model';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    return localStorage.getItem(CURRENT_MODEL_KEY) || getOllamaModel();
  });
  const [conversationId] = useState<string>(() => {
    let id = localStorage.getItem(CONVERSATION_ID_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(CONVERSATION_ID_KEY, id);
    }
    return id;
  });

  // Carregar conversa ao iniciar
  useEffect(() => {
    const loadConversation = async () => {
      try {
        await memoryDB.init();
        const savedMessages = await memoryDB.loadConversation(conversationId);
        if (savedMessages && savedMessages.length > 0) {
          setMessages(savedMessages);
        }
      } catch (error) {
        console.error('Error loading conversation:', error);
      }
    };
    loadConversation();
  }, [conversationId]);

  // Salvar conversa quando mudar
  useEffect(() => {
    if (messages.length > 0) {
      memoryDB.saveConversation(conversationId, messages).catch(console.error);
    }
  }, [messages, conversationId]);

  const sendMessage = async (text: string, model?: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      author: 'Marco',
      content: text,
      timestamp: new Date().toISOString(),
    };

    // Pass the state updater function to ensure we're using the latest state
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      const modelToUse = model || selectedModel;
      const botResponseContent = await sendMessageToOllama([...messages, userMessage], modelToUse);

      const botMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        author: 'SuperEzio',
        content: botResponseContent,
        timestamp: new Date().toISOString(),
      };

      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Failed to get response from bot:", error);
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        author: 'SuperEzio',
        content: "Desculpe, não consegui processar sua mensagem. Tente novamente.",
        timestamp: new Date().toISOString(),
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const changeModel = (model: string) => {
    setSelectedModel(model);
    localStorage.setItem(CURRENT_MODEL_KEY, model);
  };

  const clearConversation = () => {
    setMessages([]);
    memoryDB.saveConversation(conversationId, []).catch(console.error);
  };

  return {
    messages,
    isLoading,
    sendMessage,
    selectedModel,
    changeModel,
    clearConversation,
  };
};