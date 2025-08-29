import { useState } from 'react';
import { UserPreferences } from '../types';

const defaultPreferences: UserPreferences = {
  dietaryRestrictions: [],
  allergies: [],
  priceRange: [10, 30],
  favoriteCuisines: [],
  dislikedIngredients: [],
  spicePreference: 2,
  preferredMealTypes: [],
  generalDislikes: ''
};

export const usePreferences = () => {
  const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences);

  const updatePreferences = (updates: Partial<UserPreferences>) => {
    setPreferences(prev => ({ ...prev, ...updates }));
  };

  return {
    preferences,
    updatePreferences,
    setPreferences
  };
};