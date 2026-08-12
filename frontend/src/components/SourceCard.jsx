import React, { useState } from 'react';

const SourceCard = ({ source, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-md overflow-hidden mb-3 transition-all duration-200 hover:border-gray-600">
      <div 
        className="p-3 cursor-pointer flex justify-between items-center bg-gray-800/50 hover:bg-gray-700/50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-3">
          <span className="bg-emerald-600/20 text-emerald-400 text-xs font-bold px-2 py-1 rounded">
            Source {index + 1}
          </span>
          <h4 className="text-sm font-medium text-gray-200 truncate max-w-[200px] sm:max-w-xs">
            {source.document}
          </h4>
        </div>
        <div className="flex items-center space-x-4 text-xs text-gray-400">
          {source.page && <span>Page: {source.page}</span>}
          {source.section && <span>{source.section}</span>}
          <svg 
            className={`w-4 h-4 transition-transform duration-200 ${expanded ? 'transform rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      
      {expanded && (
        <div className="p-4 border-t border-gray-700 bg-gray-900/50">
          <p className="text-sm text-gray-300 leading-relaxed font-serif">
            "{source.content}"
          </p>
        </div>
      )}
    </div>
  );
};

export default SourceCard;
