import React, { useState, useRef, useEffect } from 'react';

interface InputBarProps {
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

const InputBar: React.FC<InputBarProps> = ({ onSendMessage, isLoading }) => {
  const [text, setText] = useState('');
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (text.trim() && !isLoading) {
      onSendMessage(text);
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const textArea = textAreaRef.current;
    if (textArea) {
      textArea.style.height = 'auto';
      const scrollHeight = textArea.scrollHeight;
      // Limit height to a max of 10rem (160px) and allow scrolling
      textArea.style.overflowY = scrollHeight > 160 ? 'auto' : 'hidden';
      textArea.style.height = `${Math.min(scrollHeight, 160)}px`;
    }
  }, [text]);

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border-t border-cyan-400/20 p-4">
      <div className="max-w-2xl mx-auto flex items-end space-x-4">
        <textarea
          ref={textAreaRef}
          className="flex-1 bg-gray-800/70 text-gray-200 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500 transition-shadow duration-300"
          placeholder="Digite sua mensagem..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !text.trim()}
          className="bg-cyan-600 text-white rounded-full p-3 hover:bg-cyan-500 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-gray-900 shrink-0"
          aria-label="Enviar mensagem"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default InputBar;
