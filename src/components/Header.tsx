import React from 'react';
import { availableModels, getModelDisplayName } from '@/services/modelService';

interface HeaderProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  onClearConversation: () => void;
}

const Header: React.FC<HeaderProps> = ({ selectedModel, onModelChange, onClearConversation }) => {
  return (
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-cyan-400/20 p-4 shadow-lg">
      <div className="max-w-6xl mx-auto flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-2xl font-bold text-cyan-400 tracking-wider" style={{ fontFamily: "'Cinzel', serif" }}>
          SuperEzio Realtime
        </h1>
        
        <div className="flex items-center gap-4">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="bg-gray-800 text-gray-200 border border-cyan-500/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {availableModels.map((model) => (
              <option key={model.name} value={model.name}>
                {model.displayName}
              </option>
            ))}
          </select>
          
          <button
            onClick={onClearConversation}
            className="bg-red-600/80 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors text-sm"
            title="Limpar conversa"
          >
            Limpar
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
