#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Rapide - Validation Multilingue AI Chat Assistant
"""

import requests
import json

# Configuration
ODOO_URL = "http://localhost:8069"
ENDPOINT = "/ai_chat/get_response"

def test_language_detection(question, expected_language, description):
    """Tester une question et vérifier la langue détectée"""
    print(f"\n🧪 Test: {description}")
    print(f"❓ Question: '{question}'")
    print(f"🎯 Langue attendue: {expected_language}")
    
    try:
        # Préparer la requête
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "message": question
                # Pas de langue spécifiée pour tester la détection automatique
            }
        }
        
        # Envoyer la requête
        response = requests.post(
            ODOO_URL + ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', {})
            
            if result.get('success'):
                detected_language = result.get('language', 'Unknown')
                source = result.get('source', 'Unknown')
                confidence = result.get('confidence', 'Unknown')
                
                print(f"✅ SUCCÈS")
                print(f"🔍 Langue détectée: {detected_language}")
                print(f"📊 Source: {source}")
                print(f"📈 Confiance: {confidence}")
                
                # Vérifier si la langue correspond
                if detected_language == expected_language:
                    print(f"🎉 PARFAIT! Langue correctement détectée")
                else:
                    print(f"⚠️ ATTENTION: Attendu {expected_language}, obtenu {detected_language}")
                
                # Afficher un extrait de la réponse
                answer = result.get('answer', '')
                if answer:
                    # Prendre les 100 premiers caractères
                    preview = answer[:100].replace('\n', ' ').strip()
                    if len(answer) > 100:
                        preview += "..."
                    print(f"💬 Extrait réponse: {preview}")
                
                return True
                
            else:
                print(f"❌ ÉCHEC: {result.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"❌ ERREUR HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    """Tests principaux"""
    print("🌍 Test de Détection Automatique de Langue")
    print("=" * 60)
    
    tests = [
        # Tests français
        ("taux d'ouverture email", "fr", "Question marketing en français"),
        ("performance campagne", "fr", "Analyse performance en français"),
        ("comment créer campagne", "fr", "Guide création en français"),
        
        # Tests anglais
        ("email open rate", "en", "Marketing question in English"),
        ("campaign performance", "en", "Performance analysis in English"),
        ("how to create campaign", "en", "Creation guide in English"),
        
        # Tests arabe
        ("معدل فتح البريد الإلكتروني", "ar", "سؤال تسويقي بالعربية"),
        ("أداء الحملات", "ar", "تحليل الأداء بالعربية"),
        ("إنشاء حملة بريد إلكتروني", "ar", "دليل الإنشاء بالعربية"),
        
        # Tests détection automatique
        ("What is my ROI?", "en", "Question ROI en anglais"),
        ("Quel est mon ROI?", "fr", "Question ROI en français"),
        ("ما هو العائد على الاستثمار؟", "ar", "سؤال العائد على الاستثمار بالعربية"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for question, expected_lang, description in tests:
        success = test_language_detection(question, expected_lang, description)
        if success:
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS FINAUX")
    print(f"✅ Succès: {success_count}/{total_tests}")
    print(f"📈 Taux de réussite: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 PARFAIT! Tous les tests passent - Système multilingue fonctionnel!")
    elif success_count >= total_tests * 0.8:
        print("👍 BIEN! La plupart des tests passent - Système majoritairement fonctionnel")
    else:
        print("⚠️ ATTENTION! Plusieurs tests échouent - Vérifier la configuration")
    
    print("\n💡 Instructions:")
    print("1. Assurez-vous qu'Odoo est démarré: ./odoo-bin --addons-path=addons,custom -d ai_chat")
    print("2. Que le module ai_chat_assistant est installé")
    print("3. Que l'endpoint /ai_chat/get_response est accessible")

if __name__ == "__main__":
    main()