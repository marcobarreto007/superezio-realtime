/**
 * Componente ChatWindow
 * Janela principal do chat com mensagens
 */

import { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import type { Conversation } from '../types/chat'

interface ChatWindowProps {
  conversation: Conversation | undefined
  isStreaming: boolean
  onSendMessage: (message: string, image?: File) => void
}

export function ChatWindow({ conversation, isStreaming, onSendMessage }: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages])

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">SuperEzio</h2>
          <p>Selecione ou crie uma conversa pra começar</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">{conversation.title}</h2>
            <p className="text-sm text-gray-400">
              {conversation.messages.length} mensagens
            </p>
          </div>
          {/* Mostrar expert/LoRA da última mensagem do assistente */}
          {conversation.messages
            .filter(m => m.role === 'assistant')
            .slice(-1)[0] && (() => {
              const lastAssistant = conversation.messages
                .filter(m => m.role === 'assistant')
                .slice(-1)[0]
              return (lastAssistant.expert || lastAssistant.loraAdapter || lastAssistant.mode) ? (
                <div className="flex gap-2 text-xs">
                  {lastAssistant.expert && (
                    <span className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded">
                      {lastAssistant.expert}
                    </span>
                  )}
                  {lastAssistant.loraAdapter && (
                    <span className="px-2 py-1 bg-purple-900/30 text-purple-300 rounded">
                      {lastAssistant.loraAdapter}
                    </span>
                  )}
                </div>
              ) : null
            })()}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {conversation.messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isStreaming && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-800 text-gray-100 rounded-lg px-4 py-3">
              <div className="flex gap-1">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce delay-100">●</span>
                <span className="animate-bounce delay-200">●</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput
        onSend={onSendMessage}
        disabled={isStreaming}
        placeholder={isStreaming ? 'Aguarde...' : 'Manda aí...'}
      />
    </div>
  )
}
