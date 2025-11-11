import React from 'react';
import { LogoIcon } from './Icon';

const Header: React.FC = () => {
  return (
    <header className="w-full bg-gray-900/50 backdrop-blur-lg border-b border-cyan-500/30 p-4 sticky top-0 z-10">
      <div className="max-w-4xl mx-auto flex items-center justify-center space-x-4">
        <LogoIcon className="w-10 h-10 text-cyan-400" />
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-300 to-blue-500 bg-clip-text text-transparent tracking-wider">
          Superezio Realtime
        </h1>
      </div>
    </header>
  );
};

export default Header;