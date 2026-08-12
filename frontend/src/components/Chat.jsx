import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import { askQuestion } from '../services/api';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await askQuestion(userMessage.content);
      
      const botMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        disclaimer: response.disclaimer
      };
      
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.message || 'Something went wrong while connecting to the server.'}`,
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] w-full max-w-5xl mx-auto glass-panel rounded-xl shadow-2xl overflow-hidden border border-gray-700/50">
      
      {/* Header */}
      <div className="bg-gray-800/80 px-6 py-4 border-b border-gray-700/50 flex items-center justify-between z-10 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <span className="text-2xl bg-emerald-600/20 p-2 rounded-lg">⚖️</span>
          <div>
            <h2 className="text-lg font-bold text-gray-100 tracking-wide">Legal RAG Assistant</h2>
            <p className="text-xs text-emerald-400 font-medium">Pakistani Law Knowledge Base</p>
          </div>
        </div>
        <div className="hidden sm:flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs text-gray-400">System Online</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 scroll-smooth bg-gray-900/40 relative">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 animate-fade-in opacity-70">
            <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center border border-gray-700 mb-2">
              <span className="text-4xl">🇵🇰</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-300">How can I help you today?</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mt-4">
              <button onClick={() => setInput("What does the Constitution of Pakistan say about freedom of speech?")} className="text-sm bg-gray-800/80 hover:bg-gray-700 p-4 rounded-lg border border-gray-700/50 text-left transition-colors text-gray-300">
                "What does the Constitution of Pakistan say about freedom of speech?"
              </button>
              <button onClick={() => setInput("What are the essentials of a valid contract under the Contract Act?")} className="text-sm bg-gray-800/80 hover:bg-gray-700 p-4 rounded-lg border border-gray-700/50 text-left transition-colors text-gray-300">
                "What are the essentials of a valid contract under the Contract Act?"
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {messages.map((msg, idx) => (
              <Message key={idx} {...msg} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-6 animate-pulse">
                <div className="flex flex-row max-w-[85%] md:max-w-[75%] items-end">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-emerald-600/50 mr-4 flex items-center justify-center">
                    <span className="text-white text-sm">...</span>
                  </div>
                  <div className="glass-panel p-4 rounded-2xl rounded-tl-sm text-gray-400 text-sm">
                    Searching Pakistani legal documents...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-800/60 border-t border-gray-700/50 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Type your legal question..."
            className="w-full bg-gray-900 border border-gray-600 rounded-xl px-4 py-3 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 resize-none overflow-hidden min-h-[50px] max-h-[150px] transition-all"
            rows="1"
            style={{
              height: 'auto',
              minHeight: '52px'
            }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl p-3 flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-emerald-500/30"
          >
            <svg className="w-6 h-6 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
        <div className="text-center mt-2">
          <span className="text-[10px] text-gray-500 font-medium">AI generated legal information can be inaccurate. Always verify.</span>
        </div>
      </div>
    </div>
  );
};

export default Chat;
