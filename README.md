# AI Chat Assistant

Un assistant de chat IA simple et interactif en français.

## Description

AI Chat Assistant est une application de chatbot conversationnel qui peut:
- Répondre aux salutations et aux questions courantes
- Fournir l'heure et la date actuelles
- Gérer l'historique des conversations
- Sauvegarder les conversations pour référence future

## Installation

### Prérequis

- Python 3.7 ou supérieur

### Étapes d'installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/wafaadghim/ai_chat_assistant.git
cd ai_chat_assistant
```

2. (Optionnel) Créez un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances:
```bash
pip install -r requirements.txt
```

## Utilisation

### Mode interactif (CLI)

Pour démarrer le chatbot en mode interactif:

```bash
python -m ai_chat_assistant.main
```

Ou:

```bash
python ai_chat_assistant/main.py
```

### Commandes disponibles

- **quit / exit / quitter**: Quitter l'application
- **history**: Afficher l'historique de la conversation
- **clear**: Effacer l'historique de la conversation

### Exemples d'utilisation

Vous pouvez exécuter les exemples fournis pour voir le chatbot en action:

```bash
python examples.py
```

### Utilisation dans votre code

Vous pouvez également utiliser le chatbot dans votre propre code Python:

```python
from ai_chat_assistant import ChatBot, Conversation

# Créer une instance du chatbot
bot = ChatBot(name="Mon Assistant")

# Traiter un message
response = bot.process_message("Bonjour!")
print(response)

# Gérer les conversations
conversation = Conversation()
conversation.save_conversation(bot.get_conversation_history())
```

## Fonctionnalités

- **Reconnaissance de patterns**: Détecte et répond à différents types de messages
- **Historique**: Garde une trace de toutes les conversations
- **Sauvegarde**: Sauvegarde automatique des conversations
- **Multilingue**: Supporte le français et l'anglais
- **Extensible**: Architecture modulaire facile à étendre

## Structure du projet

```
ai_chat_assistant/
├── __init__.py          # Module principal
├── chatbot.py           # Logique du chatbot
├── conversation.py      # Gestion des conversations
└── main.py             # Interface CLI
```

## Exemples d'interactions

```
Vous: Bonjour
Assistant IA: Bonjour! Je suis Assistant IA. Comment puis-je vous aider aujourd'hui?

Vous: Quelle heure est-il?
Assistant IA: Il est actuellement 14:30:45.

Vous: Merci
Assistant IA: De rien! Je suis là pour vous aider.
```

## Développement

Pour contribuer au projet:

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Tests

Pour exécuter les tests:

```bash
python -m pytest tests/
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Auteur

- **Wafaa Dghim** - [wafaadghim](https://github.com/wafaadghim)

## Remerciements

- Merci à tous les contributeurs qui ont participé à ce projet
- Inspiré par les assistants conversationnels modernes
