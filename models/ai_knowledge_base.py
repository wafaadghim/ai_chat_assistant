# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import json
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AIKnowledgeBase(models.Model):
    _name = 'ai.knowledge.base'
    _description = 'Base de connaissances pour l\'Assistant IA'
    _order = 'priority desc, usage_count desc, create_date desc'

    question = fields.Text(string='Question', required=True, help="Question ou phrase clé")
    answer = fields.Html(string='Réponse', required=True, help="Réponse détaillée")
    category = fields.Selection([
        ('marketing', 'Marketing'),
        ('campaigns', 'Campagnes'),
        ('analytics', 'Analytics'),
        ('recommendations', 'Recommandations'),
        ('general', 'Général'),
        ('troubleshooting', 'Dépannage')
    ], string='Catégorie', default='general', required=True)
    
    language = fields.Selection([
        ('ar', 'العربية'),
        ('fr', 'Français'),
        ('en', 'English'),
        ('multi', 'Multilingue')
    ], string='Langue', default='multi', required=True)
    
    keywords = fields.Many2many('ai.knowledge.keyword', string='Mots-clés')
    priority = fields.Integer(string='Priorité', default=1, help="Plus élevé = plus prioritaire")
    usage_count = fields.Integer(string='Nombre d\'utilisations', default=0, readonly=True)
    is_active = fields.Boolean(string='Actif', default=True)
    campaign_references = fields.Text(string='Références Campagnes', help="Références aux campagnes ou données marketing")
    
    def action_view_usage(self):
        """Action pour voir l'utilisation de cette entrée"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Utilisation: {self.question}',
            'res_model': 'ai.chat.message',
            'view_mode': 'list,form',
            'domain': [('metadata', 'ilike', f'"knowledge_base_id": {self.id}')],
            'context': {'default_session_id': False}
        }

    def _extract_intent_and_entities(self, query, language):
        """Extraire l'intention et les entités de la question"""
        import re
        
        query_lower = query.lower().strip()
        
        # Dictionnaire des intentions par langue avec patterns
        intent_patterns = {
            'fr': {
                'get_performance': [
                    r'\b(performance|résultat|taux|statistique|métrique|chiffre|données)\b',
                    r'\b(comment ça marche|combien|quel.*taux|quelle.*performance)\b'
                ],
                'get_analysis': [
                    r'\b(analys|rapport|bilan|résumé|overview|aperçu)\b',
                    r'\b(montre.*moi|affiche|donne.*moi|voir)\b.*\b(rapport|analyse|bilan)\b'
                ],
                'create_campaign': [
                    r'\b(créer|créat|nouvelle|nouveau|faire|lancer).*\b(campagne|email|newsletter)\b',
                    r'\bcomment.*\b(créer|faire|lancer|démarrer)\b'
                ],
                'optimize': [
                    r'\b(optimis|améliorer|augmenter|diminuer|réduire)\b',
                    r'\b(conseils?|recommandation|suggestion|tips?)\b'
                ],
                'get_help': [
                    r'\b(aide|comment|pourquoi|help|assistance)\b',
                    r'\b(ne sais pas|comprend pas|expliquer|guide)\b'
                ],
                'get_status': [
                    r'\b(état|status|situation|où en est)\b',
                    r'\b(en cours|active|terminé|fini)\b'
                ]
            },
            'ar': {
                'get_performance': [
                    r'\b(أداء|نتائج|معدل|إحصائيات|مقاييس|أرقام|بيانات)\b',
                    r'\b(كيف.*يعمل|كم|كم.*معدل|ما.*أداء)\b'
                ],
                'get_analysis': [
                    r'\b(تحليل|تقرير|خلاصة|ملخص|نظرة عامة)\b',
                    r'\b(أظهر.*لي|اعرض|أعطني|أريد.*أن.*أرى)\b.*\b(تقرير|تحليل|خلاصة)\b'
                ],
                'create_campaign': [
                    r'\b(إنشاء|إنشئ|جديد|جديدة|عمل|إطلاق).*\b(حملة|بريد|نشرة)\b',
                    r'\bكيف.*\b(أنشئ|أعمل|أطلق|أبدأ)\b'
                ],
                'optimize': [
                    r'\b(تحسين|تطوير|زيادة|تقليل|تقليص)\b',
                    r'\b(نصائح|توصيات|اقتراحات|مشورة)\b'
                ],
                'get_help': [
                    r'\b(مساعدة|كيف|لماذا|شرح|إرشاد)\b',
                    r'\b(لا أعرف|لا أفهم|اشرح.*لي|دليل)\b'
                ]
            },
            'en': {
                'get_performance': [
                    r'\b(performance|result|rate|statistic|metric|number|data)\b',
                    r'\b(how.*work|how much|what.*rate|what.*performance)\b'
                ],
                'get_analysis': [
                    r'\b(analy|report|summary|overview|dashboard)\b',
                    r'\b(show.*me|display|give.*me|see)\b.*\b(report|analysis|summary)\b'
                ],
                'create_campaign': [
                    r'\b(create|new|make|launch|start).*\b(campaign|email|newsletter)\b',
                    r'\bhow.*to.*\b(create|make|launch|start)\b'
                ],
                'optimize': [
                    r'\b(optim|improve|increase|decrease|reduce)\b',
                    r'\b(tips?|recommendation|suggestion|advice)\b'
                ],
                'get_help': [
                    r'\b(help|how|why|explain|guide|assist)\b',
                    r'\b(don\'t know|don\'t understand|explain.*me)\b'
                ]
            }
        }
        
        # Entités marketing par langue
        marketing_entities = {
            'fr': {
                'campaign_types': r'\b(email|newsletter|sms|social|facebook|instagram|google|adwords)\b',
                'metrics': r'\b(taux.*ouverture|taux.*clic|roi|conversion|engagement|reach|impression)\b',
                'timeframes': r'\b(aujourd\'hui|hier|semaine|mois|année|quotidien|mensuel)\b',
                'targets': r'\b(audience|client|prospect|segment|démographique)\b'
            },
            'ar': {
                'campaign_types': r'\b(بريد|نشرة|رسالة|اجتماعي|فيسبوك|انستغرام|جوجل)\b',
                'metrics': r'\b(معدل.*فتح|معدل.*نقر|عائد|تحويل|تفاعل|وصول|ظهور)\b',
                'timeframes': r'\b(اليوم|أمس|أسبوع|شهر|سنة|يومي|شهري)\b',
                'targets': r'\b(جمهور|عميل|محتمل|قطاع|ديموغرافي)\b'
            },
            'en': {
                'campaign_types': r'\b(email|newsletter|sms|social|facebook|instagram|google|adwords)\b',
                'metrics': r'\b(open.*rate|click.*rate|roi|conversion|engagement|reach|impression)\b',
                'timeframes': r'\b(today|yesterday|week|month|year|daily|monthly)\b',
                'targets': r'\b(audience|customer|prospect|segment|demographic)\b'
            }
        }
        
        # Détecter l'intention principale
        detected_intent = 'general'
        intent_confidence = 0.0
        
        patterns = intent_patterns.get(language, intent_patterns.get('en', {}))
        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query_lower):
                    intent_confidence += 0.3
                    if intent_confidence > 0.3:  # Seuil de confiance
                        detected_intent = intent
                        break
        
        # Extraire les entités
        entities = {}
        entity_patterns = marketing_entities.get(language, marketing_entities.get('en', {}))
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.findall(pattern, query_lower)
            if matches:
                entities[entity_type] = matches
        
        return {
            'intent': detected_intent,
            'intent_confidence': min(intent_confidence, 1.0),
            'entities': entities,
            'query_keywords': re.findall(r'\b\w{3,}\b', query_lower)  # Mots de 3+ caractères
        }

    @api.model
    def search_knowledge(self, query, language='multi', category=None, limit=5):
        """Rechercher dans la base de connaissances avec correspondance exacte du sujet"""
        import re
        
        # D'abord extraire l'intention et les entités de la question
        query_analysis = self._extract_intent_and_entities(query, language)
        
        domain = [('is_active', '=', True)]
        
        # Filtre par langue - prioriser la langue spécifique puis multilingue
        if language != 'multi':
            # Rechercher d'abord dans la langue spécifique
            domain_specific = domain + [('language', '=', language)]
            domain_multi = domain + [('language', '=', 'multi')]
        else:
            domain_specific = domain
            domain_multi = []
        
        # Filtre par catégorie
        if category:
            if domain_specific:
                domain_specific.append(('category', '=', category))
            if domain_multi:
                domain_multi.append(('category', '=', category))
        
        # Recherche textuelle
        query_lower = query.lower().strip()
        query_words = re.findall(r'\b\w+\b', query_lower)
        
        def calculate_entry_score(entry, is_specific_language=True):
            """Calculer le score pour une entrée avec validation de pertinence thématique"""
            score = 0
            entry_question_lower = entry.question.lower()
            entry_answer_lower = entry.answer.lower()
            
            # 0. VALIDATION DE PERTINENCE THÉMATIQUE (nouveau)
            # Vérifier si l'entrée correspond à l'intention détectée
            intent_match_bonus = self._calculate_intent_relevance(
                query_analysis, entry, entry_question_lower, entry_answer_lower
            )
            score += intent_match_bonus
            
            # Si pas de correspondance thématique minimum, réduire drastiquement
            if intent_match_bonus < 5 and query_analysis['intent_confidence'] > 0.6:
                score -= 50  # Pénalité pour manque de pertinence thématique
            
            # 1. Correspondance exacte complète (très haute priorité)
            if query_lower == entry_question_lower:
                score += 120  # Augmenté pour correspondance parfaite
            elif query_lower in entry_question_lower:
                # Correspondance partielle dans la question
                if entry_question_lower.startswith(query_lower):
                    score += 60  # Commence par la requête
                elif entry_question_lower.endswith(query_lower):
                    score += 50  # Se termine par la requête
                else:
                    score += 35  # Contient la requête
            
            # 2. Correspondance exacte inversée (question contient la requête)
            if entry_question_lower in query_lower:
                score += 35
            
            # 3. Score basé sur les mots individuels dans la question
            question_words = re.findall(r'\b\w+\b', entry_question_lower)
            matching_words = 0
            for word in query_words:
                if len(word) > 2:  # Ignorer les mots trop courts
                    if word in question_words:
                        matching_words += 1
                        score += 8
                    # Correspondance partielle de mot (stemming basique)
                    elif any(qw.startswith(word[:4]) or word.startswith(qw[:4]) for qw in question_words if len(qw) > 3):
                        score += 3
            
            # Bonus pour pourcentage de mots correspondants
            if query_words and matching_words > 0:
                match_percentage = matching_words / len(query_words)
                score += match_percentage * 15
            
            # 4. Score basé sur les mots-clés
            keyword_matches = 0
            for keyword in entry.keywords:
                keyword_lower = keyword.name.lower()
                if keyword_lower in query_lower:
                    keyword_matches += 1
                    if keyword_lower == query_lower:
                        score += 25  # Correspondance exacte du mot-clé
                    else:
                        score += 12  # Correspondance partielle
                
                # Correspondance de mots individuels avec les mots-clés
                for word in query_words:
                    if len(word) > 2 and word in keyword_lower:
                        score += 6
            
            # 5. Score basé sur la réponse (plus faible priorité)
            if query_lower in entry_answer_lower:
                score += 5
            
            # Correspondance de mots dans la réponse
            answer_word_matches = sum(1 for word in query_words 
                                    if len(word) > 2 and word in entry_answer_lower)
            score += answer_word_matches * 2
            
            # 6. Bonus pour langue spécifique vs multilingue
            if is_specific_language:
                score += 20
            
            # 7. Bonus pour priorité et usage
            score += entry.priority * 2
            score += min(entry.usage_count * 0.2, 8)  # Max 8 points bonus
            
            # 8. Bonus pour catégorie correspondante
            if category and entry.category == category:
                score += 15
            
            # 9. Pénalité pour réponses trop courtes ou vagues
            if len(entry.answer) < 50:
                score -= 5
            
            # 10. Bonus pour réponses détaillées
            if len(entry.answer) > 200:
                score += 5
            
            return score
        
        # Collecter et scorer les entrées
        scored_entries = []
        
        # D'abord rechercher dans la langue spécifique
        if domain_specific:
            specific_entries = self.search(domain_specific)
            for entry in specific_entries:
                score = calculate_entry_score(entry, True)
                if score > 0:
                    scored_entries.append((score, entry, True))
        
        # Puis dans les entrées multilingues si nécessaire
        if domain_multi and (not scored_entries or scored_entries[0][0] < 50):
            multi_entries = self.search(domain_multi)
            for entry in multi_entries:
                score = calculate_entry_score(entry, False)
                if score > 0:
                    scored_entries.append((score, entry, False))
        
        # Trier par score décroissant
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        
        # Filtrer les doublons et retourner les résultats
        seen_ids = set()
        unique_entries = []
        
        for score, entry, is_specific in scored_entries:
            if entry.id not in seen_ids and len(unique_entries) < limit:
                seen_ids.add(entry.id)
                unique_entries.append(entry)
        
        return unique_entries

    def _calculate_intent_relevance(self, query_analysis, entry, entry_question_lower, entry_answer_lower):
        """Calculer la pertinence thématique entre la question et l'entrée"""
        import re
        
        intent = query_analysis['intent']
        entities = query_analysis['entities']
        query_keywords = query_analysis['query_keywords']
        
        relevance_score = 0
        
        # Mapping intentions vers catégories et mots-clés pertinents
        intent_mappings = {
            'get_performance': {
                'categories': ['analytics', 'campaigns'],
                'keywords_patterns': [
                    r'\b(performance|résultat|taux|rate|metric|statistique|chiffre|roi|conversion)\b',
                    r'\b(أداء|نتائج|معدل|إحصائيات|عائد)\b'
                ],
                'bonus': 25
            },
            'get_analysis': {
                'categories': ['analytics', 'marketing'],
                'keywords_patterns': [
                    r'\b(analys|rapport|dashboard|overview|aperçu|bilan|résumé)\b',
                    r'\b(تحليل|تقرير|نظرة عامة|ملخص)\b'
                ],
                'bonus': 30
            },
            'create_campaign': {
                'categories': ['campaigns', 'marketing'],
                'keywords_patterns': [
                    r'\b(créer|create|campagne|campaign|email|newsletter|lancer|launch)\b',
                    r'\b(إنشاء|حملة|بريد|إطلاق)\b'
                ],
                'bonus': 35
            },
            'optimize': {
                'categories': ['recommendations', 'marketing'],
                'keywords_patterns': [
                    r'\b(optimis|améliorer|improve|conseil|recommandation|suggestion|tips)\b',
                    r'\b(تحسين|توصيات|نصائح|اقتراحات)\b'
                ],
                'bonus': 30
            },
            'get_help': {
                'categories': ['general'],
                'keywords_patterns': [
                    r'\b(aide|help|comment|how|pourquoi|why|expliquer|explain)\b',
                    r'\b(مساعدة|كيف|لماذا|شرح)\b'
                ],
                'bonus': 15
            }
        }
        
        # Vérifier correspondance catégorie
        if intent in intent_mappings:
            mapping = intent_mappings[intent]
            
            # Bonus si catégorie correspond
            if entry.category in mapping['categories']:
                relevance_score += mapping['bonus']
            
            # Vérifier patterns de mots-clés dans question et réponse
            for pattern in mapping['keywords_patterns']:
                if re.search(pattern, entry_question_lower):
                    relevance_score += 15
                if re.search(pattern, entry_answer_lower):
                    relevance_score += 8
        
        # Vérifier correspondance des entités extraites
        for entity_type, entity_values in entities.items():
            for entity_value in entity_values:
                if entity_value in entry_question_lower:
                    relevance_score += 20  # Entité dans question
                if entity_value in entry_answer_lower:
                    relevance_score += 10  # Entité dans réponse
        
        # Correspondance sémantique des mots-clés de la question
        semantic_matches = 0
        for keyword in query_keywords:
            # Vérification directe
            if keyword in entry_question_lower:
                semantic_matches += 1
                relevance_score += 8
            elif keyword in entry_answer_lower:
                semantic_matches += 0.5
                relevance_score += 4
            
            # Vérification synonymes/variantes selon le domaine
            variants = self._get_keyword_variants(keyword)
            for variant in variants:
                if variant in entry_question_lower:
                    semantic_matches += 0.7
                    relevance_score += 6
                elif variant in entry_answer_lower:
                    semantic_matches += 0.3
                    relevance_score += 3
        
        # Bonus pour pourcentage de correspondance sémantique élevé
        if query_keywords:
            semantic_ratio = semantic_matches / len(query_keywords)
            relevance_score += semantic_ratio * 20
        
        return min(relevance_score, 100)  # Cap à 100 points
    
    def _get_keyword_variants(self, keyword):
        """Récupérer les variantes d'un mot-clé avec gestion d'erreur"""
        try:
            # Essayer d'utiliser le modèle keyword s'il existe et est accessible
            if hasattr(self.env, 'ai.knowledge.keyword'):
                keyword_model = self.env['ai.knowledge.keyword']
                return keyword_model.get_keyword_variants(keyword)
        except Exception:
            # Fallback vers le mapping hardcodé si problème d'accès
            pass
        
        # Mapping de fallback intégré
        variants_map = {
            # Français
            'performance': ['performance', 'résultat', 'efficacité', 'rendement', 'productivité'],
            'campagne': ['campagne', 'publicité', 'advertising', 'promotion', 'marketing'],
            'email': ['email', 'mail', 'courriel', 'newsletter', 'emailing'],
            'taux': ['taux', 'pourcentage', 'ratio', 'métrique', 'indicateur'],
            'ouverture': ['ouverture', 'open', 'lecture', 'consultation', 'vue'],
            'clic': ['clic', 'click', 'clique', 'interaction', 'engagement'],
            'conversion': ['conversion', 'vente', 'achat', 'transformation', 'action'],
            'roi': ['roi', 'retour', 'rentabilité', 'bénéfice', 'profit'],
            'analyse': ['analyse', 'analytique', 'statistique', 'rapport', 'données'],
            'optimisation': ['optimisation', 'amélioration', 'enhancement', 'perfectionnement'],
            
            # English
            'campaign': ['campaign', 'advertising', 'promotion', 'marketing'],
            'rate': ['rate', 'percentage', 'ratio', 'metric'],
            'open': ['open', 'opening', 'view', 'read'],
            'click': ['click', 'clicking', 'interaction'],
            'analysis': ['analysis', 'analytics', 'statistics', 'report', 'data'],
            'optimization': ['optimization', 'improvement', 'enhancement'],
            
            # العربية
            'حملة': ['حملة', 'إعلان', 'ترويج', 'دعاية'],
            'معدل': ['معدل', 'نسبة', 'مقياس'],
            'فتح': ['فتح', 'قراءة', 'اطلاع'],
            'نقر': ['نقر', 'ضغط', 'تفاعل'],
            'تحليل': ['تحليل', 'إحصائية', 'تقرير', 'بيانات'],
            'تحسين': ['تحسين', 'تطوير', 'تحسن']
        }
        
        return variants_map.get(keyword.lower(), [keyword])

    def _validate_response_relevance(self, user_message, entry, query_analysis, language):
        """Validation finale de la pertinence de la réponse par rapport à la question"""
        import re
        
        relevance_score = 0
        user_message_lower = user_message.lower()
        entry_question_lower = entry.question.lower()
        entry_answer_lower = entry.answer.lower()
        
        # 1. Correspondance thématique directe (score le plus important)
        intent = query_analysis['intent']
        entities = query_analysis['entities']
        keywords = query_analysis['query_keywords']
        
        # Vérifier si la réponse traite du même sujet que la question
        subject_match = False
        
        # Extraction du sujet principal de la question
        question_subjects = self._extract_main_subjects(user_message, language)
        answer_subjects = self._extract_main_subjects(entry.answer, language)
        
        # Correspondance de sujets
        for q_subject in question_subjects:
            if any(q_subject in a_subject or a_subject in q_subject for a_subject in answer_subjects):
                subject_match = True
                relevance_score += 30
                break
        
        # 2. Correspondance d'intention
        if self._intent_matches_entry(intent, entry, entry_question_lower, entry_answer_lower):
            relevance_score += 25
        
        # 3. Correspondance d'entités spécifiques
        entity_matches = 0
        for entity_list in entities.values():
            for entity in entity_list:
                if entity in entry_question_lower or entity in entry_answer_lower:
                    entity_matches += 1
                    relevance_score += 15
        
        # 4. Correspondance de mots-clés contextuels
        contextual_matches = 0
        for keyword in keywords:
            if len(keyword) > 3:  # Mots significatifs seulement
                if keyword in entry_question_lower:
                    contextual_matches += 1
                    relevance_score += 10
                elif keyword in entry_answer_lower:
                    contextual_matches += 0.5
                    relevance_score += 5
        
        # 5. Validation par exclusion (éviter les réponses hors-sujet)
        off_topic_penalty = self._calculate_off_topic_penalty(
            user_message_lower, entry_answer_lower, intent, language
        )
        relevance_score -= off_topic_penalty
        
        # Score final et seuils
        final_score = max(0, relevance_score)
        is_relevant = (
            final_score >= 40 and subject_match  # Seuil élevé + correspondance sujet
        ) or (
            final_score >= 60  # Seuil très élevé même sans correspondance parfaite de sujet
        )
        
        # Confidence basée sur le score
        confidence = min(0.95, max(0.3, final_score / 100))
        
        return {
            'is_relevant': is_relevant,
            'confidence_score': confidence,
            'relevance_score': final_score,
            'subject_match': subject_match,
            'entity_matches': entity_matches,
            'contextual_matches': contextual_matches,
            'off_topic_penalty': off_topic_penalty
        }

    def _extract_main_subjects(self, text, language):
        """Extraire les sujets principaux d'un texte"""
        import re
        
        # Sujets marketing par langue
        subject_patterns = {
            'fr': {
                'email': r'\b(email|mail|courriel|newsletter|emailing)\b',
                'campagne': r'\b(campagne|publicité|advertising|promotion)\b',
                'performance': r'\b(performance|résultat|efficacité|rendement)\b',
                'roi': r'\b(roi|retour|rentabilité|bénéfice|profit)\b',
                'taux': r'\b(taux|pourcentage|ratio|métrique)\b',
                'conversion': r'\b(conversion|vente|achat|transformation)\b',
                'ouverture': r'\b(ouverture|open|lecture|consultation)\b',
                'clic': r'\b(clic|click|clique|interaction)\b',
                'analyse': r'\b(analys|statistique|rapport|données|insight)\b',
                'optimisation': r'\b(optimis|améliorer|perfectionner|enhancement)\b'
            },
            'ar': {
                'email': r'\b(بريد|إيميل|رسالة|نشرة)\b',
                'campagne': r'\b(حملة|إعلان|ترويج|دعاية)\b',
                'performance': r'\b(أداء|نتيجة|فعالية|كفاءة)\b',
                'roi': r'\b(عائد|ربح|مردود|فائدة)\b',
                'taux': r'\b(معدل|نسبة|مقياس)\b',
                'conversion': r'\b(تحويل|بيع|شراء|تحول)\b',
                'ouverture': r'\b(فتح|قراءة|اطلاع)\b',
                'clic': r'\b(نقر|ضغط|تفاعل)\b',
                'analyse': r'\b(تحليل|إحصائية|تقرير|بيانات)\b',
                'optimisation': r'\b(تحسين|تطوير|تحسن)\b'
            },
            'en': {
                'email': r'\b(email|mail|newsletter|mailing)\b',
                'campaign': r'\b(campaign|advertising|promotion|marketing)\b',
                'performance': r'\b(performance|result|efficiency|effectiveness)\b',
                'roi': r'\b(roi|return|profitability|profit)\b',
                'rate': r'\b(rate|percentage|ratio|metric)\b',
                'conversion': r'\b(conversion|sale|purchase|transformation)\b',
                'open': r'\b(open|opening|view|read)\b',
                'click': r'\b(click|clicking|interaction)\b',
                'analysis': r'\b(analy|statistic|report|data|insight)\b',
                'optimization': r'\b(optim|improve|enhance|better)\b'
            }
        }
        
        subjects = []
        patterns = subject_patterns.get(language, subject_patterns.get('en', {}))
        text_lower = text.lower()
        
        for subject, pattern in patterns.items():
            if re.search(pattern, text_lower):
                subjects.append(subject)
        
        return subjects

    def _intent_matches_entry(self, intent, entry, entry_question_lower, entry_answer_lower):
        """Vérifier si l'intention correspond à l'entrée"""
        
        # Mapping intentions vers patterns de vérification
        intent_verification = {
            'get_performance': [
                r'\b(performance|résultat|taux|rate|metric|statistique|أداء|نتائج|معدل)\b',
                r'\b(analytics|analys|rapport|dashboard|تحليل|تقرير)\b'
            ],
            'get_analysis': [
                r'\b(analys|rapport|overview|aperçu|dashboard|bilan|تحليل|تقرير|نظرة)\b',
                r'\b(données|data|statistique|metric|بيانات|إحصائية)\b'
            ],
            'create_campaign': [
                r'\b(créer|create|nouveau|new|faire|make|lancer|launch|إنشاء|جديد)\b',
                r'\b(campagne|campaign|email|newsletter|publicité|حملة|بريد)\b'
            ],
            'optimize': [
                r'\b(optimis|améliorer|improve|enhance|augmenter|increase|تحسين|تطوير)\b',
                r'\b(conseil|recommendation|suggestion|tip|نصيحة|توصية|اقتراح)\b'
            ]
        }
        
        patterns = intent_verification.get(intent, [])
        
        for pattern in patterns:
            if re.search(pattern, entry_question_lower) or re.search(pattern, entry_answer_lower):
                return True
        
        # Vérifier correspondance catégorie
        category_mapping = {
            'get_performance': ['analytics', 'campaigns'],
            'get_analysis': ['analytics', 'marketing'],
            'create_campaign': ['campaigns', 'marketing'],
            'optimize': ['recommendations', 'marketing']
        }
        
        if intent in category_mapping and entry.category in category_mapping[intent]:
            return True
        
        return False

    def _calculate_off_topic_penalty(self, user_message_lower, entry_answer_lower, intent, language):
        """Calculer la pénalité pour réponses hors-sujet"""
        penalty = 0
        
        # Patterns de sujets non pertinents selon l'intention
        off_topic_patterns = {
            'get_performance': {
                'fr': [r'\b(créer|création|nouveau|guide.*étapes|how.*to.*create)\b'],
                'ar': [r'\b(إنشاء|جديد|كيفية.*إنشاء)\b'],
                'en': [r'\b(create|creation|new|how.*to.*create|setup.*guide)\b']
            },
            'create_campaign': {
                'fr': [r'\b(analys|résultat|performance|statistique|taux.*actuel)\b'],
                'ar': [r'\b(تحليل|نتيجة|أداء|إحصائية|معدل.*حالي)\b'],
                'en': [r'\b(analy|result|performance|statistic|current.*rate)\b']
            },
            'optimize': {
                'fr': [r'\b(créer.*nouveau|comment.*créer|étapes.*création)\b'],
                'ar': [r'\b(إنشاء.*جديد|كيفية.*إنشاء|خطوات.*الإنشاء)\b'],
                'en': [r'\b(create.*new|how.*to.*create|steps.*creation)\b']
            }
        }
        
        patterns = off_topic_patterns.get(intent, {}).get(language, [])
        
        for pattern in patterns:
            if re.search(pattern, entry_answer_lower):
                penalty += 20
        
        return penalty

    def _generate_domain_specific_fallback(self, user_message, query_analysis, language):
        """Générer un fallback spécifique au domaine depuis la base de données"""
        # Rediriger vers la nouvelle méthode basée sur la base de données
        return self._get_database_fallback(query_analysis, language)

    def increment_usage(self):
        """Incrémenter le compteur d'usage"""
        self.usage_count += 1

    @api.model
    def get_marketing_insights(self):
        """Obtenir des insights marketing"""
        try:
            insights = {
                'total_campaigns': 0,
                'active_campaigns': [],
                'avg_open_rate': 0,
                'avg_reply_rate': 0,
                'total_sent': 0,
                'total_opened': 0,
                'total_replied': 0,
                'recommendations': []
            }
            
            # Essayer d'obtenir des données de mass_mailing si disponible
            if 'mailing.mailing' in self.env:
                try:
                    mailings = self.env['mailing.mailing'].search([])
                    
                    insights['total_campaigns'] = len(mailings)
                    
                    total_sent = sum(m.sent for m in mailings if m.sent > 0)
                    total_opened = sum(m.opened for m in mailings if m.opened > 0)
                    total_replied = sum(m.replied for m in mailings if m.replied > 0)
                    
                    insights.update({
                        'total_sent': total_sent,
                        'total_opened': total_opened,
                        'total_replied': total_replied,
                        'avg_open_rate': (total_opened / total_sent * 100) if total_sent > 0 else 0,
                        'avg_reply_rate': (total_replied / total_sent * 100) if total_sent > 0 else 0,
                    })
                    
                    # Campagnes actives
                    active_campaigns = mailings.filtered(lambda m: m.state in ['running', 'done'])
                    insights['active_campaigns'] = [{
                        'id': c.id,
                        'name': c.name,
                        'state': c.state,
                        'sent': c.sent,
                        'opened': c.opened,
                        'replied': c.replied
                    } for c in active_campaigns[:5]]
                    
                except Exception as e:
                    _logger.warning("Erreur accès mass_mailing: %s", e)
            
            return insights
            
        except Exception as e:
            _logger.error("Erreur get_marketing_insights: %s", e)
            return {'error': str(e)}

    @api.model
    def get_campaign_recommendations(self):
        """Générer des recommandations de campagne"""
        recommendations = []
        
        try:
            if 'mailing.mailing' in self.env:
                mailings = self.env['mailing.mailing'].search([
                    ('sent', '>', 0)
                ], limit=10, order='create_date desc')
                
                for mailing in mailings:
                    open_rate = (mailing.opened / mailing.sent * 100) if mailing.sent > 0 else 0
                    reply_rate = (mailing.replied / mailing.sent * 100) if mailing.sent > 0 else 0
                    
                    if open_rate < 15:
                        recommendations.append({
                            'type': 'warning',
                            'campaign_id': mailing.id,
                            'campaign_name': mailing.name,
                            'message': f"📉 Campagne '{mailing.name}' - Taux d'ouverture faible ({open_rate:.1f}%). Recommandation: Améliorer l'objet du mail.",
                            'action': 'improve_subject'
                        })
                    
                    if open_rate > 35:
                        recommendations.append({
                            'type': 'success',
                            'campaign_id': mailing.id,
                            'campaign_name': mailing.name,
                            'message': f"🎯 Campagne '{mailing.name}' - Excellent taux d'ouverture ({open_rate:.1f}%)! Répliquez cette stratégie.",
                            'action': 'replicate_strategy'
                        })
                    
                    if open_rate > 20 and reply_rate < 5:
                        recommendations.append({
                            'type': 'info',
                            'campaign_id': mailing.id,
                            'campaign_name': mailing.name,
                            'message': f"💡 Campagne '{mailing.name}' - Bon taux d'ouverture mais faible engagement. Améliorez le call-to-action.",
                            'action': 'improve_cta'
                        })
        
        except Exception as e:
            _logger.warning("Erreur génération recommandations: %s", e)
            # Recommandations génériques si pas d'accès aux données
            recommendations = [
                {
                    'type': 'info',
                    'message': "📊 Analysez régulièrement vos métriques de campagne pour identifier les opportunités d'amélioration.",
                    'action': 'analyze_metrics'
                },
                {
                    'type': 'info', 
                    'message': "🎯 Segmentez votre audience pour des messages plus personnalisés et un meilleur engagement.",
                    'action': 'segment_audience'
                },
                {
                    'type': 'info',
                    'message': "📧 Testez différents objets de mail pour optimiser vos taux d'ouverture.",
                    'action': 'test_subjects'
                }
            ]
        
        return recommendations[:5]  # Limiter à 5 recommandations

