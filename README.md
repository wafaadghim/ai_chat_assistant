# AI Chat Assistant - Module Odoo

## 🤖 Description
Assistant de chat intelligent spécialisé en marketing pour Odoo avec interface de type Messenger et intelligence artificielle intégrée.

## ✨ Fonctionnalités Principales

### 🎯 Chat Intelligent
- **Interface Messenger** : Bulle de chat moderne en bas à droite avec couleurs Odoo
- **Support multilingue** : Arabe, Français, Anglais
- **Messages de bienvenue personnalisés** selon la langue détectée
- **Réponses intelligentes** basées sur une base de connaissances
- **Indicateurs de frappe** animés

### 🧠 Intelligence Artificielle
- **Recommandations automatiques** basées sur les données de campagnes
- **Analyse des performances** en temps réel
- **Suggestions d'optimisation** personnalisées
- **Classification automatique** des questions (marketing, campagne, analytics)
- **Détection de langue** automatique

### 📊 Analytics Marketing
- **Intégration avec les campagnes** de mass mailing
- **Métriques en temps réel** : taux d'ouverture, taux de réponse
- **Recommandations AI** comme :
  - "Arrête la campagne X - coût élevé, faible retour"
  - "Augmente le budget Instagram - taux de conversion +35%"
- **Dashboard intelligent** avec insights marketing

### 🎨 Interface Utilisateur
- **Design Messenger moderne** avec animations fluides
- **Couleurs Odoo** : #714B67, #875A7B, #F0EEEE
- **Avatar du bot** et de l'utilisateur
- **Suggestions rapides** interactives
- **Actions rapides** contextuelles
- **Responsive design**

## 🚀 Installation

### Prérequis
```bash
- Odoo 16.0+
- Modules : base, web, mail, mass_mailing
```

### Étapes d'installation
1. Copier le module dans le répertoire des addons Odoo
2. Redémarrer le serveur Odoo
3. Activer le mode développeur
4. Aller dans Apps → Rechercher "AI Chat Assistant"
5. Installer le module

## 📋 Configuration

### 1. Base de Connaissances
Aller dans **AI Chat Assistant > Base de Connaissances** pour :
- Ajouter des questions/réponses personnalisées
- Configurer les mots-clés de déclenchement  
- Définir les actions rapides
- Gérer les réponses multilingues

### 2. Questions/Réponses Prédéfinies

#### 🇸🇦 En Arabe
- **Salutations** : مرحبا، أهلا، سلام
- **Analyse marketing** : ما أفضل قناة إعلانية هذا الشهر؟
- **Recommandations AI** : توصيات الذكاء الاصطناعي
- **Rapports** : اعطني تقرير الحملات الأقل أداء

#### 🇫🇷 En Français  
- **Salutations** : bonjour, salut, bonsoir
- **Analyse marketing** : analyse marketing, performance campagne
- **Optimisation** : recommandations, suggestions d'amélioration

#### 🇺🇸 En Anglais
- **Greetings** : hello, hi, good morning
- **Marketing** : best advertising channel, campaign performance
- **Analytics** : marketing ROI, conversion analysis

## 🔧 API Endpoints

### Endpoints Principaux
```javascript
POST /ai_chat/process
- Traite les messages du chatbot
- Paramètres: {message: string, session_id: int}

GET /ai_chat/marketing/insights  
- Récupère les insights marketing en temps réel

POST /ai_chat/quick_action
- Exécute les actions rapides
- Paramètres: {action: string}

POST /ai_chat/session/create
- Crée une nouvelle session de chat
```

### Exemples d'utilisation
```javascript
// Envoyer un message
odoo.session.rpc('/ai_chat/process', {
    message: "ما أفضل قناة إعلانية؟",
    session_id: 123
});

// Obtenir les insights
odoo.session.rpc('/ai_chat/marketing/insights', {});

// Exécuter une action rapide
odoo.session.rpc('/ai_chat/quick_action', {
    action: 'marketing_overview'
});
```

## 📊 Modèles de Données

### AIKnowledgeBase
```python
- question (Text): Question ou mots-clés déclencheurs
- response (Text): Réponse du chatbot
- language (Selection): ar/fr/en/multi
- category (Selection): greeting/marketing/analytics/recommendations
- keywords (Text): Mots-clés séparés par virgules
- priority (Integer): Priorité de correspondance
- requires_data (Boolean): Nécessite données temps réel
- quick_actions (Text): Actions rapides en JSON
```

