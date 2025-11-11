import { useState, useRef, useEffect, useCallback } from 'react';
import { ChatMessage } from '../types';
import { startChat } from '../services/provider';
// Chat-like interface returned by provider selector
type ChatLike = { sendMessageStream: (args: { message: string }) => AsyncGenerator<{ text: string }, void, unknown> } | null;
import { retrieve, ensureIndex } from '../services/ragClient';

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatRef = useRef<ChatLike>(null);

  const initializeChat = useCallback(async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Build RAG index in background
        await ensureIndex();
        if (!chatRef.current) {
          chatRef.current = startChat();
          // Send an empty message to get the initial greeting from the bot
          const responseStream = await chatRef.current.sendMessageStream({ message: "" });
          
          let botMessage: ChatMessage = { role: 'model', content: '' };
          setMessages([botMessage]);

          for await (const chunk of responseStream) {
            botMessage.content += chunk.text;
            setMessages([ { ...botMessage } ]);
          }
        }
      } catch (e) {
        console.error("Failed to initialize chat:", e);
        setError("Não foi possível iniciar o chat. Verifique sua chave de API e a conexão.");
      } finally {
        setIsLoading(false);
      }
  }, []);

  useEffect(() => {
    initializeChat();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = async (prompt: string) => {
    if (!prompt.trim() || !chatRef.current) return;

    setIsLoading(true);
    setError(null);

    const userMessage: ChatMessage = { role: 'user', content: prompt };
    
    // Create a placeholder for the bot's response
    const botMessagePlaceholder: ChatMessage = { role: 'model', content: '' };
    setMessages(prev => [...prev, userMessage, botMessagePlaceholder]);
    
    try {
      // Retrieve top context and prepend to the prompt
      const chunks = await retrieve(prompt, 4);
      const context = chunks.map((c, i) => `Fonte ${i+1} (${c.url}):\n${c.content}`).join('\n\n');
      const ragPrompt = context
        ? `Você tem o seguinte contexto de apoio (use apenas se relevante e cite como "Fonte X"):\n\n${context}\n\n---\nPergunta do usuário: ${prompt}`
        : prompt;

      const stream = await chatRef.current.sendMessageStream({ message: ragPrompt });
      let currentBotContent = '';

      for await (const chunk of stream) {
        currentBotContent += chunk.text;
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = { role: 'model', content: currentBotContent };
          return newMessages;
        });
      }

    } catch (e) {
      console.error("Failed to send message:", e);
      const errorMessage = "Desculpe, Pão-duro! Ocorreu um erro ao processar sua solicitação.";
      setError(errorMessage);
       setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = { role: 'model', content: errorMessage };
          return newMessages;
        });
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, error, sendMessage };
};
