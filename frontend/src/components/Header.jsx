// frontend/src/components/Header.jsx
import { Heart, Info, Plus, Shield } from 'lucide-react';

const Header = ({ onNewChat, currentView, personalityMode }) => {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">AskHerCare</h1>
                <p className="text-xs text-gray-500">Your health companion</p>
              </div>
            </div>
          </div>

          {/* Center Status */}
          {currentView === 'chat' && personalityMode && (
            <div className="hidden md:flex items-center space-x-2 bg-purple-50 px-3 py-1 rounded-full">
              <span className="text-lg">{personalityMode.icon}</span>
              <span className="text-sm font-medium text-purple-700">
                {personalityMode.name}
              </span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center space-x-3">
            {/* Privacy Indicator */}
            <div className="flex items-center space-x-1 text-green-600">
              <Shield className="w-4 h-4" />
              <span className="text-xs font-medium">Anonymous</span>
            </div>

            {/* New Chat Button */}
            {currentView === 'chat' && (
              <button
                onClick={onNewChat}
                className="flex items-center space-x-1 bg-gradient-to-r from-pink-500 to-purple-600 text-white px-3 py-2 rounded-lg hover:shadow-lg transition-all duration-200"
              >
                <Plus className="w-4 h-4" />
                <span className="text-sm font-medium">New Chat</span>
              </button>
            )}

            {/* Info Button */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <Info className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;