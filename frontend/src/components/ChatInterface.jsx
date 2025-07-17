// frontend/src/components/ChatInterface.jsx
import {
    ArrowLeft,
    Loader2,
    Send
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import ChatMessage from './ChatMessage';
import QuickActions from './QuickActions';

const ChatInterface = ({ 
  personalityMode, 
  selectedCategory, 
  chatHistory, 
  setChatHistory,
  onBack 
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage.trim(),
          personality_mode: personalityMode,
          category: selectedCategory?.id || null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.message,
        sources: data.sources || [],
        confidence: data.confidence || 0.8,
        personalityMode: personalityMode,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        isError: true,
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSimplify = async (messageId) => {
    const message = chatHistory.find(m => m.id === messageId);
    if (!message) return;

    try {
      const response = await fetch('http://localhost:8000/simplify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: message.content })
      });

      const data = await response.json();
      
      setChatHistory(prev => prev.map(m => 
        m.id === messageId 
          ? { ...m, simplifiedContent: data.simplified_text, showSimplified: true }
          : m
      ));
    } catch (error) {
      console.error('Error simplifying message:', error);
    }
  };

  const handleExplainTerm = async (term) => {
    try {
      const response = await fetch('http://localhost:8000/explain-term', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ term })
      });

      const data = await response.json();
      
      const explanationMessage = {
        id: Date.now(),
        type: 'assistant',
        content: `**${data.term}**: ${data.explanation}`,
        isExplanation: true,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, explanationMessage]);
    } catch (error) {
      console.error('Error explaining term:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-pink-500 to-purple-600 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onBack}
              className="text-white/80 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-white font-semibold">
                {selectedCategory ? selectedCategory.name : 'Health Chat'}
              </h2>
              <p className="text-white/80 text-sm capitalize">
                {personalityMode} mode
              </p>
            </div>
          </div>
          
          {selectedCategory && (
            <div className="text-2xl">
              {selectedCategory.icon}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {chatHistory.length === 0 && (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">💬</div>
            <h3 className="text-lg font-medium text-gray-800 mb-2">
              Start Your Conversation
            </h3>
            <p className="text-gray-600">
              Ask me anything about women's health. I'm here to help!
            </p>
          </div>
        )}

        {chatHistory.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onSimplify={handleSimplify}
            onExplainTerm={handleExplainTerm}
          />
        ))}

        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {selectedCategory && (
        <QuickActions 
          category={selectedCategory}
          onQuestionSelect={(question) => {
            setInputMessage(question);
            textareaRef.current?.focus();
          }}
        />
      )}

      {/* Input */}
      <div className="border-t bg-gray-50 p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about women's health..."
              className="w-full px-4 py-3 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              rows={2}
              disabled={isLoading}
            />
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-gradient-to-r from-pink-500 to-purple-600 text-white p-3 rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500 text-center">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;