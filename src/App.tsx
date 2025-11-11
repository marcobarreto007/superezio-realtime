import React from 'react';
import ChatWindow from '@/components/ChatWindow';

function App() {
  return (
    <div className="h-screen w-screen bg-gray-900 text-white flex flex-col" style={{ 
      backgroundColor: '#0d1a26',
      backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.1) 1px, transparent 0)',
      backgroundSize: '40px 40px'
    }}>
      <ChatWindow />
    </div>
  );
}

export default App;
