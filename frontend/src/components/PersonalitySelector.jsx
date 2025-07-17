// frontend/src/components/PersonalitySelector.jsx
import { Check } from 'lucide-react';

const PersonalitySelector = ({ modes, selectedMode, onModeChange }) => {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-800 mb-2">
          Choose Your Preferred Style
        </h3>
        <p className="text-sm text-gray-600">
          How would you like me to communicate with you?
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modes.map((mode) => (
          <PersonalityCard
            key={mode.id}
            mode={mode}
            isSelected={selectedMode === mode.id}
            onSelect={() => onModeChange(mode.id)}
          />
        ))}
      </div>
    </div>
  );
};

const PersonalityCard = ({ mode, isSelected, onSelect }) => {
  return (
    <button
      onClick={onSelect}
      className={`
        relative p-6 rounded-2xl text-left transition-all duration-200 transform
        ${isSelected 
          ? 'ring-2 ring-purple-500 shadow-lg scale-105 bg-white' 
          : 'hover:shadow-md hover:scale-102 bg-white/80 backdrop-blur-sm'
        }
        border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-300
      `}
    >
      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute top-3 right-3">
          <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
            <Check className="w-4 h-4 text-white" />
          </div>
        </div>
      )}

      {/* Icon */}
      <div className="text-3xl mb-3">
        {mode.icon}
      </div>

      {/* Content */}
      <div className="space-y-2">
        <h4 className="font-semibold text-gray-800">
          {mode.name}
        </h4>
        <p className="text-sm text-gray-600 leading-relaxed">
          {mode.description}
        </p>
      </div>

      {/* Sample Response Preview */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-500 mb-1">Sample tone:</p>
        <p className="text-sm text-gray-700">
          {getSampleResponse(mode.id)}
        </p>
      </div>

      {/* Mode Badge */}
      <div className={`
        absolute top-3 left-3 px-2 py-1 rounded-full text-xs font-medium
        ${mode.color}
      `}>
        {mode.id}
      </div>
    </button>
  );
};

const getSampleResponse = (modeId) => {
  const samples = {
    doctor: "Based on medical research, this is a common concern that affects many women...",
    bestie: "Girl, I totally get why you're asking this! Here's what you need to know...",
    sister: "I'm so glad you felt comfortable asking me this. Let me help you understand..."
  };
  return samples[modeId] || samples.doctor;
};

export default PersonalitySelector;