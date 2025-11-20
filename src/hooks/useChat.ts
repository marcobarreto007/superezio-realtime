/**
 * Hook useChat - Gerencia conversas, memória eterna e streaming
 * Integrado com RAG para contexto
 */

import { useState, useEffect, useCallback } from 'react'
import type { Conversation, Message, ChatState } from '../types/chat'
import { memoryService } from '../services/memory'
import { apiClient } from '../services/api'
import { ragService } from '../services/ragService'

export function useChat() {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    currentConversationId: null,
    isLoading: false,
    isStreaming: false
  })

  console.log('🎣 [useChat] Hook inicializado')

  // Inicializar memória e carregar conversas
  useEffect(() => {
    console.log('🔄 [useChat] Efeito de inicialização executado')
    
    const init = async () => {
      console.log('⚡ [useChat] Iniciando sistema...')
      await memoryService.init()
      const conversations = await memoryService.getAllConversations()

      // Se não tem conversas, criar uma inicial
      if (conversations.length === 0) {
        console.log('📝 [useChat] Nenhuma conversa encontrada, criando inicial')
        const initialConv: Conversation = {
          id: `conv_${Date.now()}`,
          title: 'Conversa Inicial',
          messages: [{
            id: `msg_${Date.now()}`,
            role: 'assistant',
            content: 'E aí! 👋 Quem é você? Fala aí pra eu saber com quem tô conversando!',
            timestamp: Date.now()
          }],
          createdAt: Date.now(),
          updatedAt: Date.now()
        }

        await memoryService.saveConversation(initialConv)
        conversations.push(initialConv)
        console.log('✅ [useChat] Conversa inicial criada')
      }

      console.log(`📚 [useChat] ${conversations.length} conversas carregadas`)
      setState(prev => ({
        ...prev,
        conversations,
        currentConversationId: conversations[0]?.id || null
      }))
      console.log('✅ [useChat] Sistema pronto!')
    }
    init()
  }, [])

  const currentConversation = state.conversations.find(
    c => c.id === state.currentConversationId
  )

  // Nova conversa
  const newConversation = useCallback(() => {
    const conversation: Conversation = {
      id: `conv_${Date.now()}`,
      title: 'Nova Conversa',
      messages: [{
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: 'E aí! Quem é você?',
        timestamp: Date.now()
      }],
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    setState(prev => ({
      ...prev,
      conversations: [conversation, ...prev.conversations],
      currentConversationId: conversation.id
    }))

    memoryService.saveConversation(conversation)
  }, [])

  // Selecionar conversa
  const selectConversation = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      currentConversationId: id
    }))
  }, [])

  // Deletar conversa
  const deleteConversation = useCallback(async (id: string) => {
    await memoryService.deleteConversation(id)
    setState(prev => {
      const filtered = prev.conversations.filter(c => c.id !== id)
      return {
        ...prev,
        conversations: filtered,
        currentConversationId: prev.currentConversationId === id
          ? filtered[0]?.id || null
          : prev.currentConversationId
      }
    })
  }, [])

  // Enviar mensagem com streaming
  const sendMessage = useCallback(async (content: string, image?: File) => {
    let convId = state.currentConversationId;
    if (!convId) {
      newConversation();
      await new Promise(resolve => setTimeout(resolve, 10));
      convId = state.currentConversationId!;
    }
  
    // Adicionar ao RAG
    ragService.addToMemory(content);
    const ragContext = ragService
      .searchMemory(content, 5)
      .map(m => m.content)
      .filter(ctx => ctx.trim().toLowerCase() !== content.trim().toLowerCase());
  
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: image ? `[Image Attached] ${content}` : content,
      timestamp: Date.now(),
      ragContext,
      image: image ? URL.createObjectURL(image) : undefined,
    };
  
    // Adicionar mensagem do usuário
    setState(prev => ({
      ...prev,
      conversations: prev.conversations.map(c =>
        c.id === convId
          ? { ...c, messages: [...c.messages, userMessage], updatedAt: Date.now() }
          : c
      ),
      isStreaming: true,
    }));
  
    try {
      const conversation = state.conversations.find(c => c.id === convId)!;
      const messages = [...conversation.messages, userMessage];
  
      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        ragContext,
      };
  
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(c =>
          c.id === convId
            ? { ...c, messages: [...c.messages, assistantMessage] }
            : c
        ),
      }));
  
      let fullContent = '';
      let expert: string | undefined;
      let loraAdapter: string | undefined;
      let mode: string | undefined;
  
      const stream = image 
        ? apiClient.chatStreamWithImage(messages, image)
        : apiClient.chatStream(messages);

      for await (const chunk of stream) {
        if (typeof chunk === 'string') {
          fullContent += chunk;
        } else if (chunk && typeof chunk === 'object' && 'content' in chunk) {
          fullContent += chunk.content;
          if (chunk.metadata) {
            expert = chunk.metadata.expert;
            loraAdapter = chunk.metadata.lora_adapter;
            mode = chunk.metadata.mode;
          }
        }
  
        setState(prev => ({
          ...prev,
          conversations: prev.conversations.map(c =>
            c.id === convId
              ? {
                  ...c,
                  messages: c.messages.map(m =>
                    m.id === assistantMessage.id
                      ? { 
                          ...m, 
                          content: fullContent,
                          expert,
                          loraAdapter,
                          mode
                        }
                      : m
                  ),
                }
              : c
          ),
        }));
      }
  
      ragService.addToMemory(fullContent);
      setState(prev => ({ ...prev, isStreaming: false }));
  
      const finalConv = state.conversations.find(c => c.id === convId)!;
      const title = finalConv.messages.length === 3
        ? content.substring(0, 50)
        : finalConv.title;
  
      await memoryService.saveConversation({
        ...finalConv,
        title,
        updatedAt: Date.now(),
      });
  
    } catch (error) {
      console.error('Erro no streaming:', error);
      setState(prev => ({ ...prev, isStreaming: false }));
    }
  }, [state.currentConversationId, state.conversations, newConversation]);

  return {
    conversations: state.conversations,
    currentConversation,
    isLoading: state.isLoading,
    isStreaming: state.isStreaming,
    newConversation,
    selectConversation,
    deleteConversation,
    sendMessage
  }
}
