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

// Helper function to properly join URLs
const joinURL = (base: string, path: string): string => {
  const cleanBase = base.replace(/\/+$/, ''); // Remove trailing slashes
  const cleanPath = path.replace(/^\/+/, ''); // Remove leading slashes
  return `${cleanBase}/${cleanPath}`;
};

export const useChat = () => {
  const [session, setSession] = useState<ChatSession>({
    sessionId: null,
    messages: [],
    isStarted: false,
    isLoading: false
  });

  // Get API URL from environment variable or fallback to Render URL
  const getApiUrl = (): string => {
    const baseUrl = import.meta.env.VITE_API_URL || 'https://botappetite.onrender.com';
    return baseUrl.replace(/\/+$/, ''); // Remove trailing slashes
  };

  const startChat = useCallback(async (preferences: UserPreferences) => {
    setSession(prev => ({ ...prev, isLoading: true }));
    try {
      const apiUrl = getApiUrl();
      const endpoint = joinURL(apiUrl, 'api/chat/start');
      
      console.log('Starting chat with URL:', endpoint); // Debug log
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences: transformPreferencesForBackend(preferences) })
      });
      
      let sessionId;
      if (response.ok) {
        const data = await response.json();
        sessionId = data.session_id || data.sessionId || data.message;
        console.log('Chat started successfully, session ID:', sessionId);
      } else {
        console.error('Failed to start chat, status:', response.status);
        throw new Error(`Server responded with ${response.status}`);
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
              `Welcome to Servio! I'm here to help you find the perfect meal tailored to your preferences.\n\n` +
              `Here's what you've shared with me:\n` +
              summary.split('. ').map(part => `• ${part}`).join('\n') +
              `\n\nLet me know what you're in the mood for, or ask for a recommendation!`,
            timestamp: new Date()
          }
        ]
      }));
    } catch (error) {
      console.error('Error starting chat:', error);
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
              `Welcome to Servio! I'm here to help you find the perfect meal tailored to your preferences.\n\n` +
              `Here's what you've shared with me:\n` +
              summary.split('. ').map(part => `• ${part}`).join('\n') +
              `\n\n⚠️ Currently running in demo mode. Backend connection unavailable.`,
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
      const apiUrl = getApiUrl();
      const endpoint = joinURL(apiUrl, 'api/chat/message');
      
      console.log('Sending message to URL:', endpoint); // Debug log
      
      const response = await fetch(endpoint, {
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
        console.log('Message sent successfully');
      } else {
        console.error('Failed to send message, status:', response.status);
        throw new Error(`Server responded with ${response.status}`);
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
      console.error('Error sending message:', error);
      // Error fallback
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "I'm having trouble connecting to our servers right now. Please try again in a moment.",
        timestamp: new Date()
      };

      setSession(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false
      }));
    }
  }, []);

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
