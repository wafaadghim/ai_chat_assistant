#!/usr/bin/env python3
"""
Script de validation finale du module AI Chat Assistant
"""

import os
import xml.etree.ElementTree as ET
import csv
import sys

def test_xml_syntax(file_path):
    """Test la syntaxe XML d'un fichier"""
    try:
        ET.parse(file_path)
        return True, "✅ Syntaxe XML valide"
    except ET.ParseError as e:
        return False, f"❌ Erreur XML: {e}"

def test_csv_syntax(file_path):
    """Test la syntaxe CSV d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            csv.reader(f)
            lines = f.readlines()
            if len(lines) < 2:
                return False, "❌ CSV vide ou incomplet"
        return True, f"✅ CSV valide ({len(lines)} lignes)"
    except Exception as e:
        return False, f"❌ Erreur CSV: {e}"

def test_python_syntax(file_path):
    """Test la syntaxe Python d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, file_path, 'exec')
        return True, "✅ Syntaxe Python valide"
    except SyntaxError as e:
        return False, f"❌ Erreur Python: {e}"
    except Exception as e:
        return False, f"❌ Erreur: {e}"

def main():
    module_path = "/home/wafa/Documents/odoo/custom/ai_chat_assistant"
    
    print("🔍 VALIDATION FINALE DU MODULE AI CHAT ASSISTANT")
    print("=" * 60)
    
    # Tests des fichiers critiques
    tests = [
        # Fichiers XML
        ("views/chatbot_views.xml", test_xml_syntax),
        ("views/chatbot_templates.xml", test_xml_syntax),
        ("views/marketing_views.xml", test_xml_syntax),
        
        # Fichiers CSV
        ("security/ir.model.access.csv", test_csv_syntax),
        
        # Fichiers Python
        ("__init__.py", test_python_syntax),
        ("models/__init__.py", test_python_syntax),
        ("models/ai_knowledge_base.py", test_python_syntax),
        ("controllers/__init__.py", test_python_syntax),
        ("controllers/main.py", test_python_syntax),
    ]
    
    all_passed = True
    
    for file_rel_path, test_func in tests:
        file_path = os.path.join(module_path, file_rel_path)
        
        if os.path.exists(file_path):
            passed, message = test_func(file_path)
            print(f"{file_rel_path:<35} {message}")
            if not passed:
                all_passed = False
        else:
            print(f"{file_rel_path:<35} ❌ Fichier manquant")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ Le module est prêt pour l'installation")
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("1. Redémarrer le serveur Odoo")
        print("2. Aller dans Apps → Update Apps List")
        print("3. Rechercher 'AI Chat Assistant'")
        print("4. Installer le module")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️  Corrigez les erreurs avant l'installation")
        return 1

if __name__ == "__main__":
    sys.exit(main())