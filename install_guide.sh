#!/bin/bash

# Script pour redémarrer et réinstaller le module AI Chat Assistant

echo "🔄 Redémarrage et réinstallation du module AI Chat Assistant"

# Variables
MODULE_NAME="ai_chat_assistant"
ODOO_PATH="/home/wafa/Documents/odoo"

echo "📁 Module path: $ODOO_PATH/custom/$MODULE_NAME"

# Étapes de dépannage
echo "
🛠️  ÉTAPES DE DÉPANNAGE:

1. Vérifier que le module est dans le bon répertoire
2. Redémarrer le serveur Odoo 
3. Désinstaller puis réinstaller le module
4. Vider le cache du navigateur
5. Vérifier les logs Odoo

"

echo "📋 COMMANDES UTILES:"
echo ""
echo "# Redémarrer Odoo (si vous utilisez un service)"
echo "sudo systemctl restart odoo"
echo ""
echo "# Ou redémarrer manuellement"
echo "cd $ODOO_PATH"
echo "./odoo-bin --addons-path=addons,custom --dev=all"
echo ""
echo "# Installer le module via CLI"
echo "./odoo-bin -d your_database -i $MODULE_NAME --stop-after-init"
echo ""
echo "# Mettre à jour le module"
echo "./odoo-bin -d your_database -u $MODULE_NAME --stop-after-init"

echo ""
echo "🌐 ACCÈS WEB:"
echo "1. Aller à http://localhost:8069"
echo "2. Se connecter en mode développeur"
echo "3. Apps → Rechercher 'AI Chat Assistant'"
echo "4. Désinstaller puis réinstaller si nécessaire"

echo ""
echo "🔍 VÉRIFICATION DES LOGS:"
echo "Vérifiez les logs Odoo pour toute erreur durant l'installation"
echo "Les modèles suivants doivent être créés:"
echo "- ai.knowledge.base"
echo "- ai.chat.session" 
echo "- ai.chat.message"

echo ""
echo "✅ Module prêt pour l'installation !"