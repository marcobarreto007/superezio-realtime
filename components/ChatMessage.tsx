import React from 'react';
import { ChatMessage as ChatMessageType } from '../types';
import { UserIcon, BotIcon, CopyIcon, ReportIcon } from './Icon';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isCSV = message.content.includes('```csv');

  const handleCopy = () => {
    const csvContent = message.content.replace(/```csv\n|```/g, '');
    navigator.clipboard.writeText(csvContent);
  };
  
  const renderContent = () => {
    if (isCSV) {
      const csvContent = message.content.replace(/```csv\n|```/g, '').trim();
      return (
        <div className="bg-gray-900/70 border border-cyan-500/20 rounded-lg overflow-hidden shadow-lg">
          <div className="flex justify-between items-center p-3 bg-gray-800/80 border-b border-cyan-500/20">
            <div className="flex items-center space-x-2">
              <ReportIcon className="w-5 h-5 text-cyan-400" />
              <span className="text-sm font-bold text-gray-200 tracking-wide">Relatório Financeiro</span>
            </div>
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 text-xs bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-1 px-3 rounded-md transition-all duration-200 transform hover:scale-105"
            >
              <CopyIcon className="w-4 h-4" />
              <span>Copiar</span>
            </button>
          </div>
          <pre className="whitespace-pre-wrap text-sm text-gray-300 overflow-x-auto p-4 font-mono">
            <code>{csvContent}</code>
          </pre>
        </div>
      );
    }
    
    // Basic markdown for bold text **text**
    const parts = message.content.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={i} className="font-bold text-cyan-400">{part.slice(2, -2)}</strong>;
        }
        return part;
    });
  };

  if (isUser) {
    return (
      <div className="flex justify-end animate-slide-in-bottom">
        <div className="flex items-start gap-3 max-w-xl">
          <div className="relative bg-gradient-to-br from-blue-600 to-cyan-700 rounded-lg p-3 shadow-md">
            <p className="text-white">{message.content}</p>
          </div>
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-inner">
            <UserIcon className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-slide-in-bottom">
      <div className="flex items-start gap-3 max-w-xl">
        <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0 shadow-inner">
         <BotIcon className="w-7 h-7 text-gray-300" />
        </div>
        <div className="bg-gray-800 rounded-lg p-3 shadow-md">
          <div className="text-gray-200 whitespace-pre-wrap leading-relaxed">{renderContent()}</div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;