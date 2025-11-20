/**
 * Componente Sidebar
 * Lista de conversas + botão nova conversa
 */

import type { Conversation } from '../types/chat'

interface SidebarProps {
  conversations: Conversation[]
  currentConversationId: string | null
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  onDeleteConversation: (id: string) => void
}

export function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation
}: SidebarProps) {
  return (
    <div className="w-64 bg-gray-900 border-r border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white mb-4">SuperEzio</h1>
        <button
          onClick={onNewConversation}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
        >
          + Nova Conversa
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`group relative p-3 rounded-lg mb-2 cursor-pointer transition-colors ${
              conv.id === currentConversationId
                ? 'bg-gray-800 border border-blue-600'
                : 'hover:bg-gray-800'
            }`}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-white truncate">
                  {conv.title}
                </h3>
                <p className="text-xs text-gray-400 mt-1">
                  {conv.messages.length} mensagens
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDeleteConversation(conv.id)
                }}
                className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-opacity"
                title="Deletar conversa"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 text-xs text-gray-500">
        <p>💾 Memória Eterna Ativa</p>
        <p>🔍 RAG Integrado</p>
        <p className="mt-2">100% Local • RTX 3060</p>
      </div>
    </div>
  )
}
