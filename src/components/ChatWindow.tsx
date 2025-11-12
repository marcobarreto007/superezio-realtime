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
  onSendMessage: (message: string) => void
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
        <h2 className="text-xl font-bold text-white">{conversation.title}</h2>
        <p className="text-sm text-gray-400">
          {conversation.messages.length} mensagens
        </p>
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