class AIKnowledgeKeyword(models.Model):
    _name = 'ai.knowledge.keyword'
    _description = 'Mots-clés pour la base de connaissances AI'
    _rec_name = 'keyword'

    keyword = fields.Char(
        string='Mot-clé',
        required=True,
        help='Mot-clé principal'
    )
    
    variants = fields.Text(
        string='Variantes',
        help='Variantes et synonymes du mot-clé (séparés par des virgules)'
    )
    
    language = fields.Selection([
        ('fr', 'Français'),
        ('en', 'English'),
        ('ar', 'العربية')
    ], string='Langue', default='fr', required=True)
    
    category = fields.Selection([
        ('marketing', 'Marketing'),
        ('email', 'Email'),
        ('campaign', 'Campagne'),
        ('performance', 'Performance'),
        ('analytics', 'Analytics'),
        ('general', 'Général')
    ], string='Catégorie', default='general')
    
    weight = fields.Float(
        string='Poids',
        default=1.0,
        help='Poids du mot-clé dans les calculs de pertinence'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True
    )

    @api.model
    def get_keyword_variants(self, keyword):
        """Récupérer les variantes d'un mot-clé"""
        variants_map = {
            # Français
            'performance': ['performance', 'résultat', 'efficacité', 'rendement', 'productivité'],
            'campagne': ['campagne', 'publicité', 'advertising', 'promotion', 'marketing'],
            'email': ['email', 'mail', 'courriel', 'newsletter', 'emailing'],
            'taux': ['taux', 'pourcentage', 'ratio', 'métrique', 'indicateur'],
            'ouverture': ['ouverture', 'open', 'lecture', 'consultation', 'vue'],
            'clic': ['clic', 'click', 'clique', 'interaction', 'engagement'],
            'conversion': ['conversion', 'vente', 'achat', 'transformation', 'action'],
            'roi': ['roi', 'retour', 'rentabilité', 'bénéfice', 'profit'],
            'analyse': ['analyse', 'analytique', 'statistique', 'rapport', 'données'],
            'optimisation': ['optimisation', 'amélioration', 'enhancement', 'perfectionnement'],
            
            # English
            'campaign': ['campaign', 'advertising', 'promotion', 'marketing'],
            'rate': ['rate', 'percentage', 'ratio', 'metric'],
            'open': ['open', 'opening', 'view', 'read'],
            'click': ['click', 'clicking', 'interaction'],
            'analysis': ['analysis', 'analytics', 'statistics', 'report', 'data'],
            'optimization': ['optimization', 'improvement', 'enhancement'],
            
            # العربية
            'حملة': ['حملة', 'إعلان', 'ترويج', 'دعاية'],
            'معدل': ['معدل', 'نسبة', 'مقياس'],
            'فتح': ['فتح', 'قراءة', 'اطلاع'],
            'نقر': ['نقر', 'ضغط', 'تفاعل'],
            'تحليل': ['تحليل', 'إحصائية', 'تقرير', 'بيانات'],
            'تحسين': ['تحسين', 'تطوير', 'تحسن']
        }
        
        return variants_map.get(keyword.lower(), [keyword])

    @api.model
    def create_default_keywords(self):
        """Créer les mots-clés par défaut"""
        default_keywords = [
            # Français
            {'keyword': 'performance', 'variants': 'performance,résultat,efficacité,rendement,productivité', 'language': 'fr', 'category': 'performance'},
            {'keyword': 'campagne', 'variants': 'campagne,publicité,advertising,promotion,marketing', 'language': 'fr', 'category': 'campaign'},
            {'keyword': 'email', 'variants': 'email,mail,courriel,newsletter,emailing', 'language': 'fr', 'category': 'email'},
            {'keyword': 'taux', 'variants': 'taux,pourcentage,ratio,métrique,indicateur', 'language': 'fr', 'category': 'analytics'},
            {'keyword': 'ouverture', 'variants': 'ouverture,open,lecture,consultation,vue', 'language': 'fr', 'category': 'email'},
            {'keyword': 'clic', 'variants': 'clic,click,clique,interaction,engagement', 'language': 'fr', 'category': 'email'},
            {'keyword': 'conversion', 'variants': 'conversion,vente,achat,transformation,action', 'language': 'fr', 'category': 'performance'},
            {'keyword': 'roi', 'variants': 'roi,retour,rentabilité,bénéfice,profit', 'language': 'fr', 'category': 'performance'},
            {'keyword': 'analyse', 'variants': 'analyse,analytique,statistique,rapport,données', 'language': 'fr', 'category': 'analytics'},
            {'keyword': 'optimisation', 'variants': 'optimisation,amélioration,enhancement,perfectionnement', 'language': 'fr', 'category': 'marketing'},
            
            # English
            {'keyword': 'campaign', 'variants': 'campaign,advertising,promotion,marketing', 'language': 'en', 'category': 'campaign'},
            {'keyword': 'performance', 'variants': 'performance,result,efficiency,effectiveness', 'language': 'en', 'category': 'performance'},
            {'keyword': 'email', 'variants': 'email,mail,newsletter,mailing', 'language': 'en', 'category': 'email'},
            {'keyword': 'rate', 'variants': 'rate,percentage,ratio,metric', 'language': 'en', 'category': 'analytics'},
            {'keyword': 'open', 'variants': 'open,opening,view,read', 'language': 'en', 'category': 'email'},
            {'keyword': 'click', 'variants': 'click,clicking,interaction', 'language': 'en', 'category': 'email'},
            {'keyword': 'conversion', 'variants': 'conversion,sale,purchase,transformation', 'language': 'en', 'category': 'performance'},
            {'keyword': 'roi', 'variants': 'roi,return,profitability,profit', 'language': 'en', 'category': 'performance'},
            {'keyword': 'analysis', 'variants': 'analysis,analytics,statistics,report,data', 'language': 'en', 'category': 'analytics'},
            {'keyword': 'optimization', 'variants': 'optimization,improvement,enhancement', 'language': 'en', 'category': 'marketing'},
        ]
        
        for keyword_data in default_keywords:
            existing = self.search([
                ('keyword', '=', keyword_data['keyword']),
                ('language', '=', keyword_data['language'])
            ])
            
            if not existing:
                self.create(keyword_data)

