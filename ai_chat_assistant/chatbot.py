"""
ChatBot module - Main chatbot logic and AI interaction.
"""

import re
from typing import List, Dict, Optional
from datetime import datetime


class ChatBot:
    """
    A simple AI Chat Assistant that can handle basic conversations.
    """
    
    def __init__(self, name: str = "Assistant"):
        """
        Initialize the chatbot.
        
        Args:
            name: The name of the chatbot
        """
        self.name = name
        self.conversation_history: List[Dict[str, str]] = []
        self.patterns = {
            r'\b(bonjour|salut|hello|hi)\b': self._greet,
            r'\b(comment (ça va|vas-tu)|how are you)\b': self._status,
            r'\b(au revoir|bye|goodbye)\b': self._farewell,
            r'\b(merci|thank you|thanks)\b': self._thank,
            r'\b(aide|help)\b': self._help,
            r'\b(nom|name)\b': self._name,
            r'\b(heure|time)\b': self._time,
            r'\b(date)\b': self._date,
        }
    
    def _greet(self, message: str) -> str:
        """Generate a greeting response."""
        return f"Bonjour! Je suis {self.name}. Comment puis-je vous aider aujourd'hui?"
    
    def _status(self, message: str) -> str:
        """Generate a status response."""
        return "Je vais très bien, merci! Prêt à vous assister."
    
    def _farewell(self, message: str) -> str:
        """Generate a farewell response."""
        return "Au revoir! N'hésitez pas à revenir si vous avez besoin d'aide."
    
    def _thank(self, message: str) -> str:
        """Generate a thank you response."""
        return "De rien! Je suis là pour vous aider."
    
    def _help(self, message: str) -> str:
        """Generate a help response."""
        return ("Je peux vous aider avec plusieurs choses:\n"
                "- Conversations simples\n"
                "- Vous donner l'heure et la date\n"
                "- Répondre à vos questions\n"
                "Posez-moi simplement votre question!")
    
    def _name(self, message: str) -> str:
        """Generate a name response."""
        return f"Je m'appelle {self.name}. Enchanté!"
    
    def _time(self, message: str) -> str:
        """Generate a time response."""
        current_time = datetime.now().strftime("%H:%M:%S")
        return f"Il est actuellement {current_time}."
    
    def _date(self, message: str) -> str:
        """Generate a date response."""
        current_date = datetime.now().strftime("%d/%m/%Y")
        return f"Nous sommes le {current_date}."
    
    def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message
            
        Returns:
            The chatbot's response
        """
        message_lower = message.lower()
        
        # Store the message in conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": message,
            "bot": None
        })
        
        # Try to match patterns
        for pattern, handler in self.patterns.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                response = handler(message)
                self.conversation_history[-1]["bot"] = response
                return response
        
        # Default response if no pattern matches
        response = "Je comprends votre message. Pouvez-vous me donner plus de détails?"
        self.conversation_history[-1]["bot"] = response
        return response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of conversation exchanges
        """
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
