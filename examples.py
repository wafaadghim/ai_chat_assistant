#!/usr/bin/env python
"""
Example usage of the AI Chat Assistant.
"""

from ai_chat_assistant import ChatBot, Conversation


def example_basic_conversation():
    """Example of a basic conversation."""
    print("=" * 60)
    print("Example 1: Basic Conversation")
    print("=" * 60)
    
    bot = ChatBot(name="Assistant")
    
    messages = [
        "Bonjour",
        "Comment vas-tu?",
        "Quelle heure est-il?",
        "Merci",
        "Au revoir"
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        response = bot.process_message(message)
        print(f"Bot: {response}")


def example_conversation_history():
    """Example of using conversation history."""
    print("\n" + "=" * 60)
    print("Example 2: Conversation History")
    print("=" * 60)
    
    bot = ChatBot(name="Assistant")
    
    bot.process_message("Bonjour")
    bot.process_message("Comment ça va?")
    bot.process_message("Merci")
    
    print("\nConversation History:")
    for i, exchange in enumerate(bot.get_conversation_history(), 1):
        print(f"\n{i}. User: {exchange['user']}")
        print(f"   Bot: {exchange['bot']}")
        print(f"   Time: {exchange['timestamp']}")


def example_conversation_storage():
    """Example of saving and loading conversations."""
    print("\n" + "=" * 60)
    print("Example 3: Conversation Storage")
    print("=" * 60)
    
    # Create a conversation manager
    conversation = Conversation(storage_path="/tmp/example_conversations.json")
    
    # Create and save a conversation
    bot = ChatBot(name="Assistant")
    bot.process_message("Bonjour!")
    bot.process_message("Aide-moi")
    
    # Save the conversation
    conversation.save_conversation(bot.get_conversation_history())
    print("\nConversation saved!")
    
    # Load recent conversations
    recent = conversation.get_recent_conversations(limit=1)
    print(f"\nLoaded {len(recent)} recent conversation(s)")
    
    if recent:
        print("\nMost recent conversation:")
        for msg in recent[0]['messages']:
            print(f"  User: {msg['user']}")
            print(f"  Bot: {msg['bot']}")


def example_multilingual():
    """Example of multilingual support."""
    print("\n" + "=" * 60)
    print("Example 4: Multilingual Support")
    print("=" * 60)
    
    bot = ChatBot(name="Multilingual Bot")
    
    messages = [
        ("Bonjour", "French greeting"),
        ("Hello", "English greeting"),
        ("Merci", "French thanks"),
        ("Thank you", "English thanks"),
    ]
    
    for message, description in messages:
        print(f"\nUser ({description}): {message}")
        response = bot.process_message(message)
        print(f"Bot: {response}")


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("AI Chat Assistant - Usage Examples")
    print("*" * 60)
    
    example_basic_conversation()
    example_conversation_history()
    example_conversation_storage()
    example_multilingual()
    
    print("\n" + "*" * 60)
    print("Examples completed!")
    print("*" * 60)
    print()
