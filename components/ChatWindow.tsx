import React, { useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import ChatMessage from './ChatMessage';
import InputBar from './InputBar';
import { LoadingIcon } from './Icon';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, error, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <div className="flex flex-col flex-grow h-full bg-gray-900/50 backdrop-blur-sm rounded-xl border border-cyan-500/20 shadow-2xl shadow-black/50 overflow-hidden">
      <div className="flex-grow p-4 md:p-6 overflow-y-auto">
        <div className="flex flex-col space-y-6">
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))}
          {isLoading && messages[messages.length-1]?.role === 'user' && (
             <div className="flex justify-start animate-slide-in-bottom">
                <div className="flex items-center space-x-3 bg-gray-800 rounded-lg p-3 max-w-lg shadow-lg">
                  <LoadingIcon className="w-6 h-6 text-cyan-400" />
                   <p className="text-gray-400 italic text-sm">Analisando dados...</p>
                </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      {error && <div className="p-3 text-center text-red-300 bg-red-900/50 border-t border-cyan-500/20 font-semibold">{error}</div>}
      <InputBar onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatWindow;