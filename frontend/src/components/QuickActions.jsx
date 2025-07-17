// frontend/src/components/QuickActions.jsx
import { MessageSquare, Zap } from 'lucide-react';

const QuickActions = ({ category, onQuestionSelect }) => {
  const getQuickQuestions = (categoryId) => {
    const questions = {
      menstruation: [
        "What's a normal period cycle?",
        "Why is my period irregular?",
        "How to manage period pain?",
        "What are normal period symptoms?"
      ],
      pregnancy: [
        "Early signs of pregnancy?",
        "When to take a pregnancy test?",
        "What to expect in first trimester?",
        "Pregnancy nutrition tips?"
      ],
      pcos: [
        "What is PCOS exactly?",
        "PCOS symptoms to look for?",
        "How to manage PCOS naturally?",
        "PCOS and fertility concerns?"
      ],
      birth_control: [
        "What birth control is right for me?",
        "How effective are different methods?",
        "Birth control side effects?",
        "Emergency contraception options?"
      ],
      first_time_sex: [
        "What to expect the first time?",
        "How to prepare for first time?",
        "Is pain normal the first time?",
        "Safe sex practices?"
      ],
      vaginal_health: [
        "How to maintain vaginal health?",
        "Signs of vaginal infection?",
        "Normal vs abnormal discharge?",
        "When to see a gynecologist?"
      ]
    };
    return questions[categoryId] || [];
  };

  const quickQuestions = getQuickQuestions(category.id);

  if (quickQuestions.length === 0) return null;

  return (
    <div className="border-t bg-gradient-to-r from-pink-50 to-purple-50 p-4">
      <div className="flex items-center space-x-2 mb-3">
        <Zap className="w-4 h-4 text-purple-600" />
        <span className="text-sm font-medium text-gray-700">Quick Questions</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {quickQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionSelect(question)}
            className="text-left p-3 rounded-lg bg-white hover:bg-purple-50 border border-gray-200 hover:border-purple-300 transition-all duration-200 group"
          >
            <div className="flex items-start space-x-2">
              <MessageSquare className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700 group-hover:text-purple-700">
                {question}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;