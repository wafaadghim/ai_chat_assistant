"""
Main module - Command-line interface for the AI Chat Assistant.
"""

import sys
from .chatbot import ChatBot
from .conversation import Conversation


def main():
    """
    Main function to run the AI Chat Assistant CLI.
    """
    print("=" * 50)
    print("AI Chat Assistant")
    print("=" * 50)
    print("Tapez 'quit' ou 'exit' pour quitter")
    print("Tapez 'history' pour voir l'historique")
    print("Tapez 'clear' pour effacer l'historique")
    print("=" * 50)
    print()
    
    chatbot = ChatBot(name="Assistant IA")
    conversation = Conversation()
    
    try:
        while True:
            user_input = input("Vous: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'quitter']:
                print(f"\n{chatbot.name}: Au revoir!")
                # Save conversation before exiting
                if chatbot.conversation_history:
                    conversation.save_conversation(chatbot.conversation_history)
                    print("Conversation sauvegardée.")
                break
            
            if user_input.lower() == 'history':
                history = chatbot.get_conversation_history()
                if history:
                    print("\n--- Historique de la conversation ---")
                    for exchange in history:
                        print(f"Vous: {exchange['user']}")
                        print(f"{chatbot.name}: {exchange['bot']}")
                        print()
                else:
                    print("Aucun historique disponible.")
                continue
            
            if user_input.lower() == 'clear':
                chatbot.clear_history()
                print("Historique effacé.")
                continue
            
            response = chatbot.process_message(user_input)
            print(f"{chatbot.name}: {response}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{chatbot.name}: Au revoir!")
        if chatbot.conversation_history:
            conversation.save_conversation(chatbot.conversation_history)
            print("Conversation sauvegardée.")
    except Exception as e:
        print(f"\nErreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
