import { Heart, MessageCircle } from 'lucide-react';
import { useState } from 'react';
import CategoryGrid from './components/CategoryGrid';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import PersonalitySelector from './components/PersonalitySelector';

const App = () => {
  const [currentView, setCurrentView] = useState('home');
  const [personalityMode, setPersonalityMode] = useState('doctor');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);

  const personalityModes = [
    {
      id: 'doctor',
      name: 'Doctor Mode',
      description: 'Professional medical guidance',
      icon: '👩‍⚕️',
      color: 'bg-blue-100 text-blue-800'
    },
    {
      id: 'bestie',
      name: 'Bestie Mode',
      description: 'Friendly, supportive advice',
      icon: '💕',
      color: 'bg-pink-100 text-pink-800'
    },
    {
      id: 'sister',
      name: 'Sister Mode',
      description: 'Caring, gentle support',
      icon: '🤗',
      color: 'bg-purple-100 text-purple-800'
    }
  ];

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setCurrentView('chat');
  };

  const handleNewChat = () => {
    setChatHistory([]);
    setSelectedCategory(null);
    setCurrentView('home');
  };

  const currentPersonality = personalityModes.find(p => p.id === personalityMode);

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50">
      <Header 
        onNewChat={handleNewChat}
        currentView={currentView}
        personalityMode={currentPersonality}
      />
      
      <main className="max-w-4xl mx-auto px-4 py-6">
        {currentView === 'home' && (
          <div className="space-y-8">
            {/* Welcome Section */}
            <div className="text-center space-y-4">
              <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
                <Heart className="w-5 h-5 text-pink-500" />
                <span className="text-lg font-medium text-gray-800">AskHerCare</span>
              </div>
              
              <h1 className="text-3xl md:text-4xl font-bold text-gray-800 leading-tight">
                Your Safe Space for
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-600">
                  Women's Health Questions
                </span>
              </h1>
              
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Get accurate, caring answers to your health questions. Anonymous, private, and always here for you.
              </p>
            </div>

            {/* Personality Selector */}
            <PersonalitySelector
              modes={personalityModes}
              selectedMode={personalityMode}
              onModeChange={setPersonalityMode}
            />

            {/* Categories */}
            <CategoryGrid onCategorySelect={handleCategorySelect} />

            {/* Quick Start */}
            <div className="text-center">
              <button
                onClick={() => setCurrentView('chat')}
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white px-8 py-4 rounded-full font-medium shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Start Chatting</span>
              </button>
            </div>
          </div>
        )}

        {currentView === 'chat' && (
          <ChatInterface
            personalityMode={personalityMode}
            selectedCategory={selectedCategory}
            chatHistory={chatHistory}
            setChatHistory={setChatHistory}
            onBack={() => setCurrentView('home')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 pb-6 text-center text-sm text-gray-500">
        <p>
          💜 Built with care for women's health education. 
          Always consult healthcare professionals for medical decisions.
        </p>
      </footer>
    </div>
  );
};

export default App;