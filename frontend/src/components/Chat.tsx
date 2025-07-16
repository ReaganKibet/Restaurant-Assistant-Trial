import React, { useState, useRef, useEffect } from "react";
import { Preferences } from "./Preferences";
import { MenuSection } from "./MenuSection";
import allergiesData from "../data/allergy.json";
import ingredientsData from "../data/ingredients.json";
import { Box, Button, Paper, Typography, Divider } from "@mui/material";

// Extract string arrays for preferences UI
const allergiesList = allergiesData.common_allergens || [];
const ingredientsList = Array.isArray(ingredientsData.ingredients)
  ? ingredientsData.ingredients.map((i: any) => i.name)
  : [];

type Message = {
  text: string;
  sender: "user" | "assistant";
};

const cuisinesList = ["Italian", "Mexican", "Indian", "Chinese", "American"];
const mealTypesList = ["appetizer", "main course", "dessert", "side"];
const dietaryRestrictionsList = ["vegetarian", "vegan", "gluten_free", "dairy_free"];

const defaultPreferences = {
  dietary_restrictions: ["vegetarian"],
  allergies: ["peanuts", "shellfish"],
  price_range: [10, 30],
  favorite_cuisines: ["Italian", "Mexican"],
  disliked_ingredients: [],
  spice_preference: 2,
  preferred_meal_types: [],
  dislikes: []
};

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState(defaultPreferences);
  const [chatStarted, setChatStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;
    const userMsg = { text: input, sender: "user" as const };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");

    try {
      const res = await fetch("/api/chat/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
          preferences
        })
      });
      const data = await res.json();
      if (data.message) setMessages((msgs) => [...msgs, { text: data.message, sender: "assistant" }]);
      if (data.follow_up_questions) {
        data.follow_up_questions.forEach((q: string) =>
          setMessages((msgs) => [...msgs, { text: "💡 " + q, sender: "assistant" }])
        );
      }
      if (data.session_id) setSessionId(data.session_id);
    } catch {
      setMessages((msgs) => [...msgs, { text: "Sorry, there was a problem contacting the assistant.", sender: "assistant" }]);
    }
  };

  const API_BASE_URL = import.meta.env.VITE_API_URL;

  const startChat = async () => {
    setMessages([
      { text: "👋 Hi! I'm your restaurant assistant. How can I help you today?", sender: "assistant" }
    ]);
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/chat/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preferences })
      });
      const data = await res.json();
      if (data.session_id) setSessionId(data.session_id);
      if (data.message) setMessages(msgs => [...msgs, { text: data.message, sender: "assistant" }]);
      setChatStarted(true);
    } catch {
      setMessages(msgs => [...msgs, { text: "Sorry, could not start a chat session.", sender: "assistant" }]);
    }
  };

  return (
    <Box sx={{ display: { md: 'flex' }, gap: 3, alignItems: 'flex-start', mt: 3 }}>
      {/* Preferences Section */}
      <Box sx={{ flex: 1, minWidth: 320 }}>
        <Preferences
          preferences={preferences}
          setPreferences={setPreferences}
          allergiesList={allergiesList}
          ingredientsList={ingredientsList}
          cuisinesList={cuisinesList}
          mealTypesList={mealTypesList}
          dietaryRestrictionsList={dietaryRestrictionsList}
        />
      </Box>
      {/* Divider for desktop */}
      <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
      {/* Menu Section */}
      <Box sx={{ flex: 2, minWidth: 350 }}>
        <MenuSection preferences={preferences} />
        {/* Chat UI below menu */}
        <Paper sx={{ mt: 3, p: 2 }}>
          <Typography variant="h6">Chat</Typography>
          <Box sx={{ maxHeight: 240, overflowY: 'auto', mb: 2 }}>
            {messages.map((msg, idx) => (
              <Box key={idx} sx={{ my: 1, textAlign: msg.sender === "user" ? "right" : "left" }}>
                <Typography
                  variant="body2"
                  sx={{
                    display: "inline-block",
                    px: 2,
                    py: 1,
                    borderRadius: 2,
                    bgcolor: msg.sender === "user" ? "primary.light" : "grey.200"
                  }}
                >
                  {msg.text}
                </Typography>
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </Box>
          <form onSubmit={e => { e.preventDefault(); if (chatStarted) sendMessage(e); else startChat(); }} style={{ display: 'flex', gap: 8 }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder={chatStarted ? "Type your message..." : "Start chatting..."}
              style={{ flex: 1, padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
              disabled={!chatStarted && !!input}
            />
            <Button variant="contained" type="submit">
              {chatStarted ? "Send" : "Start Chat"}
            </Button>
          </form>
        </Paper>
      </Box>
    </Box>
  );
};