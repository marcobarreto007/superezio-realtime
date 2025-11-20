/**
 * Componente ChatWindow
 * Janela principal do chat com mensagens e confirmação de agente
 */

import { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import type { Conversation } from '../types/chat'
import { AgentConfirmation } from './AgentConfirmation'
import { PendingAction, ToolExecution } from '../../server/agentTools'

interface ChatWindowProps {
  conversation: Conversation | undefined
  isStreaming: boolean
  onSendMessage: (message: string) => void
  // Agent props
  pendingAction: PendingAction | null
  onConfirmAction: () => void
  onCancelAction: () => void
  isAgentExecuting: boolean
  lastResult: ToolExecution | null
}

export function ChatWindow({
  conversation,
  isStreaming,
  onSendMessage,
  pendingAction,
  onConfirmAction,
  onCancelAction,
  isAgentExecuting,
  lastResult
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages, lastResult])

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">SuperEzio Realtime</h2>
          <p className="mb-4">Multi-LoRA Local Agent</p>
          <p className="text-sm opacity-70">Selecione ou crie uma conversa pra começar</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-full relative">
      {/* Agent Confirmation Modal */}
      {pendingAction && (
        <AgentConfirmation
          action={pendingAction}
          onConfirm={onConfirmAction}
          onCancel={onCancelAction}
          isExecuting={isAgentExecuting}
        />
      )}

      {/* Header */}
      <div className="border-b border-gray-700 px-6 py-4 flex justify-between items-center bg-gray-900/50 backdrop-blur">
        <div>
            <h2 className="text-xl font-bold text-white">{conversation.title}</h2>
            <p className="text-sm text-gray-400">
            {conversation.messages.length} mensagens • Qwen2.5-7B (Multi-LoRA)
            </p>
        </div>
        {/* Status Indicator */}
        <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isStreaming || isAgentExecuting ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
            <span className="text-xs text-gray-500 uppercase font-mono">
                {isAgentExecuting ? 'EXECUTING TOOL' : isStreaming ? 'GENERATING' : 'IDLE'}
            </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {conversation.messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isStreaming && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-800 text-gray-100 rounded-lg px-4 py-3 border border-gray-700">
              <div className="flex gap-1">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce delay-100">●</span>
                <span className="animate-bounce delay-200">●</span>
              </div>
            </div>
          </div>
        )}

        {isAgentExecuting && !isStreaming && (
            <div className="flex justify-center my-4">
                <div className="bg-blue-900/30 text-blue-200 rounded-full px-4 py-1 text-xs font-mono flex items-center gap-2 border border-blue-800">
                    <span className="animate-spin w-3 h-3 border-2 border-blue-200/30 border-t-blue-200 rounded-full" />
                    Executando ferramenta do sistema...
                </div>
            </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput
        onSend={onSendMessage}
        disabled={isStreaming || !!pendingAction}
        placeholder={isStreaming ? 'Pensando...' : pendingAction ? 'Aguardando confirmação...' : 'Manda aí... (Pode pedir pra ler arquivos)'}
      />
    </div>
  )
}
