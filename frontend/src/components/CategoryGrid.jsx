// frontend/src/components/CategoryGrid.jsx
import { ChevronRight, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';

const CategoryGrid = ({ onCategorySelect }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/categories');
      if (!response.ok) {
        throw new Error('Failed to fetch categories');
      }
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error('Error fetching categories:', error);
      setError('Failed to load categories');
      // Fallback to static categories
      setCategories([
        {
          id: "menstruation",
          name: "Menstruation",
          description: "Periods, cycle tracking, symptoms",
          icon: "🩸"
        },
        {
          id: "pregnancy",
          name: "Pregnancy",
          description: "Conception, pregnancy care, symptoms",
          icon: "🤱"
        },
        {
          id: "pcos",
          name: "PCOS",
          description: "Polycystic ovary syndrome",
          icon: "🫶"
        },
        {
          id: "birth_control",
          name: "Birth Control",
          description: "Contraceptives, family planning",
          icon: "💊"
        },
        {
          id: "first_time_sex",
          name: "First-time Sex",
          description: "Sexual health, first experiences",
          icon: "💕"
        },
        {
          id: "vaginal_health",
          name: "Vaginal Health",
          description: "Infections, hygiene, wellness",
          icon: "🌸"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryGradient = (index) => {
    const gradients = [
      'from-pink-400 to-rose-400',
      'from-purple-400 to-indigo-400',
      'from-blue-400 to-cyan-400',
      'from-green-400 to-emerald-400',
      'from-yellow-400 to-orange-400',
      'from-red-400 to-pink-400'
    ];
    return gradients[index % gradients.length];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">
          What can I help you with?
        </h2>
        <p className="text-gray-600">
          Choose a category or ask me anything directly
        </p>
      </div>

      {error && (
        <div className="text-center text-yellow-600 bg-yellow-50 rounded-lg p-3">
          {error} - Using offline categories
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((category, index) => (
          <CategoryCard
            key={category.id}
            category={category}
            gradient={getCategoryGradient(index)}
            onClick={() => onCategorySelect(category)}
          />
        ))}
      </div>
    </div>
  );
};

const CategoryCard = ({ category, gradient, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        relative overflow-hidden p-6 rounded-2xl text-left transition-all duration-300 transform
        ${isHovered ? 'scale-105 shadow-2xl' : 'shadow-lg hover:shadow-xl'}
        bg-gradient-to-br ${gradient} text-white
        focus:outline-none focus:ring-4 focus:ring-purple-300
      `}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-white/20"></div>
        <div className="absolute -bottom-4 -left-4 w-16 h-16 rounded-full bg-white/10"></div>
      </div>

      <div className="relative z-10">
        {/* Icon */}
        <div className="text-4xl mb-4">
          {category.icon}
        </div>

        {/* Content */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold">
            {category.name}
          </h3>
          <p className="text-white/90 text-sm leading-relaxed">
            {category.description}
          </p>
        </div>

        {/* Arrow */}
        <div className={`
          absolute top-4 right-4 transition-transform duration-300
          ${isHovered ? 'translate-x-1' : ''}
        `}>
          <ChevronRight className="w-5 h-5 text-white/80" />
        </div>

        {/* Hover Overlay */}
        <div className={`
          absolute inset-0 bg-white/10 transition-opacity duration-300
          ${isHovered ? 'opacity-100' : 'opacity-0'}
        `}></div>
      </div>
    </button>
  );
};

export default CategoryGrid;