class AIChatSession(models.Model):
    _name = 'ai.chat.session'
    _description = 'Session de Chat AI'
    _order = 'start_time desc'

    name = fields.Char(string='Nom de la session', required=True)
    user_id = fields.Many2one('res.users', string='Utilisateur', required=True, default=lambda self: self.env.user)
    start_time = fields.Datetime(string='Heure de début', default=fields.Datetime.now)
    last_activity = fields.Datetime(string='Dernière activité', default=fields.Datetime.now)
    state = fields.Selection([
        ('active', 'Actif'),
        ('closed', 'Fermé')
    ], string='État', default='active')
    
    session_type = fields.Selection([
        ('marketing', 'Marketing'),
        ('support', 'Support'),
        ('general', 'Général')
    ], string='Type de session', default='general')
    
    message_ids = fields.One2many('ai.chat.message', 'session_id', string='Messages')
    message_count = fields.Integer(string='Nombre de messages', compute='_compute_message_count')
    metadata = fields.Text(string='Métadonnées', help="Données JSON pour contexte supplémentaire")

    @api.depends('message_ids')
    def _compute_message_count(self):
        for session in self:
            session.message_count = len(session.message_ids)

    def action_view_messages(self):
        """Action pour voir les messages de cette session"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Messages - {self.name}',
            'res_model': 'ai.chat.message',
            'view_mode': 'list,form',
            'domain': [('session_id', '=', self.id)],
            'context': {'default_session_id': self.id}
        }

class AIChatMessage(models.Model):
    _name = 'ai.chat.message'
    _description = 'Message de Chat AI'
    _order = 'timestamp desc'

    session_id = fields.Many2one('ai.chat.session', string='Session', required=True, ondelete='cascade')
    message_type = fields.Selection([
        ('user', 'Utilisateur'),
        ('bot', 'Bot AI')
    ], string='Type de message', required=True)
    
    message = fields.Text(string='Message', required=True)
    user_id = fields.Many2one('res.users', string='Utilisateur', required=True, default=lambda self: self.env.user)
    timestamp = fields.Datetime(string='Horodatage', default=fields.Datetime.now)
    response_time = fields.Float(string='Temps de réponse (s)', help="Temps de réponse en secondes")
    confidence_score = fields.Float(string='Score de confiance', help="Score de confiance de la réponse IA")
    metadata = fields.Text(string='Métadonnées', help="Données JSON supplémentaires")

    @api.model
    def create_chat_response(self, user_message, session_id, language='en'):
        """Créer une réponse de chat avec IA améliorée et respect de la langue"""
        start_time = datetime.now()
        
        try:
            # Enregistrer le message utilisateur
            user_msg = self.create({
                'session_id': session_id,
                'message_type': 'user',
                'message': user_message,
                'user_id': self.env.user.id,
                'timestamp': start_time
            })
            
            # Détecter la langue de façon obligatoire pour assurer la cohérence
            detected_language = self._detect_language(user_message)
            
            # Utiliser la langue détectée en priorité sur celle fournie
            final_language = detected_language if detected_language else (language or 'en')
            
            _logger.info("Message: '%s' | Langue détectée: '%s' | Langue finale: '%s'", user_message, detected_language, final_language)
            
            # Analyser la requête pour extraire l'intention et les entités
            query_analysis = self.env['ai.knowledge.base']._extract_intent_and_entities(user_message, final_language)
            
            # Rechercher dans la base de connaissances avec langue stricte
            knowledge_entries = self.env['ai.knowledge.base'].search_knowledge(
                user_message, 
                language=final_language,
                limit=5  # Augmenter pour plus d'options
            )
            
            response_data = {}
            
            if knowledge_entries:
                best_match = knowledge_entries[0]
                
                # VALIDATION FINALE DE PERTINENCE
                relevance_check = self._validate_response_relevance(
                    user_message, best_match, query_analysis, final_language
                )
                
                if not relevance_check['is_relevant']:
                    # Si pas pertinent, chercher une alternative ou utiliser fallback
                    _logger.info("Réponse non pertinente détectée, recherche alternative...")
                    
                    # Essayer avec des critères plus stricts
                    alternative_entries = self.env['ai.knowledge.base'].search_knowledge(
                        user_message,
                        language=final_language,
                        category=query_analysis['intent'].replace('get_', '').replace('create_', ''),
                        limit=3
                    )
                    
                    best_alternative = None
                    for entry in alternative_entries:
                        alt_check = self._validate_response_relevance(
                            user_message, entry, query_analysis, final_language
                        )
                        if alt_check['is_relevant']:
                            best_alternative = entry
                            break
                    
                    if best_alternative:
                        best_match = best_alternative
                        confidence = 0.75
                    else:
                        # Utiliser fallback intelligent spécifique au domaine DE LA BASE DE DONNÉES
                        response_message = self._get_database_fallback(
                            query_analysis, final_language
                        )
                        confidence = 0.4
                        quick_actions = self._get_language_specific_quick_actions(final_language)
                        
                        response_data = {
                            'detected_language': detected_language,
                            'final_language': final_language,
                            'fallback': True,
                            'fallback_type': 'database_domain_specific',
                            'confidence': confidence,
                            'quick_actions': quick_actions,
                            'intent': query_analysis['intent'],
                            'source': 'database_fallback'
                        }
                        
                        # Enregistrer directement le fallback et retourner
                        response_time = (datetime.now() - start_time).total_seconds()
                        bot_msg = self.create({
                            'session_id': session_id,
                            'message_type': 'bot',
                            'message': response_message,
                            'user_id': self.env.user.id,
                            'timestamp': datetime.now(),
                            'response_time': response_time,
                            'confidence_score': confidence,
                            'metadata': json.dumps(response_data)
                        })
                        
                        return {
                            'response': response_message,
                            'user_message_id': user_msg.id,
                            'bot_message_id': bot_msg.id,
                            **response_data
                        }
                
                # Vérifier que la réponse est dans la bonne langue
                if best_match.language != final_language and best_match.language != 'multi':
                    # Si la langue ne correspond pas, chercher spécifiquement dans cette langue
                    lang_specific = self.env['ai.knowledge.base'].search_knowledge(
                        user_message,
                        language=final_language,
                        limit=1
                    )
                    if lang_specific:
                        best_match = lang_specific[0]
                
                best_match.increment_usage()
                
                # Formater la réponse avec données dynamiques
                response_message = self._format_response_with_data(
                    best_match.answer, 
                    best_match.category
                )
                
                # S'assurer que la réponse finale est dans la bonne langue
                if not self._is_response_in_correct_language(response_message, final_language):
                    response_message = self._translate_or_fallback_response(
                        response_message, 
                        final_language,
                        user_message
                    )
                
                confidence = relevance_check['confidence_score']
                quick_actions = self._get_language_specific_quick_actions(final_language)
                
                response_data = {
                    'knowledge_base_id': best_match.id,
                    'detected_language': detected_language,
                    'final_language': final_language,
                    'category': best_match.category,
                    'confidence': confidence,
                    'quick_actions': quick_actions,
                    'source_language': best_match.language
                }
            else:
                # Réponse de fallback intelligente DE LA BASE DE DONNÉES
                response_message = self._get_database_fallback(query_analysis, final_language)
                confidence = 0.2
                quick_actions = self._get_language_specific_quick_actions(final_language)
                
                response_data = {
                    'detected_language': detected_language,
                    'final_language': final_language,
                    'fallback': True,
                    'fallback_type': 'database_general',
                    'confidence': confidence,
                    'quick_actions': quick_actions,
                    'source': 'database_fallback'
                }
            
            # Calculer le temps de réponse
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Enregistrer la réponse du bot
            bot_msg = self.create({
                'session_id': session_id,
                'message_type': 'bot',
                'message': response_message,
                'user_id': self.env.user.id,
                'timestamp': datetime.now(),
                'response_time': response_time,
                'confidence_score': confidence,
                'metadata': json.dumps(response_data)
            })
            
            return {
                'response': response_message,
                'user_message_id': user_msg.id,
                'bot_message_id': bot_msg.id,
                **response_data
            }
            
        except Exception as e:
            _logger.error("Erreur create_chat_response: %s", e, exc_info=True)
            # Assurer que même les messages d'erreur sont dans la bonne langue
            error_language = self._detect_language(user_message) if user_message else 'en'
            return {
                'response': self._get_error_message(error_language),
                'error': True,
                'detected_language': error_language,
                'quick_actions': self._get_language_specific_quick_actions(error_language)
            }

    def _format_response_with_data(self, template_response, category):
        """Formater la réponse avec des données réelles"""
        try:
            if '{' in template_response:
                # Obtenir les insights marketing réels
                insights = self.env['ai.knowledge.base'].get_marketing_insights()
                formatted_response = template_response.format(**insights)
                return formatted_response
        except Exception:
            pass
        
        return template_response

    def _parse_quick_actions(self, quick_actions_json):
        """Parser les actions rapides du JSON"""
        try:
            if quick_actions_json:
                return json.loads(quick_actions_json)
        except (json.JSONDecodeError, TypeError):
            pass
        return []

    def _get_default_quick_actions(self, language):
        """Actions rapides par défaut selon la langue (compatibilité)"""
        return self._get_language_specific_quick_actions(language)

    def _get_language_specific_quick_actions(self, language):
        """Actions rapides spécifiques à chaque langue avec plus d'options"""
        actions_map = {
            'ar': [
                {'text': 'نظرة عامة', 'action': 'marketing_overview'},
                {'text': 'أداء الحملات', 'action': 'view_campaigns'},
                {'text': 'تحليل العائد', 'action': 'get_analytics'},
                {'text': 'التوصيات', 'action': 'get_improvement_suggestions'}
            ],
            'fr': [
                {'text': 'Apercu marketing', 'action': 'marketing_overview'},
                {'text': 'Performance campagnes', 'action': 'view_campaigns'},
                {'text': 'Analytics ROI', 'action': 'get_analytics'},
                {'text': 'Recommandations', 'action': 'get_improvement_suggestions'}
            ],
            'en': [
                {'text': 'Marketing Overview', 'action': 'marketing_overview'},
                {'text': 'Campaign Performance', 'action': 'view_campaigns'},
                {'text': 'ROI Analytics', 'action': 'get_analytics'},
                {'text': 'Recommendations', 'action': 'get_improvement_suggestions'}
            ]
        }
        
        return actions_map.get(language, actions_map['en'])

    def _is_response_in_correct_language(self, response, expected_language):
        """Vérifier si la réponse est dans la langue attendue"""
        if not response or not expected_language:
            return True
            
        # Vérifier la présence de caractères spécifiques à chaque langue
        import re
        
        if expected_language == 'ar':
            # Vérifier la présence de caractères arabes
            return bool(re.search(r'[\u0600-\u06FF]', response))
        elif expected_language == 'fr':
            # Vérifier des patterns français
            french_patterns = [
                r'\b(le|la|les|de|du|des|et|est|une|un)\b',
                r'\b(avec|sur|dans|pour|par|sans)\b',
                r'\b(bonjour|salut|merci|désolé)\b'
            ]
            return any(re.search(pattern, response.lower()) for pattern in french_patterns)
        elif expected_language == 'en':
            # Vérifier des patterns anglais
            english_patterns = [
                r'\b(the|and|or|but|in|on|at|for|with)\b',
                r'\b(hello|hi|thank|sorry|please)\b',
                r'\b(campaign|marketing|analysis|performance)\b'
            ]
            return any(re.search(pattern, response.lower()) for pattern in english_patterns)
        
        return True  # Par défaut, accepter la réponse

    def _translate_or_fallback_response(self, response, target_language, original_query):
        """Traduire ou fournir une réponse de fallback dans la langue cible"""
        # Utiliser les paramètres pour éviter les warnings (même si non utilisés pour le moment)
        _ = response, original_query
        
        # Pour l'instant, fournir une réponse de fallback appropriée
        fallback_responses = {
            'ar': """🤖 عذراً، المعلومات متوفرة ولكن أحتاج إلى صياغة الإجابة بشكل أفضل.
            
يمكنني مساعدتك في:
• تحليل الحملات التسويقية
• عرض الإحصائيات والمقاييس  
• تقديم التوصيات والاقتراحات
• تحسين أداء التسويق

يرجى إعادة صياغة السؤال أو اختيار من الخيارات أدناه.""",
            
            'fr': """🤖 Desole, j'ai des informations disponibles mais je dois mieux formuler ma reponse.
            
Je peux vous aider avec :
• Analyse des campagnes marketing
• Affichage des statistiques et metriques
• Recommandations et suggestions
• Optimisation des performances marketing

Veuillez reformuler votre question ou choisir une option ci-dessous.""",
            
            'en': """🤖 Sorry, I have information available but need to better formulate my response.
            
I can help you with:
• Marketing campaign analysis
• Statistics and metrics display
• Recommendations and suggestions  
• Marketing performance optimization

Please rephrase your question or choose an option below."""
        }
        
        return fallback_responses.get(target_language, fallback_responses['en'])

    def _get_database_fallback(self, query_analysis, language):
        """Récupérer un fallback depuis la base de données selon l'intention"""
        intent = query_analysis['intent']
        
        # Mapping intentions vers questions fallback dans la base
        fallback_queries = {
            'get_performance': 'fallback_performance',
            'get_analysis': 'fallback_analysis', 
            'create_campaign': 'fallback_creation',
            'optimize': 'fallback_optimization',
            'get_help': 'fallback_general'
        }
        
        # Déterminer la question fallback appropriée
        fallback_query = fallback_queries.get(intent, 'fallback_general')
        
        # Rechercher dans la base de données
        domain = [
            ('is_active', '=', True),
            ('question', '=', fallback_query),
            ('language', 'in', [language, 'multi'])
        ]
        
        fallback_entries = self.search(domain, limit=1)
        
        if fallback_entries:
            # Utiliser le fallback spécifique de la base
            return fallback_entries[0].answer
        else:
            # Si pas de fallback dans la base, utiliser le fallback général
            general_domain = [
                ('is_active', '=', True),
                ('question', '=', 'fallback_general'),
                ('language', 'in', [language, 'multi'])
            ]
            
            general_entries = self.search(general_domain, limit=1)
            
            if general_entries:
                return general_entries[0].answer
            else:
                # Dernière option : message minimal depuis base (pas hardcodé)
                return self._get_minimal_database_response(language)

    def _get_minimal_database_response(self, language):
        """Obtenir une réponse minimale depuis la base de données"""
        # Chercher n'importe quelle entrée active dans la langue pour avoir au moins quelque chose
        domain = [
            ('is_active', '=', True),
            ('language', 'in', [language, 'multi']),
            ('category', '=', 'general')
        ]
        
        any_entry = self.search(domain, limit=1)
        
        if any_entry:
            return f"<p>🤖 Assistant disponible. Question non trouvée dans ma base de données.</p><p>Reformulez votre question pour obtenir une réponse précise.</p>"
        else:
            # Absolument dernière option si aucune entrée dans la base
            return "<p>🤖 Base de données en cours de chargement. Veuillez réessayer.</p>"

    def _generate_smart_fallback(self, user_message, language):
        """Méthode maintenant basée sur la base de données - plus de hardcode"""
        # Rediriger vers la méthode basée sur la base de données
        query_analysis = self._extract_intent_and_entities(user_message, language)
        return self._get_database_fallback(query_analysis, language)

    def _get_error_message(self, language):
        """Messages d'erreur selon la langue"""
        error_messages = {
            'ar': "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
            'fr': "Désolé, une erreur est survenue. Veuillez réessayer.",
            'en': "Sorry, an error occurred. Please try again."
        }
        
        return error_messages.get(language, error_messages['en'])

    def _detect_language(self, message):
        """Détecter la langue du message de manière avancée"""
        import re
        
        message_lower = message.lower().strip()
        
        # Vérifier d'abord l'arabe (caractères unicode)
        if re.search(r'[\u0600-\u06FF]', message):
            return 'ar'
        
        # Mots-clés français étendus avec pondération
        french_indicators = {
            # Salutations
            'bonjour': 3, 'salut': 3, 'bonsoir': 3, 'bonne': 2,
            # Articles et prépositions communes
            'le': 1, 'la': 1, 'les': 1, 'de': 1, 'du': 1, 'des': 1, 
            'et': 1, 'est': 1, 'une': 1, 'un': 1, 'pour': 1, 'avec': 1, 
            'sur': 1, 'dans': 1, 'par': 1, 'sans': 1,
            # Verbes français courants
            'être': 2, 'avoir': 2, 'faire': 2, 'aller': 2, 'voir': 2,
            'savoir': 2, 'pouvoir': 2, 'vouloir': 2, 'venir': 2,
            # Mots spécifiques au marketing
            'campagne': 3, 'marketing': 3, 'analyse': 3, 'performance': 3,
            'statistiques': 3, 'données': 3, 'rapport': 3, 'résultats': 3,
            # Interrogatifs français
            'comment': 2, 'pourquoi': 2, 'quand': 2, 'où': 2, 'que': 1, 'qui': 1, 'quoi': 2,
            # Mots courants
            'très': 2, 'bien': 2, 'plus': 1, 'moins': 1, 'tout': 1, 'tous': 1,
            'peut': 2, 'peux': 2, 'dois': 2, 'veux': 2
        }
        
        # Mots-clés anglais étendus avec pondération
        english_indicators = {
            # Salutations
            'hello': 3, 'hi': 3, 'hey': 3, 'good': 2,
            # Articles et prépositions
            'the': 1, 'and': 1, 'or': 1, 'but': 1, 'in': 1, 'on': 1, 'at': 1,
            'for': 1, 'with': 1, 'by': 1, 'from': 1, 'to': 1, 'of': 1,
            # Verbes anglais courants
            'have': 1, 'has': 1, 'had': 1, 'is': 1, 'are': 1, 'was': 1, 'were': 1,
            'do': 1, 'does': 1, 'did': 1, 'will': 1, 'would': 1, 'could': 1, 'should': 1,
            # Mots spécifiques au marketing
            'campaign': 3, 'marketing': 3, 'analysis': 3, 'performance': 3,
            'statistics': 3, 'data': 3, 'report': 3, 'results': 3,
            # Interrogatifs anglais
            'how': 2, 'why': 2, 'when': 2, 'where': 2, 'what': 2, 'who': 2, 'which': 2,
            # Mots courants
            'very': 2, 'really': 2, 'more': 1, 'less': 1, 'all': 1, 'some': 1,
            'can': 2, 'may': 2, 'must': 2, 'need': 2, 'want': 2, 'get': 1, 'show': 2
        }
        
        # Mots-clés arabes (translittérés) avec pondération
        arabic_indicators = {
            # Salutations arabes communes (en caractères latins pour les cas mixtes)
            'marhaba': 3, 'ahlan': 3, 'salam': 3, 'sabah': 2, 'masa': 2,
            # Mots marketing en arabe translittéré
            'tasweeq': 3, 'hamla': 3, 'tahliil': 3, 'ada': 3,
            # Interrogatifs arabes
            'kayf': 2, 'mata': 2, 'ayn': 2, 'matha': 2, 'man': 2, 'limatha': 2,
            # Mots courants
            'kol': 1, 'koll': 1, 'min': 1, 'ila': 1, 'fi': 1, 'ala': 1
        }
        
        # Calculer les scores pour chaque langue
        french_score = 0
        english_score = 0
        arabic_score = 0
        
        words = re.findall(r'\b\w+\b', message_lower)
        
        for word in words:
            if word in french_indicators:
                french_score += french_indicators[word]
            if word in english_indicators:
                english_score += english_indicators[word]
            if word in arabic_indicators:
                arabic_score += arabic_indicators[word]
        
        # Bonus pour les patterns typiques de chaque langue
        
        # Patterns français
        if re.search(r'\b(qu\'|j\'|l\'|n\'|d\'|c\'|m\'|t\'|s\')', message_lower):
            french_score += 2
        if re.search(r'\b(tion|sion|ment|ence|ance)\b', message_lower):
            french_score += 1
        
        # Patterns anglais
        if re.search(r'\b(\'m|\'re|\'ve|\'ll|\'d|n\'t)\b', message_lower):
            english_score += 2
        if re.search(r'\b(ing|ed|er|est|ly)\b', message_lower):
            english_score += 1
        
        # Déterminer la langue avec le score le plus élevé
        max_score = max(french_score, english_score, arabic_score)
        
        if max_score == 0:
            # Aucun indicateur trouvé, utiliser des heuristiques supplémentaires
            if len(message) > 0 and ord(message[0]) > 127:
                return 'ar'  # Caractères non-ASCII, probablement arabe
            return 'en'  # Par défaut anglais
        
        if arabic_score == max_score:
            return 'ar'
        elif french_score == max_score:
            return 'fr'
        else:
            return 'en'

    @api.model  
    def get_marketing_insights(self):
        """Proxy vers la méthode de ai.knowledge.base"""
        return self.env['ai.knowledge.base'].get_marketing_insights()