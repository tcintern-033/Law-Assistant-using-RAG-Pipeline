import React from 'react';
import SourceCard from './SourceCard';

const Message = ({ role, content, sources }) => {
  const isBot = role === 'assistant';

  return (
    <div className={`flex w-full ${isBot ? 'justify-start' : 'justify-end'} mb-6`}>
      <div className={`flex max-w-[85%] md:max-w-[75%] ${isBot ? 'flex-row' : 'flex-row-reverse'}`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
          isBot ? 'bg-emerald-600 mr-4' : 'bg-blue-600 ml-4'
        }`}>
          {isBot ? (
            <span className="text-white text-lg">🇵🇰</span>
          ) : (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          )}
        </div>

        {/* Message Bubble */}
        <div className={`flex flex-col space-y-4 ${
          isBot 
            ? 'glass-panel p-5 rounded-2xl rounded-tl-sm' 
            : 'bg-blue-600 p-4 rounded-2xl rounded-tr-sm'
        }`}>
          <div className="prose prose-invert max-w-none text-sm md:text-base leading-relaxed">
            {content.split('\n').map((paragraph, i) => (
              <p key={i} className="mb-2 last:mb-0">{paragraph}</p>
            ))}
          </div>

          {/* Sources Section */}
          {isBot && sources && sources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-700/50">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center">
                <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Retrieved Legal Context
              </h4>
              <div className="space-y-2">
                {sources.map((source, idx) => (
                  <SourceCard key={idx} source={source} index={idx} />
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Message;
