import React from 'react';
import { Message } from '@/types';
import MarkdownMessage from './MarkdownMessage';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const { role, content, author, timestamp } = message;
  const isUser = role === 'user';

  const bubbleClasses = isUser
    ? 'bg-cyan-800/60 text-white self-end rounded-l-xl rounded-br-xl'
    : 'bg-gray-800/70 text-gray-300 self-start rounded-r-xl rounded-bl-xl';
  
  const authorName = isUser ? 'Você' : author;
  const authorClass = isUser ? 'text-cyan-300' : 'text-purple-400';

  const formattedTime = new Date(timestamp).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`flex flex-col w-full max-w-2xl mx-auto animate-slide-in-bottom ${isUser ? 'items-end' : 'items-start'}`}>
      <div className={`px-4 py-3 ${bubbleClasses} shadow-md max-w-full`}>
        <div className="flex items-center mb-1">
          <span className={`font-bold text-sm ${authorClass}`}>{authorName}</span>
        </div>
        <div className="text-base">
          {isUser ? (
            <p className="whitespace-pre-wrap">{content}</p>
          ) : (
            <MarkdownMessage content={content} />
          )}
        </div>
        <div className="text-xs text-gray-500 mt-2 text-right">
          {formattedTime}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
