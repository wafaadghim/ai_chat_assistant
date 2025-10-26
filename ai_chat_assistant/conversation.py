"""
Conversation module - Handles conversation management and storage.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class Conversation:
    """
    Manages conversation storage and retrieval.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize conversation manager.
        
        Args:
            storage_path: Path to store conversations (optional)
        """
        self.storage_path = Path(storage_path) if storage_path else Path("conversations.json")
        self.conversations: List[Dict] = self._load_conversations()
    
    def _load_conversations(self) -> List[Dict]:
        """Load conversations from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_conversation(self, conversation_data: List[Dict[str, str]]) -> None:
        """
        Save a conversation to storage.
        
        Args:
            conversation_data: List of conversation exchanges
        """
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "messages": conversation_data
        }
        self.conversations.append(conversation)
        self._save_to_file()
    
    def _save_to_file(self) -> None:
        """Save all conversations to file."""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
    
    def get_all_conversations(self) -> List[Dict]:
        """
        Get all stored conversations.
        
        Returns:
            List of all conversations
        """
        return self.conversations
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Get recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        return self.conversations[-limit:]
    
    def clear_all(self) -> None:
        """Clear all stored conversations."""
        self.conversations.clear()
        if self.storage_path.exists():
            self.storage_path.unlink()
