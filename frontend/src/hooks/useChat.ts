import { useState, useCallback } from 'react';
import { ChatSession, ChatMessage, UserPreferences } from '../types';

// Transform frontend preferences to backend format
const transformPreferencesForBackend = (preferences: UserPreferences) => ({
  dietary_restrictions: preferences.dietaryRestrictions.map(d => d.toLowerCase().replace('-', '_')),
  allergies: preferences.allergies,
  price_range: preferences.priceRange,
  favorite_cuisines: preferences.favoriteCuisines.map(c => c.toLowerCase()),
  disliked_ingredients: preferences.dislikedIngredients,
  spice_preference: preferences.spicePreference,
  preferred_meal_types: preferences.preferredMealTypes.map(m => m.toLowerCase().replace(' ', '_')),
  dislikes: preferences.generalDislikes ? [preferences.generalDislikes] : []
});

export const useChat = () => {
  const [session, setSession] = useState<ChatSession>({
    sessionId: null,
    messages: [],
    isStarted: false,
    isLoading: false
  });

  const startChat = useCallback(async (preferences: UserPreferences) => {
    setSession(prev => ({ ...prev, isLoading: true }));
    try {
      const response = await fetch('/api/chat/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences: transformPreferencesForBackend(preferences) })
      });
      let sessionId;
      if (response.ok) {
        const data = await response.json();
        sessionId = data.session_id || data.sessionId || data.message; // prefer session_id
      } else {
        sessionId = 'demo-session-' + Date.now();
      }
      // Add preferences summary as first message in chat
      const summary = generatePreferenceSummary(preferences);
      setSession(prev => ({
        ...prev,
        sessionId,
        isStarted: true,
        isLoading: false,
        messages: [
          {
            id: Date.now().toString(),
            type: 'assistant',
            content:
              `👋 Welcome to Servio! I'm here to help you find the perfect meal tailored to your preferences.\n\n` +
              `Here's what you've shared with me:\n` +
              summary.split('. ').map(part => `• ${part}`).join('\n') +
              `\n\nLet me know what you're in the mood for, or ask for a recommendation!`,
            timestamp: new Date()
          }
        ]
      }));
    } catch (error) {
      console.log('Starting demo session...');
      const sessionId = 'demo-session-' + Date.now();
      const summary = generatePreferenceSummary(preferences);
      setSession(prev => ({
        ...prev,
        sessionId,
        isStarted: true,
        isLoading: false,
        messages: [
          {
            id: Date.now().toString(),
            type: 'assistant',
            content:
              `👋 Welcome to Servio! I'm here to help you find the perfect meal tailored to your preferences.\n\n` +
              `Here's what you've shared with me:\n` +
              summary.split('. ').map(part => `• ${part}`).join('\n') +
              `\n\nLet me know what you're in the mood for, or ask for a recommendation!`,
            timestamp: new Date()
          }
        ]
      }));
    }
  }, []);

  const sendMessage = useCallback(async (sessionId: string, content: string, preferences?: UserPreferences) => {
    if (!sessionId) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };

    setSession(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true
    }));

    try {
      const response = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: content,
          preferences: preferences ? transformPreferencesForBackend(preferences) : undefined
        })
      });

      let assistantContent;
      
      if (response.ok) {
        const data = await response.json();
        assistantContent = data.message;
      } else {
        // Remove default welcome message
        return;
      }

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: assistantContent,
        timestamp: new Date()
      };

      setSession(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false
      }));
    } catch (error) {
      // Remove default fallback message
      setSession(prev => ({
        ...prev,
        isLoading: false
      }));
    }
  }, [session.sessionId]);

  // Helper to generate preferences summary
  function generatePreferenceSummary(prefs: UserPreferences) {
    const parts = [];
    if (prefs.dietaryRestrictions.length > 0) {
      parts.push(`Dietary: ${prefs.dietaryRestrictions.join(', ')}`);
    }
    if (prefs.allergies.length > 0) {
      parts.push(`Allergies: ${prefs.allergies.join(', ')}`);
    }
    if (prefs.favoriteCuisines.length > 0) {
      parts.push(`Favorite cuisines: ${prefs.favoriteCuisines.join(', ')}`);
    }
    parts.push(`Price range: $${prefs.priceRange[0]}-$${prefs.priceRange[1]}`);
    parts.push(`Spice level: ${prefs.spicePreference}/5`);
    if (prefs.dislikedIngredients.length > 0) {
      parts.push(`Dislikes: ${prefs.dislikedIngredients.slice(0, 3).join(', ')}${prefs.dislikedIngredients.length > 3 ? '...' : ''}`);
    }
    return parts.join('. ');
  }

  return {
    session,
    startChat,
    sendMessage
  };
};