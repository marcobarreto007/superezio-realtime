import React from 'react';
import Header from '@/components/Header';
import ChatWindow from '@/components/ChatWindow';

function App() {
  return (
    <div className="h-screen w-screen bg-gray-900 text-white flex flex-col" style={{ 
      backgroundColor: '#0d1a26',
      backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.1) 1px, transparent 0)',
      backgroundSize: '40px 40px'
    }}>
      <Header />
      <main className="flex-1 overflow-hidden">
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;
