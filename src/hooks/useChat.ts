/**
 * Hook useChat - Gerencia conversas, memória eterna, streaming e AGENTE
 * Integrado com RAG para contexto + Agente de Sistema
 */

import { useState, useEffect, useCallback } from 'react'
import type { Conversation, Message, ChatState } from '../types/chat'
import { memoryService } from '../services/memory'
import { apiClient } from '../services/api'
import { ragService } from '../services/ragService'
import { useAgent } from './useAgent'

export function useChat() {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    currentConversationId: null,
    isLoading: false,
    isStreaming: false
  })

  // Integrar Hook do Agente
  const {
    pendingAction,
    processToolCalls,
    confirmAction,
    cancelAction,
    lastResult,
    isExecuting: isAgentExecuting
  } = useAgent();

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
            content: 'E aí! 👋 Sou o SuperEzio. Posso te ajudar com código, e-mails e arquivos. O que manda?',
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
        content: 'E aí! Em que posso ajudar hoje?',
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

  // Enviar mensagem com streaming e suporte a Agente
  const sendMessage = useCallback(async (content: string) => {
    let convId = state.currentConversationId
    if (!convId) {
      newConversation()
      // Aguardar um tick para pegar o ID da nova conversa
      await new Promise(resolve => setTimeout(resolve, 10))
      convId = state.currentConversationId!
    }

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content,
      timestamp: Date.now()
    }

    // Adicionar ao RAG
    ragService.addToMemory(content)
    const ragContext = ragService.searchMemory(content, 5).map(m => m.content)

    // Adicionar mensagem do usuário
    setState(prev => ({
      ...prev,
      conversations: prev.conversations.map(c =>
        c.id === convId
          ? { ...c, messages: [...c.messages, userMessage], updatedAt: Date.now() }
          : c
      ),
      isStreaming: true
    }))

    try {
      const conversation = state.conversations.find(c => c.id === convId)!
      const messages = [...conversation.messages, userMessage]

      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        ragContext
      }

      // Adicionar msg vazia do assistant para ir preenchendo
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(c =>
          c.id === convId
            ? { ...c, messages: [...c.messages, assistantMessage] }
            : c
        )
      }))

      let fullContent = ''
      let toolCallsBuffer = [];

      // 1. Call Chat Stream
      // Note: If the backend decides to call a tool, it might do so in the stream or at the end.
      // Our Python backend (api.py) currently sends tool_calls in the JSON response (non-streaming mostly),
      // OR if we use the streaming endpoint, we need to check if it sends structured tool calls.
      // Since we modified apiClient to yield tool_calls object, we check for type.

      for await (const chunk of apiClient.chatStream(messages)) {
        if (typeof chunk === 'string') {
            fullContent += chunk
            setState(prev => ({
              ...prev,
              conversations: prev.conversations.map(c =>
                c.id === convId
                  ? {
                      ...c,
                      messages: c.messages.map(m =>
                        m.id === assistantMessage.id
                          ? { ...m, content: fullContent }
                          : m
                      )
                    }
                  : c
              )
            }))
        } else if (typeof chunk === 'object' && 'tool_calls' in chunk) {
            // Received tool calls!
            toolCallsBuffer = chunk.tool_calls;
        }
      }

      // 2. Process Tool Calls (if any)
      // Note: If the stream finishes and we have tool calls, we execute them.
      // Ideally we should handle this recursively (Agent Loop), but for now 1 turn is good.

      // HACK: Check if content looks like a JSON tool call if strict parsing failed
      if (fullContent.includes('"tool_calls":') || fullContent.trim().startsWith('{')) {
         try {
            const possibleJson = JSON.parse(fullContent);
            if (possibleJson.tool_calls) {
                toolCallsBuffer = possibleJson.tool_calls;
                // Clean up the message content if it was just JSON
                if (!possibleJson.content) fullContent = "Executando ferramentas...";
            }
         } catch (e) {
             // Not valid JSON, ignore
         }
      }

      if (toolCallsBuffer.length > 0) {
        console.log("🛠️ Tool Calls Detected:", toolCallsBuffer);
        const results = await processToolCalls(toolCallsBuffer);

        // Add tool results to conversation history
        if (results && results.length > 0) {
             const toolOutputMsg: Message = {
                id: `msg_${Date.now() + 2}`,
                role: 'system', // Or 'tool' role if supported
                content: `Resultado das ferramentas:\n${JSON.stringify(results, null, 2)}`,
                timestamp: Date.now()
             };

             setState(prev => ({
                ...prev,
                conversations: prev.conversations.map(c =>
                  c.id === convId
                    ? { ...c, messages: [...c.messages, toolOutputMsg] }
                    : c
                )
              }));

              // Optionally: Send back to LLM for final response (Agent Loop)
              // sendMessage("Continue com base nos resultados acima."); // Recursion risk?
        }
      }

      // Adicionar resposta ao RAG
      ragService.addToMemory(fullContent)

      setState(prev => ({ ...prev, isStreaming: false }))

      // Salvar na memória eterna
      const finalConv = state.conversations.find(c => c.id === convId)!
      const title = finalConv.messages.length === 3
        ? content.substring(0, 50)
        : finalConv.title

      await memoryService.saveConversation({
        ...finalConv,
        title,
        updatedAt: Date.now()
      })

    } catch (error) {
      console.error('Erro no streaming:', error)
      setState(prev => ({ ...prev, isStreaming: false }))
    }
  }, [state.currentConversationId, state.conversations, newConversation, processToolCalls])

  return {
    conversations: state.conversations,
    currentConversation,
    isLoading: state.isLoading,
    isStreaming: state.isStreaming,
    newConversation,
    selectConversation,
    deleteConversation,
    sendMessage,
    // Agent Props
    pendingAction,
    confirmAction,
    cancelAction,
    isAgentExecuting,
    lastResult
  }
}
