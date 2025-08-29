import React, { useState, useEffect } from 'react';
import { MenuItem, UserPreferences } from '../types';
import { Star, Clock, Flame, CheckCircle, AlertCircle, X } from 'lucide-react';
import { handleImageError, getFallbackImage } from '../utils/imageFallbacks';

interface MenuSectionProps {
  preferences: UserPreferences;
}

const MenuSection: React.FC<MenuSectionProps> = ({ preferences }) => {
  // Safety check - provide default preferences if undefined
  const safePreferences = preferences || {
    dietaryRestrictions: [],
    allergies: [],
    priceRange: [10, 30],
    favoriteCuisines: [],
    dislikedIngredients: [],
    spicePreference: 2,
    preferredMealTypes: [],
    generalDislikes: ''
  };
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<MenuItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [loading, setLoading] = useState(true);

  // Map API (backend) item shape to frontend MenuItem shape
  const mapApiItemToUi = (apiItem: any): MenuItem => {
    return {
      id: apiItem.id,
      name: apiItem.name,
      description: apiItem.description,
      price: apiItem.price,
      image: apiItem.image || apiItem.image_url || '',
      ingredients: apiItem.ingredients || [],
      allergens: apiItem.allergens || [],
      dietaryTags: apiItem.dietaryTags || apiItem.dietary_tags || [],
      cuisine: apiItem.cuisine || apiItem.cuisine_type || '',
      mealType: apiItem.mealType || apiItem.category || '',
      spiceLevel: apiItem.spiceLevel ?? apiItem.spice_level ?? 0,
      nutritionalInfo: apiItem.nutritionalInfo || apiItem.nutritional_info || { calories: 0, protein: 0, carbs: 0, fat: 0 },
      reviews: apiItem.reviews,
      average_rating: apiItem.average_rating,
      total_reviews: apiItem.total_reviews
    };
  };

  // Mock menu data - replace with actual API call
  const mockMenuItems: MenuItem[] = [
    {
      id: '1',
      name: 'Grilled Salmon with Quinoa',
      description: 'Fresh Atlantic salmon grilled to perfection, served with quinoa pilaf and seasonal vegetables',
      price: 24,
      image: 'https://images.pexels.com/photos/842571/pexels-photo-842571.jpeg',
      ingredients: ['Salmon', 'Quinoa', 'Broccoli', 'Lemon', 'Olive Oil', 'Garlic'],
      allergens: ['Fish'],
      dietaryTags: ['Gluten-Free', 'Dairy-Free'],
      cuisine: 'American',
      mealType: 'Main Course',
      spiceLevel: 1,
      nutritionalInfo: { calories: 420, protein: 35, carbs: 25, fat: 18 }
    },
    {
      id: '2',
      name: 'Vegetarian Buddha Bowl',
      description: 'Colorful bowl with quinoa, roasted chickpeas, avocado, and tahini dressing',
      price: 16,
      image: 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
      ingredients: ['Quinoa', 'Chickpeas', 'Avocado', 'Spinach', 'Carrots', 'Tahini', 'Lemon'],
      allergens: ['Sesame'],
      dietaryTags: ['Vegetarian', 'Vegan', 'Gluten-Free'],
      cuisine: 'Mediterranean',
      mealType: 'Main Course',
      spiceLevel: 2,
      nutritionalInfo: { calories: 380, protein: 15, carbs: 45, fat: 16 }
    },
    {
      id: '3',
      name: 'Spicy Thai Basil Chicken',
      description: 'Authentic Thai stir-fry with ground chicken, Thai basil, and jasmine rice',
      price: 19,
      image: 'https://images.pexels.com/photos/2641886/pexels-photo-2641886.jpeg',
      ingredients: ['Chicken', 'Thai Basil', 'Rice', 'Chili Peppers', 'Garlic', 'Fish Sauce', 'Soy Sauce'],
      allergens: ['Soybeans', 'Fish'],
      dietaryTags: ['Gluten-Free', 'Dairy-Free'],
      cuisine: 'Thai',
      mealType: 'Main Course',
      spiceLevel: 4,
      nutritionalInfo: { calories: 450, protein: 28, carbs: 35, fat: 20 }
    },
    {
      id: '4',
      name: 'Margherita Pizza',
      description: 'Classic Italian pizza with fresh mozzarella, basil, and san marzano tomatoes',
      price: 18,
      image: 'https://images.pexels.com/photos/315755/pexels-photo-315755.jpeg',
      ingredients: ['Wheat Flour', 'Mozzarella', 'Tomatoes', 'Basil', 'Olive Oil'],
      allergens: ['Wheat', 'Milk'],
      dietaryTags: ['Vegetarian'],
      cuisine: 'Italian',
      mealType: 'Main Course',
      spiceLevel: 1,
      nutritionalInfo: { calories: 520, protein: 22, carbs: 55, fat: 24 }
    },
    {
      id: '5',
      name: 'Chocolate Lava Cake',
      description: 'Rich chocolate cake with molten center, served with vanilla ice cream',
      price: 9,
      image: 'https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg',
      ingredients: ['Chocolate', 'Eggs', 'Butter', 'Sugar', 'Wheat Flour', 'Vanilla'],
      allergens: ['Eggs', 'Milk', 'Wheat'],
      dietaryTags: ['Vegetarian'],
      cuisine: 'American',
      mealType: 'Dessert',
      spiceLevel: 1,
      nutritionalInfo: { calories: 380, protein: 6, carbs: 45, fat: 20 }
    },
    {
      id: '6',
      name: 'Caesar Salad',
      description: 'Crisp romaine lettuce with parmesan, croutons, and house-made caesar dressing',
      price: 14,
      image: 'https://images.pexels.com/photos/2116094/pexels-photo-2116094.jpeg',
      ingredients: ['Romaine Lettuce', 'Parmesan', 'Croutons', 'Anchovies', 'Eggs', 'Garlic', 'Lemon'],
      allergens: ['Fish', 'Eggs', 'Milk', 'Wheat'],
      dietaryTags: ['Vegetarian'],
      cuisine: 'American',
      mealType: 'Salad',
      spiceLevel: 1,
      nutritionalInfo: { calories: 280, protein: 12, carbs: 18, fat: 20 }
    }
  ];

  useEffect(() => {
    // Simulate API call
    const loadMenu = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/meals/menu');
        if (!response.ok) {
          throw new Error('Failed to fetch menu data');
        }
        const data = await response.json();
        const normalized = Array.isArray(data) ? data.map(mapApiItemToUi) : [];
        setMenuItems(normalized);
      } catch (error) {
        console.error('Failed to load menu:', error);
        // Fallback to mock data if API call fails
        setMenuItems(mockMenuItems);
      } finally {
        setLoading(false);
      }
    };

    loadMenu();
  }, []);

  useEffect(() => {
    // Filter menu items based on preferences
    const filtered = menuItems.filter(item => {
      // Price filter
      if (safePreferences.priceRange && safePreferences.priceRange[1] && item.price > safePreferences.priceRange[1]) return false;

      // Allergy filter
      if (safePreferences.allergies && Array.isArray(safePreferences.allergies)) {
        const hasAllergen = safePreferences.allergies.some(allergy => 
          item.allergens && item.allergens.includes(allergy)
        );
        if (hasAllergen) return false;
      }

      // Disliked ingredients filter
      if (safePreferences.dislikedIngredients && Array.isArray(safePreferences.dislikedIngredients)) {
        const hasDislikedIngredient = safePreferences.dislikedIngredients.some(ingredient =>
          item.ingredients && item.ingredients.some(itemIngredient => 
            itemIngredient.toLowerCase().includes(ingredient.toLowerCase())
          )
        );
        if (hasDislikedIngredient) return false;
      }

      // Spice level filter (allow items at or below preferred level)
      if (safePreferences.spicePreference && item.spiceLevel > safePreferences.spicePreference) return false;

      return true;
    });

    setFilteredItems(filtered);
  }, [menuItems, safePreferences]);

  const getCompatibilityScore = (item: MenuItem) => {
    let score = 0;
    let maxScore = 0;

    // Dietary restrictions match
    if (safePreferences.dietaryRestrictions && Array.isArray(safePreferences.dietaryRestrictions)) {
      safePreferences.dietaryRestrictions.forEach(restriction => {
        maxScore += 1;
        if (item.dietaryTags && item.dietaryTags.includes(restriction)) score += 1;
      });
    }

    // Cuisine preference match
    if (safePreferences.favoriteCuisines && safePreferences.favoriteCuisines.length > 0) {
      maxScore += 1;
      if (safePreferences.favoriteCuisines.includes(item.cuisine_type || item.cuisine)) score += 1;
    }

    // Meal type preference match
    if (safePreferences.preferredMealTypes && safePreferences.preferredMealTypes.length > 0) {
      maxScore += 1;
      if (safePreferences.preferredMealTypes.includes(item.mealType)) score += 1;
    }

    return maxScore > 0 ? (score / maxScore) * 100 : 50;
  };

  const isHighCompatibility = (item: MenuItem) => getCompatibilityScore(item) >= 75;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="space-y-3">
                <div className="h-48 bg-gray-200 rounded-lg"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">Menu</h2>
          <div className="text-sm text-gray-600">
            {filteredItems.length} of {menuItems.length} items
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map(item => (
            <div
              key={item.id}
              onClick={() => setSelectedItem(item)}
              className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer group"
            >
              <div className="relative">
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => handleImageError(e, item.cuisine_type || item.cuisine, 'small')}
                />
                {isHighCompatibility(item) && (
                  <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3" />
                    <span>Great Match!</span>
                  </div>
                )}
                <div className="absolute bottom-2 left-2 flex space-x-1">
                  {Array.from({ length: item.spiceLevel }, (_, i) => (
                    <Flame key={i} className="w-3 h-3 text-orange-500 fill-current" />
                  ))}
                </div>
              </div>
              
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-800 group-hover:text-amber-600 transition-colors">
                    {item.name}
                  </h3>
                  <span className="text-lg font-bold text-amber-600">${item.price}</span>
                </div>
                
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {item.description}
                </p>
                
                <div className="flex flex-wrap gap-1 mb-3">
                  {(item.dietaryTags || []).slice(0, 2).map(tag => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {item.cuisine_type || item.cuisine}
                  </span>
                </div>
                
                {item.allergens.length > 0 && (
                  <div className="flex items-center space-x-1 text-xs text-red-600">
                    <AlertCircle className="w-3 h-3" />
                    <span>Contains: {item.allergens.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Clock className="w-12 h-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-600 mb-2">No items match your preferences</h3>
            <p className="text-gray-500">Try adjusting your filters to see more options</p>
          </div>
        )}
      </div>

      {/* Menu Item Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="relative">
              <img
                src={selectedItem.image}
                alt={selectedItem.name}
                className="w-full h-80 object-cover"
                onError={(e) => handleImageError(e, selectedItem.cuisine_type || selectedItem.cuisine, 'medium')}
              />
              <button
                onClick={() => setSelectedItem(null)}
                className="absolute top-4 right-4 bg-white rounded-full p-2 hover:bg-gray-100 transition-colors shadow-lg"
              >
                <X className="w-5 h-5" />
              </button>
              {isHighCompatibility(selectedItem) && (
                <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-2 rounded-full text-sm font-medium flex items-center space-x-2 shadow-lg">
                  <CheckCircle className="w-4 h-4" />
                  <span>Perfect Match!</span>
                </div>
              )}
              
              {/* Popularity Score Badge */}
              <div className="absolute bottom-4 left-4 bg-amber-500 text-white px-3 py-2 rounded-full text-sm font-medium flex items-center space-x-2 shadow-lg">
                <Star className="w-4 h-4" />
                <span>{selectedItem.popularity_score || 8.0}/10</span>
              </div>
            </div>
            
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-800">{selectedItem.name}</h2>
                <span className="text-2xl font-bold text-amber-600">${selectedItem.price}</span>
              </div>
              
              <p className="text-gray-600 mb-6">{selectedItem.description}</p>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-800 mb-3">Ingredients</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedItem.ingredients.map(ingredient => (
                      <span
                        key={ingredient}
                        className={`px-2 py-1 rounded-full text-xs ${
                          safePreferences.dislikedIngredients.some(disliked =>
                            ingredient.toLowerCase().includes(disliked.toLowerCase())
                          )
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {ingredient}
                      </span>
                    ))}
                  </div>
                  
                  <h3 className="font-semibold text-gray-800 mb-3 mt-6">Dietary Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedItem.dietaryTags || []).map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  {selectedItem.allergens.length > 0 && (
                    <>
                      <h3 className="font-semibold text-gray-800 mb-3 mt-6 flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-red-600" />
                        <span>Allergens</span>
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedItem.allergens.map(allergen => (
                          <span
                            key={allergen}
                            className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full"
                          >
                            {allergen}
                          </span>
                        ))}
                      </div>
                    </>
                  )}
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-800 mb-3">Nutritional Info</h3>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Calories:</span>
                      <span className="font-medium">{selectedItem.nutritionalInfo.calories}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Protein:</span>
                      <span className="font-medium">{selectedItem.nutritionalInfo.protein}g</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Carbs:</span>
                      <span className="font-medium">{selectedItem.nutritionalInfo.carbs}g</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Fat:</span>
                      <span className="font-medium">{selectedItem.nutritionalInfo.fat}g</span>
                    </div>
                  </div>
                  
                  <div className="mt-6 space-y-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600">Cuisine:</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        {selectedItem.cuisine_type || selectedItem.cuisine}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600">Spice Level:</span>
                      <div className="flex space-x-1">
                        {Array.from({ length: 5 }, (_, i) => (
                          <Flame
                            key={i}
                            className={`w-4 h-4 ${
                              i < selectedItem.spiceLevel
                                ? 'text-orange-500 fill-current'
                                : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600">Compatibility:</span>
                      <div className="flex items-center space-x-1">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${getCompatibilityScore(selectedItem)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-green-600">
                          {Math.round(getCompatibilityScore(selectedItem))}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Reviews Section */}
                {selectedItem.reviews && selectedItem.reviews.length > 0 && (
                  <div className="mt-8">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-semibold text-gray-800">Customer Reviews</h3>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              className={`w-5 h-5 ${
                                star <= (selectedItem.average_rating || 0)
                                  ? 'text-yellow-400 fill-current'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-lg font-semibold text-gray-800">
                          {selectedItem.average_rating?.toFixed(1) || 'N/A'}
                        </span>
                        <span className="text-gray-500">
                          ({selectedItem.total_reviews || 0} reviews)
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {selectedItem.reviews.slice(0, 3).map((review) => (
                        <div key={review.id} className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-800">{review.user}</span>
                            <div className="flex items-center space-x-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`w-4 h-4 ${
                                    star <= review.rating
                                      ? 'text-yellow-400 fill-current'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                          </div>
                          <p className="text-gray-600 text-sm mb-2">{review.comment}</p>
                          <span className="text-xs text-gray-400">{review.date}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MenuSection;