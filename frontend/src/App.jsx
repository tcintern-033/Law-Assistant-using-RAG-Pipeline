import React from 'react';
import Chat from './components/Chat';
import Disclaimer from './components/Disclaimer';

function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans selection:bg-emerald-500/30">
      
      {/* Background decoration */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-900/20 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-blue-900/20 rounded-full blur-[100px]"></div>
      </div>

      <main className="relative z-10 container mx-auto px-4 py-8 h-screen flex flex-col">
        
        {/* Header section */}
        <div className="text-center mb-8 animate-fade-in-down">
          <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-200 mb-3 tracking-tight">
            Juris AI
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            AI-powered legal information retrieval from Pakistani legal documents
          </p>
        </div>

        <Disclaimer />

        {/* Chat UI */}
        <div className="flex-1 w-full max-w-5xl mx-auto flex flex-col">
          <Chat />
        </div>
        
      </main>
    </div>
  );
}

export default App;
