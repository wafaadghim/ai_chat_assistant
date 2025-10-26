#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script pour vérifier l'installation du module AI Chat Assistant
"""

import os
import sys

def check_module_structure():
    """Vérifier la structure du module"""
    print("🔍 Vérification de la structure du module AI Chat Assistant...")
    
    base_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant"
    
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py", 
        "models/ai_knowledge_base.py",
        "controllers/__init__.py",
        "controllers/main.py",
        "static/src/js/chatbot.js",
        "static/src/css/chatbot.css",
        "views/chatbot_views.xml",
        "views/chatbot_templates.xml",
        "views/marketing_views.xml",
        "security/ir.model.access.csv",
        "data/ai_responses_data.xml"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} fichiers manquants!")
        return False
    else:
        print("\n🎉 Tous les fichiers requis sont présents!")
        return True

def check_manifest():
    """Vérifier le fichier manifest"""
    print("\n📋 Vérification du manifest...")
    
    try:
        manifest_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant/__manifest__.py"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifications basiques
        if "'name'" in content and "AI Chat Assistant" in content:
            print("✅ Nom du module OK")
        else:
            print("❌ Nom du module manquant ou incorrect")
            
        if "'depends'" in content:
            print("✅ Dépendances définies")
        else:
            print("❌ Dépendances manquantes")
            
        if "'data'" in content:
            print("✅ Fichiers de données définis")
        else:
            print("❌ Fichiers de données manquants")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du manifest: {e}")
        return False

def check_models():
    """Vérifier les définitions des modèles"""
    print("\n🗃️ Vérification des modèles...")
    
    try:
        models_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant/models/ai_knowledge_base.py"
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        models_to_check = [
            "class AIKnowledgeBase",
            "class AIChatSession", 
            "class AIChatMessage"
        ]
        
        for model in models_to_check:
            if model in content:
                print(f"✅ {model} défini")
            else:
                print(f"❌ {model} manquant")
                
        # Vérifier les noms de modèles
        model_names = [
            "_name = 'ai.knowledge.base'",
            "_name = 'ai.chat.session'",
            "_name = 'ai.chat.message'"
        ]
        
        for model_name in model_names:
            if model_name in content:
                print(f"✅ {model_name}")
            else:
                print(f"❌ {model_name} manquant ou incorrect")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des modèles: {e}")
        return False

def generate_installation_report():
    """Générer un rapport d'installation"""
    print("\n📊 RAPPORT D'INSTALLATION")
    print("=" * 50)
    
    structure_ok = check_module_structure()
    manifest_ok = check_manifest() 
    models_ok = check_models()
    
    print(f"\n📁 Structure des fichiers: {'✅ OK' if structure_ok else '❌ PROBLÈME'}")
    print(f"📋 Fichier manifest: {'✅ OK' if manifest_ok else '❌ PROBLÈME'}")
    print(f"🗃️ Définition des modèles: {'✅ OK' if models_ok else '❌ PROBLÈME'}")
    
    overall_status = structure_ok and manifest_ok and models_ok
    
    print(f"\n🎯 STATUT GLOBAL: {'✅ PRÊT POUR INSTALLATION' if overall_status else '❌ CORRECTIONS NÉCESSAIRES'}")
    
    if overall_status:
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("1. Redémarrer le serveur Odoo")
        print("2. Aller dans Apps → Mettre à jour la liste des apps")
        print("3. Rechercher 'AI Chat Assistant'")
        print("4. Installer le module")
        print("5. Tester le chatbot en cliquant sur la bulle en bas à droite")
    else:
        print("\n🔧 ACTIONS REQUISES:")
        print("1. Corriger les fichiers manquants")
        print("2. Vérifier la syntaxe Python")
        print("3. Relancer ce script de test")
        
    return overall_status

if __name__ == "__main__":
    print("🤖 AI Chat Assistant - Script de Vérification")
    print("=" * 50)
    
    try:
        result = generate_installation_report()
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print("\n\n❌ Script interrompu par l'utilisateur")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)