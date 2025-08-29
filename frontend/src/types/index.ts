export interface UserPreferences {
    dietaryRestrictions: string[];
    allergies: string[];
    priceRange: [number, number];
    favoriteCuisines: string[];
    dislikedIngredients: string[];
    spicePreference: number;
    preferredMealTypes: string[];
    generalDislikes: string;
  }
  
  export interface Review {
  id: string;
  user: string;
  rating: number;
  comment: string;
  date: string;
}

export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  ingredients: string[];
  allergens: string[];
  dietaryTags: string[];
  cuisine: string;
  mealType: string;
  spiceLevel: number;
  nutritionalInfo: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  reviews?: Review[];
  average_rating?: number;
  total_reviews?: number;
}
  
  export interface ChatMessage {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }
  
  export interface ChatSession {
    sessionId: string | null;
    messages: ChatMessage[];
    isStarted: boolean;
    isLoading: boolean;
  }