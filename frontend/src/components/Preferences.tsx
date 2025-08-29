import React from 'react';
import { UserPreferences } from '../types';
import { 
  Heart, 
  AlertTriangle, 
  DollarSign, 
  Globe, 
  X, 
  Flame,
  UtensilsCrossed,
  MessageSquare,
  Check
} from 'lucide-react';
import allergiesData from '../data/allergy.json';
import ingredients from '../data/ingredients.json';

interface PreferencesProps {
  preferences: UserPreferences;
  onUpdatePreferences: (updates: Partial<UserPreferences>) => void;
  onSubmitPreferences: () => void;
  isSubmitted: boolean;
}

const Preferences: React.FC<PreferencesProps> = ({ 
  preferences, 
  onUpdatePreferences, 
  onSubmitPreferences,
  isSubmitted 
}) => {
  const dietaryOptions = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Paleo'];
  const cuisineOptions = ['Italian', 'Mexican', 'Indian', 'Chinese', 'American', 'Thai', 'Mediterranean', 'Japanese'];
  const mealTypeOptions = ['Appetizer', 'Main Course', 'Dessert', 'Side', 'Salad', 'Soup'];

  const toggleArrayItem = (array: string[], item: string, key: keyof UserPreferences) => {
    const newArray = array.includes(item)
      ? array.filter(i => i !== item)
      : [...array, item];
    onUpdatePreferences({ [key]: newArray });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <Heart className="text-amber-600 w-6 h-6" />
        <h2 className="text-2xl font-semibold text-gray-800">Your Preferences</h2>
      </div>

      {/* Dietary Restrictions */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <UtensilsCrossed className="text-green-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Dietary Restrictions</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {dietaryOptions.map(option => (
            <button
              key={option}
              onClick={() => toggleArrayItem(preferences.dietaryRestrictions, option, 'dietaryRestrictions')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                preferences.dietaryRestrictions.includes(option)
                  ? 'bg-green-100 text-green-800 border-2 border-green-300'
                  : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {/* Allergies */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="text-red-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Allergies</h3>
        </div>
        <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
          {allergiesData.common_allergens.map(allergy => (
            <button
              key={allergy}
              onClick={() => toggleArrayItem(preferences.allergies, allergy, 'allergies')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                preferences.allergies.includes(allergy)
                  ? 'bg-red-100 text-red-800 border-2 border-red-300'
                  : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
              }`}
            >
              {allergy}
            </button>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <DollarSign className="text-amber-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Price Range</h3>
        </div>
        <div className="space-y-2">
          <input
            type="range"
            min="5"
            max="50"
            value={preferences.priceRange[1]}
            onChange={(e) => onUpdatePreferences({
              priceRange: [preferences.priceRange[0], parseInt(e.target.value)]
            })}
            className="w-full accent-amber-600"
          />
          <div className="flex justify-between text-sm text-gray-600">
            <span>${preferences.priceRange[0]}</span>
            <span>${preferences.priceRange[1]}</span>
          </div>
        </div>
      </div>

      {/* Favorite Cuisines */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <Globe className="text-blue-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Favorite Cuisines</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {cuisineOptions.map(cuisine => (
            <button
              key={cuisine}
              onClick={() => toggleArrayItem(preferences.favoriteCuisines, cuisine, 'favoriteCuisines')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                preferences.favoriteCuisines.includes(cuisine)
                  ? 'bg-blue-100 text-blue-800 border-2 border-blue-300'
                  : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
              }`}
            >
              {cuisine}
            </button>
          ))}
        </div>
      </div>

      {/* Spice Preference */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <Flame className="text-orange-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Spice Level (1-5)</h3>
        </div>
        <div className="space-y-2">
          <input
            type="range"
            min="1"
            max="5"
            value={preferences.spicePreference}
            onChange={(e) => onUpdatePreferences({ spicePreference: parseInt(e.target.value) })}
            className="w-full accent-orange-600"
          />
          <div className="flex justify-center">
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map(level => (
                <Flame
                  key={level}
                  className={`w-4 h-4 ${
                    level <= preferences.spicePreference 
                      ? 'text-orange-600 fill-current' 
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Preferred Meal Types */}
      <div className="space-y-3">
        <h3 className="font-medium text-gray-700">Preferred Meal Types</h3>
        <div className="flex flex-wrap gap-2">
          {mealTypeOptions.map(type => (
            <button
              key={type}
              onClick={() => toggleArrayItem(preferences.preferredMealTypes, type, 'preferredMealTypes')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                preferences.preferredMealTypes.includes(type)
                  ? 'bg-purple-100 text-purple-800 border-2 border-purple-300'
                  : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Disliked Ingredients */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <X className="text-gray-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Disliked Ingredients</h3>
        </div>
        <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
          {ingredients.map(ingredient => (
            <button
              key={ingredient}
              onClick={() => toggleArrayItem(preferences.dislikedIngredients, ingredient, 'dislikedIngredients')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                preferences.dislikedIngredients.includes(ingredient)
                  ? 'bg-gray-200 text-gray-800 border-2 border-gray-400'
                  : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
              }`}
            >
              {ingredient}
            </button>
          ))}
        </div>
      </div>

      {/* General Dislikes */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <MessageSquare className="text-gray-600 w-5 h-5" />
          <h3 className="font-medium text-gray-700">Additional Notes</h3>
        </div>
        <textarea
          value={preferences.generalDislikes}
          onChange={(e) => onUpdatePreferences({ generalDislikes: e.target.value })}
          placeholder="Any other preferences or dislikes..."
          className="w-full p-3 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          rows={3}
        />
      </div>

      {/* Submit Button */}
      <div className="pt-4 border-t border-gray-200">
        <button
          onClick={onSubmitPreferences}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 ${
            isSubmitted
              ? 'bg-green-100 text-green-800 border-2 border-green-300'
              : 'bg-amber-600 text-white hover:bg-amber-700 hover:shadow-lg transform hover:-translate-y-0.5'
          }`}
        >
          {isSubmitted ? (
            <>
              <Check className="w-5 h-5" />
              <span>Preferences Submitted</span>
            </>
          ) : (
            <>
              <Heart className="w-5 h-5" />
              <span>Submit My Preferences</span>
            </>
          )}
        </button>
        {isSubmitted && (
          <p className="text-center text-sm text-green-600 mt-2">
            Your preferences have been saved and will be used for recommendations!
          </p>
        )}
      </div>
    </div>
  );
};

export default Preferences;