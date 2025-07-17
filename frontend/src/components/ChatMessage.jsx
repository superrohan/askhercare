// frontend/src/components/ChatMessage.jsx
import {
    BookOpen,
    Bot,
    Check,
    ChevronDown,
    ChevronUp,
    Copy,
    ExternalLink,
    Sparkles,
    User
} from 'lucide-react';
import { useState } from 'react';

const ChatMessage = ({ message, onSimplify, onExplainTerm }) => {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [selectedText, setSelectedText] = useState('');

  const isUser = message.type === 'user';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    setSelectedText(text);
  };

  const handleExplainSelected = () => {
    if (selectedText) {
      onExplainTerm(selectedText);
      window.getSelection().removeAllRanges();
      setSelectedText('');
    }
  };

  const formatContent = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  const getPersonalityIcon = () => {
    if (message.personalityMode === 'bestie') return '💕';
    if (message.personalityMode === 'sister') return '🤗';
    return '👩‍⚕️';
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-gradient-to-r from-pink-500 to-purple-600' 
            : message.isError 
              ? 'bg-red-100' 
              : 'bg-blue-100'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : message.isError ? (
            <Bot className="w-5 h-5 text-red-600" />
          ) : (
            <span className="text-sm">{getPersonalityIcon()}</span>
          )}
        </div>

        {/* Message Bubble */}
        <div className={`rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-gradient-to-r from-pink-500 to-purple-600 text-white' 
            : message.isError 
              ? 'bg-red-50 border border-red-200' 
              : message.isExplanation 
                ? 'bg-blue-50 border border-blue-200'
                : 'bg-gray-100'
        }`}>
          <div 
            className={`${isUser ? 'text-white' : 'text-gray-800'} whitespace-pre-wrap`}
            onMouseUp={handleTextSelection}
            dangerouslySetInnerHTML={{ 
              __html: formatContent(
                message.showSimplified && message.simplifiedContent 
                  ? message.simplifiedContent 
                  : message.content
              ) 
            }}
          />

          {/* Message Actions */}
          {!isUser && !message.isError && (
            <div className="mt-3 flex flex-wrap gap-2">
              {/* Simplify Button */}
              <button
                onClick={() => onSimplify(message.id)}
                className="inline-flex items-center space-x-1 text-xs bg-white/80 hover:bg-white text-purple-600 px-2 py-1 rounded-full transition-colors"
              >
                <Sparkles className="w-3 h-3" />
                <span>Simplify</span>
              </button>

              {/* Copy Button */}
              <button
                onClick={handleCopy}
                className="inline-flex items-center space-x-1 text-xs bg-white/80 hover:bg-white text-gray-600 px-2 py-1 rounded-full transition-colors"
              >
                {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>

              {/* Explain Selected Text */}
              {selectedText && (
                <button
                  onClick={handleExplainSelected}
                  className="inline-flex items-center space-x-1 text-xs bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full transition-colors"
                >
                  <BookOpen className="w-3 h-3" />
                  <span>Explain "{selectedText.substring(0, 20)}..."</span>
                </button>
              )}
            </div>
          )}

          {/* Show Simplified Toggle */}
          {message.simplifiedContent && (
            <div className="mt-2">
              <button
                onClick={() => {
                  const updatedHistory = message.showSimplified 
                    ? { ...message, showSimplified: false }
                    : { ...message, showSimplified: true };
                  // This would need to be passed up to parent component
                }}
                className="text-xs text-purple-600 hover:text-purple-800 underline"
              >
                {message.showSimplified ? 'Show Original' : 'Show Simplified'}
              </button>
            </div>
          )}

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 border-t border-gray-200 pt-2">
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center space-x-1 text-xs text-gray-600 hover:text-gray-800"
              >
                <ExternalLink className="w-3 h-3" />
                <span>Sources ({message.sources.length})</span>
                {showSources ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>

              {showSources && (
                <div className="mt-2 space-y-1">
                  {message.sources.map((source, index) => (
                    <div key={index} className="text-xs bg-white/60 rounded p-2">
                      <div className="text-gray-600 truncate">
                        {source.content}
                      </div>
                      <div className="text-gray-500 text-xs mt-1">
                        Confidence: {Math.round(source.score * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Confidence Indicator */}
          {message.confidence && message.confidence < 0.7 && (
            <div className="mt-2 text-xs text-yellow-600 bg-yellow-50 rounded px-2 py-1">
              ⚠️ Please verify this information with a healthcare professional
            </div>
          )}

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${isUser ? 'text-white/70' : 'text-gray-500'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;