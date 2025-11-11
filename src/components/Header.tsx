import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-cyan-400/20 p-4 text-center shadow-lg">
      <h1 className="text-2xl font-bold text-cyan-400 tracking-wider" style={{ fontFamily: "'Cinzel', serif" }}>
        SuperEzio Realtime
      </h1>
    </header>
  );
};

export default Header;
