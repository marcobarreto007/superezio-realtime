import React, { useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import MessageBubble from './MessageBubble';
import InputBar from './InputBar';
import LoadingIndicator from './LoadingIndicator';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full">
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
      <InputBar onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatWindow;
