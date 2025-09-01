import React from 'react';
import { usePreferences } from '../hooks/usePreferences';
import { useChat } from '../hooks/useChat';
import Preferences from './Preferences';
import MenuSection from './MenuSection';
import ChatInterface from './ChatInterface';

const Chat: React.FC = () => {
  const { preferences, updatePreferences } = usePreferences();
  const { session, startChat, sendMessage } = useChat();
  const [preferencesSubmitted, setPreferencesSubmitted] = React.useState(false);
  const hasInitializedRef = React.useRef(false); // Critical fix: use ref instead of state

  // SINGLE initialization point - ONLY via preferences submission
  const initializeChat = React.useCallback(async () => {
    if (hasInitializedRef.current || session.isStarted) return;
    
    hasInitializedRef.current = true;
    await startChat(preferences);
  }, [preferences, session.isStarted, startChat]);

  const handleSubmitPreferences = async () => {
    setPreferencesSubmitted(true);
    
    // Only initialize if not already started
    if (!session.isStarted) {
      await initializeChat();
    } else {
      const preferenceSummary = generatePreferenceSummary(preferences);
      if (session.sessionId) {
        await sendMessage(session.sessionId, `I've updated my preferences: ${preferenceSummary}`);
      } else {
        console.error('No active session ID');
      }
    }
    
    setTimeout(() => setPreferencesSubmitted(false), 3000);
  };

  const generatePreferenceSummary = (prefs: typeof preferences) => {
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
  };

  const handleSendMessage = async (message: string) => {
    if (!session.sessionId) {
      console.error('No active session ID');
      return;
    }
    
    await sendMessage(session.sessionId, message);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Servio ,Your Digital Dining Companion</h1>
          <p className="text-gray-600 text-lg">Find your perfect meal, tailored to your taste</p>
        </div>

        {/* Debug Info - Remove in production */}
        {import.meta.env.MODE === 'development' && (
          <div className="mb-4 p-2 bg-gray-100 rounded text-sm">
            <p>Session ID: {session.sessionId || 'None'}</p>
            <p>Session Started: {session.isStarted ? 'Yes' : 'No'}</p>
          </div>
        )}

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Preferences Panel - Left Side on Desktop */}
          <div className="lg:col-span-1">
            <Preferences 
              preferences={preferences} 
              onUpdatePreferences={updatePreferences}
              onSubmitPreferences={handleSubmitPreferences}
              isSubmitted={preferencesSubmitted}
            />
          </div>

          {/* Menu and Chat Section - Right Side on Desktop */}
          <div className="lg:col-span-3 space-y-6">
            {/* Menu Section */}
            <MenuSection preferences={preferences} />
            
            {/* Chat Interface */}
            <div className="h-96">
              <ChatInterface
                session={session}
                preferences={preferences}
                onSendMessage={handleSendMessage}
                // CRITICAL: Removed onStartChat to prevent duplicate initialization
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
