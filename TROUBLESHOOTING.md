# 🔧 Guide de Résolution - Erreur RPC 404: ai.chat.message

## ❌ Problème Identifié
```
RPC_ERROR: 404: Not Found
KeyError: 'ai.chat.message'
```

## ✅ Solutions Appliquées

### 1. **Correction des Imports de Modèles**
- ✅ Consolidé tous les modèles dans `ai_knowledge_base.py`
- ✅ Simplifié `models/__init__.py`
- ✅ Corrigé les imports manquants dans le contrôleur

### 2. **Correction des Dépendances**
- ✅ Supprimé les dépendances optionnelles (`mass_mailing`, `marketing_automation`, `utm`)
- ✅ Gardé seulement les dépendances essentielles : `base`, `web`, `mail`
- ✅ Ajouté la gestion conditionnelle pour les modules optionnels

### 3. **Correction des Droits d'Accès**
- ✅ Nettoyé le fichier `ir.model.access.csv`
- ✅ Supprimé les duplications
- ✅ Défini les permissions correctes pour tous les modèles

### 4. **Correction du Contrôleur**
- ✅ Ajouté l'import manquant `fields` et `datetime`
- ✅ Corrigé `fields.Datetime.now()` → `datetime.now()`
- ✅ Ajouté la gestion d'erreurs robuste

## 🚀 Étapes de Résolution

### Étape 1: Désinstaller le Module (si déjà installé)
1. Aller dans **Apps**
2. Rechercher "AI Chat Assistant" 
3. **Désinstaller** complètement
4. **Redémarrer Odoo**

### Étape 2: Réinstaller le Module
1. **Redémarrer le serveur Odoo**
   ```bash
   # Si service système
   sudo systemctl restart odoo
   
   # Ou redémarrage manuel
   cd /home/wafa/Documents/odoo
   ./odoo-bin --addons-path=addons,custom --dev=all
   ```

2. **Mettre à jour la liste des applications**
   - Apps → "Update Apps List"

3. **Installer le module**
   - Rechercher "AI Chat Assistant"
   - Cliquer "Install"

### Étape 3: Vérification Post-Installation
1. **Vérifier les modèles créés**
   - Aller dans **Settings → Technical → Database Structure → Models**
   - Rechercher : `ai.knowledge.base`, `ai.chat.session`, `ai.chat.message`

2. **Tester l'API**
   - Ouvrir la console du navigateur (F12)
   - Tester :
   ```javascript
   odoo.session.rpc('/ai_chat/process', 'call', {
       message: "Hello test",
       session_id: null
   }).then(console.log);
   ```

3. **Vérifier le chatbot**
   - La bulle 🤖 doit apparaître en bas à droite
   - Cliquer dessus pour ouvrir le chat
   - Taper un message de test

## 🔍 Diagnostic Avancé

### Si l'erreur persiste:

1. **Vérifier les logs Odoo**
   ```bash
   # Voir les derniers logs
   tail -f /var/log/odoo/odoo-server.log
   
   # Ou dans le terminal Odoo directement
   ```

2. **Vérifier la base de données**
   ```sql
   -- Se connecter à PostgreSQL
   sudo -u postgres psql your_database_name
   
   -- Vérifier que les tables existent
   \dt ai_*
   
   -- Vérifier les modèles Odoo
   SELECT name, model FROM ir_model WHERE model LIKE 'ai.%';
   ```

3. **Mode Debug Odoo**
   - Activer le mode développeur
   - Aller dans **Settings → Technical → Server Actions**
   - Exécuter : "Update Module List"

## 📋 Checklist de Vérification

- [ ] Module correctement placé dans `/custom/ai_chat_assistant/`
- [ ] Serveur Odoo redémarré
- [ ] Module désinstallé puis réinstallé
- [ ] Aucune erreur dans les logs Odoo
- [ ] Models `ai.*` présents dans la base de données
- [ ] API endpoints accessibles 
- [ ] Cache navigateur vidé
- [ ] Bulle de chat visible en bas à droite

## 🎯 Test Final

Après installation, tester ces commandes dans la console du navigateur :

```javascript
// Test 1: Vérifier que les modèles existent
console.log("Testing models availability...");

// Test 2: Test création de session
odoo.session.rpc('/ai_chat/session/create', 'call', {})
    .then(result => console.log("✅ Session API OK:", result))
    .catch(error => console.log("❌ Session API Error:", error));

// Test 3: Test traitement de message
odoo.session.rpc('/ai_chat/process', 'call', {
    message: "Hello AI Assistant", 
    session_id: null
}).then(result => console.log("✅ Process API OK:", result))
  .catch(error => console.log("❌ Process API Error:", error));

// Test 4: Test insights marketing
odoo.session.rpc('/ai_chat/marketing/insights', 'call', {})
    .then(result => console.log("✅ Insights API OK:", result))
    .catch(error => console.log("❌ Insights API Error:", error));
```

## 🆘 Support Supplémentaire

Si le problème persiste après ces étapes :

1. **Vérifier la version d'Odoo** (compatible avec 16.0+)
2. **Vérifier les permissions de fichiers**
3. **Tester avec une base de données fraîche**
4. **Activer le mode `--dev=all` pour plus de logs**

---

**Status**: ✅ Module prêt pour installation après corrections appliquées.