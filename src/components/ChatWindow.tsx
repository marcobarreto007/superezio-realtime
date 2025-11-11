import React, { useRef, useEffect, useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { useAgent } from '@/hooks/useAgent';
import MessageBubble from './MessageBubble';
import InputBar from './InputBar';
import LoadingIndicator from './LoadingIndicator';
import Header from './Header';
import AgentConfirmation from './AgentConfirmation';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, sendMessage, selectedModel, changeModel, clearConversation } = useChat();
  const { pendingAction, detectAndPrepareAction, executeAction, cancelAction } = useAgent();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Detectar comandos do agente nas mensagens
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'user') {
        const command = detectAndPrepareAction(lastMessage.content);
        if (command && command.requiresConfirmation) {
          setShowConfirmation(true);
        }
      }
    }
  }, [messages, detectAndPrepareAction]);

  const handleConfirmAction = async () => {
    const result = await executeAction(true);
    setShowConfirmation(false);
    if (result && result.result) {
      // Adicionar resultado como mensagem do sistema
      const resultMessage = {
        id: crypto.randomUUID(),
        role: 'assistant' as const,
        author: 'SuperEzio' as const,
        content: `✅ Ação executada: ${result.tool}\n${JSON.stringify(result.result, null, 2).substring(0, 500)}`,
        timestamp: new Date().toISOString(),
      };
      // Não adicionar automaticamente, deixar o usuário ver o resultado
    }
  };

  const handleCancelAction = () => {
    cancelAction();
    setShowConfirmation(false);
  };

  return (
    <div className="flex flex-col h-full">
      <Header 
        selectedModel={selectedModel} 
        onModelChange={changeModel}
        onClearConversation={clearConversation}
      />
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && (
          <div className="flex justify-start max-w-2xl mx-auto pl-4">
             <LoadingIndicator />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <InputBar onSendMessage={sendMessage} isLoading={isLoading} selectedModel={selectedModel} />
      
      {showConfirmation && pendingAction && (
        <AgentConfirmation
          tool={pendingAction.tool}
          parameters={pendingAction.parameters}
          onConfirm={handleConfirmAction}
          onCancel={handleCancelAction}
        />
      )}
    </div>
  );
};

export default ChatWindow;
