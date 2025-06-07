from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger
import json
from datetime import datetime

from app.models.schemas import MenuItem
from app.services.menu_service import MenuService
from app.config import settings

class RAGService:
    def __init__(self, menu_service: MenuService):
        self.menu_service = menu_service
        self.menu_embeddings = self._load_menu_embeddings()
        self.qa_pairs = self._load_qa_pairs()

    def _load_menu_embeddings(self) -> Dict[str, List[float]]:
        """Load pre-computed menu item embeddings"""
        try:
            with open("data/menu_embeddings.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading menu embeddings: {str(e)}")
            return {}

    def _load_qa_pairs(self) -> List[Dict[str, Any]]:
        """Load pre-defined Q&A pairs"""
        try:
            with open("data/qa_pairs.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading Q&A pairs: {str(e)}")
            return []

    def _compute_similarity(
        self,
        query_embedding: List[float],
        item_embedding: List[float]
    ) -> float:
        """Compute cosine similarity between query and item embeddings"""
        try:
            query_norm = np.linalg.norm(query_embedding)
            item_norm = np.linalg.norm(item_embedding)
            if query_norm == 0 or item_norm == 0:
                return 0
            return np.dot(query_embedding, item_embedding) / (query_norm * item_norm)
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0

    async def get_menu_qa(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get answer to a question about the menu"""
        try:
            # First, check if there's a direct match in Q&A pairs
            for qa_pair in self.qa_pairs:
                if self._compute_similarity(
                    self._get_embedding(question),
                    self._get_embedding(qa_pair["question"])
                ) > 0.8:  # High similarity threshold
                    return {
                        "answer": qa_pair["answer"],
                        "confidence": 1.0,
                        "source": "qa_pairs"
                    }

            # If no direct match, search through menu items
            relevant_items = []
            for item_id, embedding in self.menu_embeddings.items():
                similarity = self._compute_similarity(
                    self._get_embedding(question),
                    embedding
                )
                if similarity > 0.5:  # Lower threshold for menu items
                    item = self.menu_service.get_menu_item_by_id(item_id)
                    if item:
                        relevant_items.append((item, similarity))

            # Sort by similarity
            relevant_items.sort(key=lambda x: x[1], reverse=True)

            if not relevant_items:
                return {
                    "answer": "I'm sorry, I couldn't find any relevant information about that in our menu.",
                    "confidence": 0.0,
                    "source": "menu"
                }

            # Generate answer based on most relevant items
            top_item, confidence = relevant_items[0]
            answer = self._generate_answer(question, top_item, context)

            return {
                "answer": answer,
                "confidence": confidence,
                "source": "menu",
                "relevant_items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "similarity": sim
                    }
                    for item, sim in relevant_items[:3]
                ]
            }

        except Exception as e:
            logger.error(f"Error in menu Q&A: {str(e)}")
            return {
                "answer": "I apologize, but I'm having trouble processing your question right now.",
                "confidence": 0.0,
                "source": "error"
            }

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text (placeholder - would use actual embedding model)"""
        # This is a placeholder - in a real implementation, you would use
        # a proper embedding model like sentence-transformers
        return [0.0] * 384  # Example dimension

    def _generate_answer(
        self,
        question: str,
        item: MenuItem,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a natural language answer based on menu item"""
        # This is a simple implementation - could be enhanced with LLM
        question = question.lower()
        
        if "price" in question:
            return f"The {item.name} costs ${item.price:.2f}."
        
        elif "ingredient" in question:
            return f"The {item.name} contains: {', '.join(item.ingredients)}."
        
        elif "allergen" in question or "allergy" in question:
            if item.allergens:
                return f"The {item.name} contains the following allergens: {', '.join(item.allergens)}."
            return f"The {item.name} doesn't contain any common allergens."
        
        elif "spice" in question or "hot" in question:
            return f"The {item.name} has a spice level of {item.spice_level}/5."
        
        elif "time" in question or "long" in question:
            return f"The {item.name} takes approximately {item.preparation_time} minutes to prepare."
        
        elif "vegetarian" in question:
            if item.is_vegetarian:
                return f"Yes, the {item.name} is vegetarian."
            return f"No, the {item.name} is not vegetarian."
        
        elif "vegan" in question:
            if item.is_vegan:
                return f"Yes, the {item.name} is vegan."
            return f"No, the {item.name} is not vegan."
        
        elif "gluten" in question:
            if item.is_gluten_free:
                return f"Yes, the {item.name} is gluten-free."
            return f"No, the {item.name} is not gluten-free."
        
        elif "dairy" in question:
            if item.is_dairy_free:
                return f"Yes, the {item.name} is dairy-free."
            return f"No, the {item.name} is not dairy-free."
        
        else:
            return f"The {item.name} is {item.description}"

    async def update_menu_embeddings(self) -> None:
        """Update menu item embeddings"""
        try:
            menu_items = self.menu_service.get_all_menu_items()
            new_embeddings = {}

            for item in menu_items:
                # Generate embedding for item name and description
                item_text = f"{item.name} {item.description}"
                new_embeddings[item.id] = self._get_embedding(item_text)

            # Save updated embeddings
            with open("data/menu_embeddings.json", "w") as f:
                json.dump(new_embeddings, f, indent=2)

            self.menu_embeddings = new_embeddings
            logger.info("Menu embeddings updated successfully")

        except Exception as e:
            logger.error(f"Error updating menu embeddings: {str(e)}")
            raise

    async def add_qa_pair(
        self,
        question: str,
        answer: str,
        category: Optional[str] = None
    ) -> None:
        """Add a new Q&A pair to the knowledge base"""
        try:
            new_pair = {
                "question": question,
                "answer": answer,
                "category": category,
                "created_at": datetime.now().isoformat()
            }

            self.qa_pairs.append(new_pair)

            # Save updated Q&A pairs
            with open("data/qa_pairs.json", "w") as f:
                json.dump(self.qa_pairs, f, indent=2)

            logger.info("Q&A pair added successfully")

        except Exception as e:
            logger.error(f"Error adding Q&A pair: {str(e)}")
            raise 