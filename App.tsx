import React from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';

const App: React.FC = () => {
  return (
    <div className="min-h-screen text-white flex flex-col items-center">
      <Header />
      <main className="flex-grow flex flex-col w-full max-w-4xl p-4">
        <ChatWindow />
      </main>
    </div>
  );
};

export default App;