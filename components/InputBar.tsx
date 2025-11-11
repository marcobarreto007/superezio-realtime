import React, { useState, useRef, useEffect } from 'react';
import { SendIcon } from './Icon';

interface InputBarProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const InputBar: React.FC<InputBarProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="p-4 bg-gray-900/60 border-t border-cyan-500/20">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3 group">
        <div className="flex-grow relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Faça uma pergunta sobre suas finanças..."
            rows={1}
            className="w-full max-h-40 bg-gray-800 border border-gray-700 rounded-lg p-3 pr-4 text-white placeholder-gray-500 focus:outline-none resize-none transition-all duration-200 ring-2 ring-transparent group-focus-within:ring-cyan-500"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="bg-cyan-500 text-white rounded-full p-3 hover:bg-cyan-400 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all duration-200 shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-400 transform hover:scale-110 disabled:scale-100"
        >
          <SendIcon className="w-6 h-6" />
        </button>
      </form>
    </div>
  );
};

export default InputBar;