#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la syntaxe du module AI Chat Assistant
"""

import sys
import os
import traceback

def test_syntax():
    """Tester la syntaxe des fichiers Python du module"""
    print("🔍 Test de syntaxe AI Chat Assistant")
    print("=" * 50)
    
    # Chemin vers le module
    module_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant"
    
    # Fichiers Python à tester
    python_files = [
        "models/ai_knowledge_base.py",
        "controllers/main.py",
        "__init__.py",
        "__manifest__.py"
    ]
    
    errors_found = False
    
    for file_path in python_files:
        full_path = os.path.join(module_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"❌ Fichier non trouvé: {file_path}")
            errors_found = True
            continue
            
        print(f"🔍 Test de {file_path}...")
        
        try:
            # Lire et compiler le fichier
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test de compilation
            compile(content, full_path, 'exec')
            print(f"✅ {file_path} - Syntaxe OK")
            
        except SyntaxError as e:
            print(f"❌ {file_path} - Erreur de syntaxe:")
            print(f"   Ligne {e.lineno}: {e.text}")
            print(f"   {e.msg}")
            errors_found = True
            
        except Exception as e:
            print(f"⚠️ {file_path} - Erreur: {e}")
            errors_found = True
    
    print("=" * 50)
    
    if errors_found:
        print("❌ Des erreurs ont été trouvées!")
        return False
    else:
        print("✅ Tous les tests de syntaxe ont réussi!")
        return True

def test_xml_files():
    """Tester la validité des fichiers XML"""
    print("\n🔍 Test des fichiers XML")
    print("=" * 50)
    
    import xml.etree.ElementTree as ET
    
    module_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant"
    
    xml_files = [
        "data/demo_knowledge_base.xml",
        "data/fallback_database_entries.xml", 
        "views/chatbot_views.xml",
        "views/chatbot_templates.xml"
    ]
    
    errors_found = False
    
    for file_path in xml_files:
        full_path = os.path.join(module_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"❌ Fichier XML non trouvé: {file_path}")
            errors_found = True
            continue
            
        print(f"🔍 Test XML de {file_path}...")
        
        try:
            ET.parse(full_path)
            print(f"✅ {file_path} - XML valide")
            
        except ET.ParseError as e:
            print(f"❌ {file_path} - Erreur XML:")
            print(f"   {e}")
            errors_found = True
            
        except Exception as e:
            print(f"⚠️ {file_path} - Erreur: {e}")
            errors_found = True
    
    print("=" * 50)
    
    if errors_found:
        print("❌ Des erreurs XML ont été trouvées!")
        return False
    else:
        print("✅ Tous les fichiers XML sont valides!")
        return True

def check_manifest():
    """Vérifier le fichier manifest"""
    print("\n🔍 Test du fichier __manifest__.py")
    print("=" * 50)
    
    manifest_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant/__manifest__.py"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Evaluer le contenu du manifest
        manifest_data = eval(content)
        
        required_keys = ['name', 'version', 'depends', 'data']
        
        for key in required_keys:
            if key not in manifest_data:
                print(f"❌ Clé manquante dans __manifest__.py: {key}")
                return False
            else:
                print(f"✅ {key}: {manifest_data[key]}")
        
        print("✅ __manifest__.py est valide!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans __manifest__.py: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test complet du module AI Chat Assistant")
    print("=" * 70)
    
    all_good = True
    
    # Test syntaxe Python
    if not test_syntax():
        all_good = False
    
    # Test fichiers XML  
    if not test_xml_files():
        all_good = False
    
    # Test manifest
    if not check_manifest():
        all_good = False
    
    print("\n" + "=" * 70)
    
    if all_good:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Le module AI Chat Assistant est prêt à être installé!")
        print("\n📋 Prochaines étapes:")
        print("   1. Redémarrer Odoo")
        print("   2. Mettre à jour le module depuis l'interface")
        print("   3. Tester le chat en ligne")
        return 0
    else:
        print("❌ DES ERREURS ONT ÉTÉ TROUVÉES!")
        print("🔧 Veuillez corriger les erreurs avant d'installer le module.")
        return 1

if __name__ == "__main__":
    sys.exit(main())