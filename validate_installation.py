#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation du module AI Chat Assistant pour Odoo
"""

import os
import sys
import xml.etree.ElementTree as ET
import ast

def check_python_syntax(file_path):
    """Vérifier la syntaxe Python d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read(), filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_xml_syntax(file_path):
    """Vérifier la syntaxe XML d'un fichier"""
    try:
        ET.parse(file_path)
        return True, None
    except ET.ParseError as e:
        return False, f"XML Parse Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_manifest():
    """Valider le fichier __manifest__.py"""
    print("📋 Validation du __manifest__.py...")
    
    if not os.path.exists('__manifest__.py'):
        print("❌ __manifest__.py manquant")
        return False
    
    is_valid, error = check_python_syntax('__manifest__.py')
    if not is_valid:
        print(f"❌ __manifest__.py: {error}")
        return False
    
    # Charger et vérifier le contenu
    try:
        with open('__manifest__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les champs obligatoires
        required_fields = ['name', 'version', 'depends', 'data']
        manifest = ast.literal_eval(content.split('=', 1)[1].strip())
        
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Champ manquant dans __manifest__.py: {field}")
                return False
        
        print("✅ __manifest__.py valide")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de __manifest__.py: {e}")
        return False

def validate_data_files():
    """Valider les fichiers de données référencés dans le manifest"""
    print("\n📁 Validation des fichiers de données...")
    
    # Lire le manifest pour obtenir la liste des fichiers
    try:
        with open('__manifest__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        manifest = ast.literal_eval(content.split('=', 1)[1].strip())
        data_files = manifest.get('data', [])
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du manifest: {e}")
        return False
    
    all_valid = True
    
    for file_path in data_files:
        if not os.path.exists(file_path):
            print(f"❌ Fichier manquant: {file_path}")
            all_valid = False
            continue
        
        if file_path.endswith('.xml'):
            is_valid, error = check_xml_syntax(file_path)
            if not is_valid:
                print(f"❌ {file_path}: {error}")
                all_valid = False
            else:
                print(f"✅ {file_path}")
        
        elif file_path.endswith('.csv'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if content:
                    print(f"✅ {file_path}")
                else:
                    print(f"⚠️ {file_path} (vide)")
            except Exception as e:
                print(f"❌ {file_path}: {e}")
                all_valid = False
        
        else:
            print(f"✅ {file_path} (non vérifié)")
    
    return all_valid

def validate_python_files():
    """Valider tous les fichiers Python"""
    print("\n🐍 Validation des fichiers Python...")
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    all_valid = True
    
    for py_file in python_files:
        is_valid, error = check_python_syntax(py_file)
        if not is_valid:
            print(f"❌ {py_file}: {error}")
            all_valid = False
        else:
            print(f"✅ {py_file}")
    
    return all_valid

def check_module_structure():
    """Vérifier la structure standard du module Odoo"""
    print("\n📂 Vérification de la structure du module...")
    
    required_structure = {
        '__init__.py': 'file',
        '__manifest__.py': 'file',
        'models': 'dir',
        'models/__init__.py': 'file',
        'views': 'dir',
        'security': 'dir',
        'security/ir.model.access.csv': 'file'
    }
    
    all_valid = True
    
    for path, path_type in required_structure.items():
        if path_type == 'file':
            if os.path.isfile(path):
                print(f"✅ {path}")
            else:
                print(f"❌ Fichier manquant: {path}")
                all_valid = False
        elif path_type == 'dir':
            if os.path.isdir(path):
                print(f"✅ {path}/")
            else:
                print(f"❌ Répertoire manquant: {path}/")
                all_valid = False
    
    return all_valid

def main():
    """Fonction principale de validation"""
    print("🔍 VALIDATION DU MODULE AI CHAT ASSISTANT")
    print("==========================================\n")
    
    # Vérifier si nous sommes dans le bon répertoire
    if not os.path.exists('__manifest__.py'):
        print("❌ Ce script doit être exécuté depuis le répertoire du module")
        sys.exit(1)
    
    validation_results = []
    
    # Validations
    validation_results.append(("Structure du module", check_module_structure()))
    validation_results.append(("Manifest", validate_manifest()))
    validation_results.append(("Fichiers Python", validate_python_files()))
    validation_results.append(("Fichiers de données", validate_data_files()))
    
    # Résumé
    print("\n📊 RÉSUMÉ DE LA VALIDATION")
    print("==========================")
    
    all_passed = True
    for test_name, result in validation_results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 MODULE PRÊT POUR L'INSTALLATION !")
        print("Vous pouvez maintenant installer le module dans Odoo")
    else:
        print("⚠️ LE MODULE A DES PROBLÈMES")
        print("Corrigez les erreurs avant l'installation")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)