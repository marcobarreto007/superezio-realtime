/**
 * App SuperEzio
 * Interface limpa e direta - reflete a personalidade
 * Memória eterna + RAG + Streaming
 */

import { Sidebar } from './components/Sidebar'
import { ChatWindow } from './components/ChatWindow'
import { useChat } from './hooks/useChat'
import { useEffect } from 'react'

export default function App() {
  console.log('🚀 [App] Componente montado')
  
  const {
    conversations,
    currentConversation,
    isStreaming,
    newConversation,
    selectConversation,
    deleteConversation,
    sendMessage
  } = useChat()

  useEffect(() => {
    console.log('📊 [App] Estado atualizado:')
    console.log(`  - Conversas: ${conversations.length}`)
    console.log(`  - Conversa atual: ${currentConversation?.id || 'nenhuma'}`)
    console.log(`  - Streaming: ${isStreaming}`)
  }, [conversations, currentConversation, isStreaming])

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversation?.id || null}
        onSelectConversation={selectConversation}
        onNewConversation={newConversation}
        onDeleteConversation={deleteConversation}
      />

      {/* Chat Window */}
      <ChatWindow
        conversation={currentConversation}
        isStreaming={isStreaming}
        onSendMessage={sendMessage}
      />
    </div>
  )
}
