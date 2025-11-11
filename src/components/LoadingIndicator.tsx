import React from 'react';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex items-center space-x-2">
      <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse [animation-delay:-0.3s]"></div>
      <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse [animation-delay:-0.15s]"></div>
      <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
      <span className="text-sm text-gray-400">SuperEzio está digitando...</span>
    </div>
  );
};

export default LoadingIndicator;