### AIChatSession
```python
- name (Char): Nom de la session
- user_id (Many2one): Utilisateur
- message_count (Integer): Nombre de messages
- last_activity (Datetime): Dernière activité
- satisfaction_rating (Selection): Note de satisfaction
```

### AIChatMessage
```python
- session_id (Many2one): Session de chat
- message (Text): Message utilisateur
- response (Text): Réponse IA
- message_type (Selection): user/assistant/system
- content_category (Selection): Catégorie du contenu
- language_detected (Selection): Langue détectée
- marketing_insight (Text): Insight marketing extrait
```

## 🎨 Personnalisation CSS

### Variables CSS Odoo
```css
:root {
    --odoo-primary: #714B67;
    --odoo-secondary: #875A7B;
    --odoo-light: #F0EEEE;
    --odoo-white: #FFFFFF;
    --odoo-gray: #6C757D;
}
```

### Classes Principales
```css
.chat-launcher        /* Bulle de lancement */
.chat-widget         /* Widget principal */
.chat-header         /* En-tête avec avatar */
.chat-messages       /* Zone des messages */
.chat-bubble         /* Bulle de message */
.typing-indicator    /* Indicateur de frappe */
.quick-suggestions   /* Suggestions rapides */
```

## 🚀 Fonctionnalités Avancées

### 1. Recommandations AI Intelligentes
```python
# Exemple de recommandations générées
recommendations = [
    {
        'type': 'warning',
        'message': "📉 Campagne 'Summer Sale' - Taux d'ouverture faible (12%). Améliorer l'objet.",
        'action': 'improve_subject'
    },
    {
        'type': 'success', 
        'message': "🎯 Campagne 'Newsletter' - Excellent taux (38%). Répliquer cette stratégie!",
        'action': 'replicate_strategy'
    }
]
```

### 2. Analytics en Temps Réel
```python
# Métriques calculées automatiquement
insights = {
    'total_campaigns': 15,
    'avg_open_rate': 24.5,
    'avg_reply_rate': 8.2,
    'total_sent': 50000,
    'total_opened': 12250,
    'total_replied': 4100
}
```

### 3. Actions Rapides Contextuelles
```json
[
    {"text": "عرض الحملات النشطة", "action": "view_active_campaigns"},
    {"text": "تحليل أداء التسويق", "action": "analyze_marketing_performance"},
    {"text": "مقترحات تحسين", "action": "get_improvement_suggestions"}
]
```

## 📱 Interface Mobile
- **Responsive design** adapté aux mobiles
- **Taille optimisée** : 95% de la largeur sur mobile
- **Interactions tactiles** optimisées
- **Animation fluides** sur tous les appareils

## 🔒 Sécurité
- **Authentification utilisateur** requise
- **Permissions par rôle** : utilisateurs/administrateurs
- **Validation des entrées** côté serveur
- **Protection XSS** sur les réponses HTML

## 🐛 Dépannage

### Problèmes courants
1. **Le chatbot n'apparaît pas**
   - Vérifier que le module est installé
   - Contrôler les erreurs JavaScript en console
   - Vider le cache du navigateur

2. **Erreurs API**
   - Vérifier les logs Odoo
   - Contrôler les permissions utilisateur
   - Tester les endpoints manuellement

3. **Réponses manquantes**
   - Vérifier la base de connaissances
   - Contrôler la correspondance des mots-clés
   - Ajuster les priorités

## 📈 Développement Futur

### Fonctionnalités Prévues
- **Intégration GPT** pour des réponses plus naturelles
- **Analyse sentiment** des messages
- **Notifications push** pour les insights critiques
- **Rapports automatisés** programmés
- **Intégration CRM** pour le lead scoring
- **Chatbot vocal** avec reconnaissance vocale

## 🤝 Contribution
Pour contribuer au projet :
1. Fork le repository
2. Créer une branche feature
3. Committer les changements  
4. Soumettre une pull request

## 📄 Licence
Ce module est sous licence LGPL-3.

## 🆘 Support
Pour obtenir de l'aide :
- Créer un issue sur GitHub
- Contacter l'équipe de développement
- Consulter la documentation Odoo

---

**Développé avec ❤️ pour améliorer l'expérience marketing dans Odoo**