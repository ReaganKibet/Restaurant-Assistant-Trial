import React, { useState, useRef, useEffect } from 'react';
import { ChatSession, UserPreferences } from '../types';
import { Send, MessageCircle, Bot, User, Loader } from 'lucide-react';


interface ChatInterfaceProps {
  session: ChatSession;
  preferences: UserPreferences;
  onSendMessage: (message: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  session,
  preferences,
  onSendMessage
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session.messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !session.isLoading) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden h-full flex flex-col">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-500 p-4 text-white">
        <div className="flex items-center space-x-3">
          <div className="bg-white bg-opacity-20 rounded-full p-2">
            <MessageCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Restaurant Assistant</h3>
            <p className="text-amber-100 text-sm">
              {session.isStarted ? 'Ready to help with recommendations' : 'Start a conversation to get personalized recommendations'}
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 min-h-0">
        {!session.isStarted ? (
          <div className="text-center py-8">
            <div className="bg-white rounded-full p-4 w-16 h-16 mx-auto mb-4 shadow-md">
              <Bot className="w-8 h-8 text-amber-600 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Welcome to our Restaurant Assistant!</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              I'll help you find the perfect meal based on your preferences. Let's start by reviewing your preferences and then we can chat!
            </p>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 max-w-md mx-auto">
              <p className="text-amber-800 text-sm">
                💡 <strong>Tip:</strong> Make sure to submit your preferences using the button in the preferences panel before starting the chat for the best recommendations!
              </p>
            </div>
            <div className="text-gray-500 text-sm italic">
              Chat will start automatically when you submit your preferences
            </div>
          </div>
        ) : (
          <>
            {session.messages.length === 0 && (
              <div className="text-center py-4">
                <p className="text-gray-500 text-sm">
                  Chat started! Ask me anything about our menu or for recommendations.
                </p>
              </div>
            )}
            
            {session.messages.map(message => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-amber-500 text-white' 
                    : 'bg-blue-500 text-white'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                
                <div className={`flex-1 max-w-[80%] ${
                  message.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  <div className={`inline-block p-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-amber-500 text-white rounded-br-sm'
                      : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
                  }`}>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>
                  <div className={`text-xs text-gray-500 mt-1 ${
                    message.type === 'user' ? 'text-right' : 'text-left'
                  }`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            
            {session.isLoading && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-gray-200 rounded-lg rounded-bl-sm shadow-sm p-3">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-xs text-gray-500">Assistant is typing...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Message Input */}
      {session.isStarted && (
        <div className="border-t border-gray-200 p-4 bg-white">
          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about menu items, get recommendations..."
              disabled={session.isLoading}
              className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || session.isLoading}
              className={`px-4 py-2 rounded-lg transition-colors ${
                !inputMessage.trim() || session.isLoading
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-amber-600 text-white hover:bg-amber-700'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;