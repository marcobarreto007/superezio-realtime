import { useState } from 'react';
import { Message } from '@/types';
import { sendMessageToOllama } from '@/services/ollamaClient';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (text: string) => {
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
      // Pass the most up-to-date messages array to the API client
      const botResponseContent = await sendMessageToOllama([...messages, userMessage]);

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

  return {
    messages,
    isLoading,
    sendMessage,
  };
};