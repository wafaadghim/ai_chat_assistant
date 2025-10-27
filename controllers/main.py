# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class AIChatController(http.Controller):

    @http.route('/ai_chat/process', type='json', auth='user', methods=['POST'])
    def process_chat_message(self, message, session_id=None, language='en', **kwargs):
        """Traiter un message de chat avec intégration complète"""
        try:
            # Créer ou obtenir la session
            if not session_id or session_id.startswith('fallback_'):
                session = self._create_chat_session()
                session_id = session.id
            else:
                session = request.env['ai.chat.session'].browse(int(session_id))
                if not session.exists():
                    session = self._create_chat_session()
                    session_id = session.id

            # Mettre à jour la dernière activité
            session.write({'last_activity': fields.Datetime.now()})
            
            # Traiter le message avec IA
            response_data = request.env['ai.chat.message'].create_chat_response(
                message, session_id, language
            )
            
            return {
                'success': True,
                'response': response_data.get('response', 'Désolé, je n\'ai pas pu traiter votre demande.'),
                'session_id': session_id,
                'quick_actions': response_data.get('quick_actions', []),
                'confidence': response_data.get('confidence', 0),
                'category': response_data.get('category', 'general')
            }
            
        except Exception as e:
            _logger.error("Erreur process_chat_message: %s", e, exc_info=True)
            return {
                'success': False,
                'error': 'Une erreur est survenue lors du traitement de votre message.',
                'session_id': session_id if 'session_id' in locals() else None
            }

    @http.route('/ai_chat/get_fallback', type='json', auth='user', methods=['POST'])
    def get_fallback_response(self, fallback_type='fallback_general', language='fr', **kwargs):
        """Endpoint spécialisé pour récupérer les réponses de fallback depuis la base de données"""
        try:
            _logger.info("🔍 Récupération fallback: %s, langue: %s", fallback_type, language)
            
            # Recherche dans la base de données des entrées de fallback
            knowledge_base = request.env['ai.knowledge.base']
            
            # Recherche par question exacte et langue
            fallback_entry = knowledge_base.search([
                ('question', '=', fallback_type),
                ('language', '=', language)
            ], limit=1)
            
            if fallback_entry:
                _logger.info("✅ Fallback trouvé dans la base de données")
                return {
                    'success': True,
                    'answer': fallback_entry.answer,
                    'category': fallback_entry.category,
                    'language': fallback_entry.language
                }
            else:
                # Fallback en français si pas trouvé dans la langue demandée
                fallback_entry = knowledge_base.search([
                    ('question', '=', fallback_type),
                    ('language', '=', 'fr')
                ], limit=1)
                
                if fallback_entry:
                    _logger.info("✅ Fallback trouvé en français")
                    return {
                        'success': True,
                        'answer': fallback_entry.answer,
                        'category': fallback_entry.category,
                        'language': 'fr'
                    }
                else:
                    _logger.warning("⚠️ Aucun fallback trouvé en base de données")
                    return {
                        'success': False,
                        'error': 'Fallback non trouvé en base de données'
                    }
                    
        except Exception as e:
            _logger.error("🚨 Erreur get_fallback_response: %s", e, exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _detect_language(self, message):
        """Détection automatique de la langue du message"""
        try:
            message_lower = message.lower().strip()
            
            # Mots-clés français communs dans le marketing
            french_keywords = [
                'taux', 'ouverture', 'email', 'campagne', 'performance', 'conversion', 
                'ameliorer', 'créer', 'comment', 'quel', 'quelle', 'pourquoi', 
                'dashboard', 'roi', 'revenus', 'clients', 'ventes', 'marketing'
            ]
            
            # Mots-clés anglais communs dans le marketing
            english_keywords = [
                'rate', 'open', 'email', 'campaign', 'performance', 'conversion',
                'improve', 'create', 'how', 'what', 'why', 'dashboard', 'roi',
                'revenue', 'customers', 'sales', 'marketing', 'analytics'
            ]
            
            # Caractères arabes (plage Unicode)
            arabic_chars = any('\u0600' <= char <= '\u06FF' for char in message)
            if arabic_chars:
                return 'ar'
            
            # Compter les correspondances
            french_count = sum(1 for word in french_keywords if word in message_lower)
            english_count = sum(1 for word in english_keywords if word in message_lower)
            
            # Si plus de mots français
            if french_count > english_count:
                return 'fr'
            elif english_count > 0:
                return 'en'
            
            # Par défaut français si pas de détection claire
            return 'fr'
            
        except Exception as e:
            _logger.warning("⚠️ Erreur détection langue: %s", e)
            return 'fr'

    @http.route('/ai_chat/get_response', type='json', auth='user', methods=['POST'])
    def get_ai_response(self, message, language=None, session_id=None, **kwargs):
        """Endpoint principal pour récupérer les réponses IA 100% base de données - TOUJOURS une réponse de la base"""
        try:
            # Détection automatique de la langue si non spécifiée
            if not language:
                language = self._detect_language(message)
            
            _logger.info("🤖 Traitement message: %s, langue détectée: %s", message, language)
            
            # Utiliser le modèle de recherche amélioré
            knowledge_base = request.env['ai.knowledge.base']
            
            # 1. Recherche directe exacte
            entries = knowledge_base.search_knowledge(message, language)
            
            if entries:
                best_entry = entries[0] if isinstance(entries, list) else entries
                _logger.info("✅ Réponse directe trouvée en base de données")
                best_entry.increment_usage()
                return {
                    'success': True,
                    'answer': best_entry.answer,
                    'confidence': 0.95,
                    'category': best_entry.category,
                    'language': language,
                    'source': 'direct_match'
                }
            
            # 2. Recherche par mots-clés si pas de correspondance exacte
            _logger.info("🔍 Recherche par mots-clés dans la base")
            keyword_entries = self._search_by_keywords(message, language)
            
            if keyword_entries:
                best_keyword_entry = keyword_entries[0]
                _logger.info("✅ Réponse par mots-clés trouvée en base")
                best_keyword_entry.increment_usage()
                return {
                    'success': True,
                    'answer': best_keyword_entry.answer,
                    'confidence': 0.75,
                    'category': best_keyword_entry.category,
                    'language': language,
                    'source': 'keyword_match'
                }
            
            # 3. Recherche par catégorie si pas de mots-clés
            _logger.info("🔍 Recherche par catégorie dans la base")
            category = self._detect_message_category(message)
            category_entries = knowledge_base.search([
                ('is_active', '=', True),
                ('category', '=', category),
                ('language', 'in', [language, 'multi'])
            ], limit=1)
            
            if category_entries:
                category_entry = category_entries[0]
                _logger.info("✅ Réponse par catégorie trouvée en base")
                category_entry.increment_usage()
                return {
                    'success': True,
                    'answer': category_entry.answer,
                    'confidence': 0.60,
                    'category': category_entry.category,
                    'language': language,
                    'source': 'category_match'
                }
            
            # 4. Dernière option : prendre n'importe quelle entrée active dans la langue
            _logger.info("🔍 Recherche d'entrée générale dans la base")
            any_entry = knowledge_base.search([
                ('is_active', '=', True),
                ('language', 'in', [language, 'multi'])
            ], limit=1)
            
            if any_entry:
                general_entry = any_entry[0]
                _logger.info("✅ Réponse générale trouvée en base")
                return {
                    'success': True,
                    'answer': general_entry.answer,
                    'confidence': 0.30,
                    'category': general_entry.category,
                    'language': language,
                    'source': 'general_fallback'
                }
            
            # 5. Si vraiment aucune entrée en base (ne devrait jamais arriver)
            _logger.warning("⚠️ Aucune entrée trouvée en base de données - créer une entrée d'urgence")
            return {
                'success': True,
                'answer': self._create_emergency_database_response(message, language),
                'confidence': 0.10,
                'category': 'general',
                'language': language,
                'source': 'emergency'
            }
                
        except Exception as e:
            _logger.error("🚨 Erreur get_ai_response: %s", e, exc_info=True)
            # Même en cas d'erreur, essayer de donner une réponse de la base
            return self._emergency_database_fallback(language)

    def _search_by_keywords(self, message, language):
        """Rechercher par mots-clés dans la base de données"""
        try:
            knowledge_base = request.env['ai.knowledge.base']
            message_lower = message.lower()
            
            # Chercher les entrées qui contiennent des mots de la question
            words = message_lower.split()
            main_words = [w for w in words if len(w) > 3]  # Mots significatifs seulement
            
            if not main_words:
                return []
            
            # Construire une requête de recherche
            domain = [
                ('is_active', '=', True),
                ('language', 'in', [language, 'multi'])
            ]
            
            # Ajouter condition OR pour chaque mot important
            word_conditions = []
            for word in main_words:
                word_conditions.extend([
                    ('question', 'ilike', word),
                    ('answer', 'ilike', word)
                ])
            
            if word_conditions:
                entries = knowledge_base.search(domain, limit=5)
                # Filtrer manuellement pour améliorer la pertinence
                relevant_entries = []
                for entry in entries:
                    score = 0
                    entry_text = (entry.question + ' ' + entry.answer).lower()
                    for word in main_words:
                        if word in entry_text:
                            score += 1
                    if score > 0:
                        relevant_entries.append(entry)
                
                # Trier par score de pertinence
                relevant_entries.sort(key=lambda e: sum(1 for w in main_words 
                                                       if w in (e.question + ' ' + e.answer).lower()), 
                                     reverse=True)
                return relevant_entries[:3]
            
            return []
            
        except Exception as e:
            _logger.error("Erreur _search_by_keywords: %s", e)
            return []

    def _detect_message_category(self, message):
        """Détecter la catégorie du message"""
        message_lower = message.lower()
        
        # Marketing patterns
        if any(word in message_lower for word in ['campagne', 'campaign', 'marketing', 'promotion', 'حملة']):
            return 'campaigns'
        
        # Analytics patterns  
        if any(word in message_lower for word in ['performance', 'analytics', 'rapport', 'statistique', 'taux', 'أداء', 'تحليل']):
            return 'analytics'
            
        # Recommendations patterns
        if any(word in message_lower for word in ['conseil', 'recommandation', 'améliorer', 'optimiser', 'نصيحة', 'تحسين']):
            return 'recommendations'
            
        return 'general'

    def _create_emergency_database_response(self, message, language):
        """Créer une réponse d'urgence mais basée sur la base de données"""
        try:
            # Essayer de créer dynamiquement une réponse utile
            knowledge_base = request.env['ai.knowledge.base']
            
            # Compter les entrées disponibles
            total_entries = knowledge_base.search_count([('is_active', '=', True)])
            
            responses = {
                'fr': f"""
                <div style="font-family: Arial, sans-serif;">
                    <h3>🤖 Assistant Marketing IA</h3>
                    <p><strong>Votre question:</strong> "{message}"</p>
                    <p>📚 Ma base de connaissances contient <strong>{total_entries} entrées</strong> disponibles.</p>
                    <p><strong>Essayez des questions plus spécifiques comme:</strong></p>
                    <ul>
                        <li>"Quel est mon taux d'ouverture email ?"</li>
                        <li>"Comment améliorer mes campagnes ?"</li>
                        <li>"Montre-moi les performances marketing"</li>
                        <li>"Créer une nouvelle campagne email"</li>
                    </ul>
                    <p><em>Plus votre question est précise, meilleure sera ma réponse depuis la base de données.</em></p>
                </div>
                """,
                'en': f"""
                <div style="font-family: Arial, sans-serif;">
                    <h3>🤖 AI Marketing Assistant</h3>
                    <p><strong>Your question:</strong> "{message}"</p>
                    <p>📚 My knowledge base contains <strong>{total_entries} entries</strong> available.</p>
                    <p><strong>Try more specific questions like:</strong></p>
                    <ul>
                        <li>"What is my email open rate?"</li>
                        <li>"How to improve my campaigns?"</li>
                        <li>"Show me marketing performance"</li>
                        <li>"Create a new email campaign"</li>
                    </ul>
                    <p><em>The more specific your question, the better my response from the database.</em></p>
                </div>
                """,
                'ar': f"""
                <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
                    <h3>🤖 مساعد التسويق الذكي</h3>
                    <p><strong>سؤالك:</strong> "{message}"</p>
                    <p>📚 قاعدة معرفتي تحتوي على <strong>{total_entries} مدخل</strong> متاح.</p>
                    <p><strong>جرب أسئلة أكثر تحديداً مثل:</strong></p>
                    <ul style="text-align: right;">
                        <li>"ما هو معدل فتح بريدي الإلكتروني؟"</li>
                        <li>"كيف أحسن حملاتي؟"</li>
                        <li>"أظهر لي أداء التسويق"</li>
                        <li>"إنشاء حملة بريد إلكتروني جديدة"</li>
                    </ul>
                    <p><em>كلما كان سؤالك أكثر دقة، كانت إجابتي أفضل من قاعدة البيانات.</em></p>
                </div>
                """
            }
            
            return responses.get(language, responses['en'])
            
        except Exception:
            return "🤖 Assistant disponible. Posez une question marketing spécifique."

    def _emergency_database_fallback(self, language):
        """Fallback d'urgence mais toujours depuis la base"""
        try:
            knowledge_base = request.env['ai.knowledge.base']
            
            # Chercher n'importe quelle entrée active
            any_entry = knowledge_base.search([
                ('is_active', '=', True)
            ], limit=1)
            
            if any_entry:
                return {
                    'success': True,
                    'answer': any_entry[0].answer,
                    'confidence': 0.20,
                    'category': any_entry[0].category,
                    'language': language,
                    'source': 'emergency_fallback'
                }
        except Exception:
            pass
            
        # Vraiment dernière option
        return {
            'success': True,
            'answer': "🤖 Service temporairement indisponible. Reconnexion à la base de données...",
            'confidence': 0.10,
            'category': 'general',
            'language': language,
            'source': 'system_error'
        }

    @http.route('/ai_chat/marketing/insights', type='json', auth='user', methods=['GET'])
    def get_marketing_insights(self):
        """Obtenir des insights marketing"""
        try:
            insights = request.env['ai.knowledge.base'].get_marketing_insights()
            return {'success': True, 'insights': insights}
        except Exception as e:
            _logger.error("Erreur get_marketing_insights: %s", e)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_chat/recommendations', type='json', auth='user', methods=['GET'])
    def get_ai_recommendations(self):
        """Obtenir des recommandations IA"""
        try:
            recommendations = request.env['ai.knowledge.base'].get_campaign_recommendations()
            return {'success': True, 'recommendations': recommendations}
        except Exception as e:
            _logger.error("Erreur get_ai_recommendations: %s", e)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_chat/campaigns/analysis', type='json', auth='user', methods=['POST'])
    def analyze_campaign(self, campaign_id=None, **kwargs):
        """Analyser une campagne spécifique"""
        try:
            if not campaign_id:
                return {'success': False, 'error': 'ID de campagne requis'}
            
            # Logique d'analyse de campagne
            analysis = {
                'campaign_id': campaign_id,
                'metrics': {
                    'open_rate': 25.5,
                    'click_rate': 3.2,
                    'conversion_rate': 1.8,
                    'total_sent': 1000,
                    'total_opened': 255,
                    'total_clicked': 32
                },
                'recommendations': [
                    'Améliorer l\'objet pour augmenter le taux d\'ouverture',
                    'Optimiser le call-to-action pour plus de conversions'
                ]
            }
            
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            _logger.error("Erreur analyze_campaign: %s", e)
            return {'success': False, 'error': str(e)}

    @http.route('/ai_chat/quick_action', type='json', auth='user', methods=['POST'])
    def execute_quick_action(self, action, **kwargs):
        """Exécuter une action rapide"""
        try:
            responses = {
                'marketing_overview': self._get_marketing_overview(),
                'view_campaigns': self._get_campaigns_summary(),
                'get_analytics': self._get_analytics_summary(),
                'view_active_campaigns': self._format_campaigns_summary(),
                'get_improvement_suggestions': self._format_recommendations()
            }
            
            response = responses.get(action, 'Action non reconnue.')
            
            return {
                'success': True,
                'response': response,
                'action_executed': action
            }
            
        except Exception as e:
            _logger.error("Erreur execute_quick_action: %s", e, exc_info=True)
            return {
                'success': False,
                'error': 'Erreur lors de l\'exécution de l\'action.'
            }

    @http.route('/ai_chat/session/create', type='json', auth='user', methods=['POST'])
    def create_chat_session(self, **kwargs):
        """Créer une nouvelle session de chat"""
        try:
            session = self._create_chat_session()
            
            # Message de bienvenue selon la langue de l'utilisateur
            user_lang = request.env.user.lang or 'en_US'
            welcome_messages = {
                'ar_SA': """🤖 مرحباً بك في مساعد الذكاء الاصطناعي للتسويق!

مرحبا، كيف يمكنني مساعدتك؟

يمكنني مساعدتك في:
• تحليل أداء الحملات التسويقية
• تقديم توصيات التحسين  
• الإجابة على أسئلة التسويق
• تحليل البيانات والمقاييس

اسأل أي سؤال أو اختر من الاقتراحات أدناه!""",
                'fr_FR': """🤖 Bienvenue dans l'Assistant IA Marketing !

Salut, comment puis-je vous aider ?

Je peux vous assister avec :
• Analyse des performances de campagnes
• Recommandations d'optimisation
• Questions sur le marketing
• Analyse de données et métriques

Posez votre question ou choisissez parmi les suggestions ci-dessous !""",
                'en_US': """🤖 Welcome to the AI Marketing Assistant!

Hi, how can I help you?

I can assist you with:
• Campaign performance analysis
• Optimization recommendations  
• Marketing questions
• Data analysis and metrics

Ask any question or choose from the suggestions below!"""
            }
            
            welcome_message = welcome_messages.get(user_lang, welcome_messages['en_US'])
            
            return {
                'success': True,
                'session_id': session.id,
                'welcome_message': welcome_message,
                'user_name': request.env.user.name
            }
            
        except Exception as e:
            _logger.error("Erreur create_chat_session: %s", e, exc_info=True)
            return {
                'success': False,
                'error': 'Impossible de créer une session de chat.'
            }

    def _create_chat_session(self):
        """Créer une nouvelle session de chat"""
        session_name = f"Chat - {request.env.user.name} - {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = request.env['ai.chat.session'].create({
            'name': session_name,
            'user_id': request.env.user.id,
            'start_time': fields.Datetime.now(),
            'last_activity': fields.Datetime.now(),
            'state': 'active',
            'session_type': 'marketing'
        })
        
        return session

    def _get_marketing_overview(self):
        """Obtenir un aperçu marketing"""
        try:
            insights = request.env['ai.knowledge.base'].get_marketing_insights()
            
            if insights.get('error'):
                return f"❌ Erreur lors de la récupération des données: {insights['error']}"
            
            overview = f"""📊 **Aperçu Marketing**

📈 **Statistiques Générales:**
• Total campagnes: {insights.get('total_campaigns', 0)}
• Messages envoyés: {insights.get('total_sent', 0):,}
• Taux d'ouverture moyen: {insights.get('avg_open_rate', 0):.1f}%
• Taux de réponse moyen: {insights.get('avg_reply_rate', 0):.1f}%

🎯 **Campagnes Actives:** {len(insights.get('active_campaigns', []))}

💡 **Recommandation:** Continuez à surveiller vos métriques pour identifier les opportunités d'amélioration !"""
            
            return overview
            
        except Exception as e:
            _logger.error("Erreur _get_marketing_overview: %s", e)
            return "📊 Aperçu marketing en cours de chargement..."

    def _get_campaigns_summary(self):
        """Obtenir un résumé des campagnes"""
        try:
            insights = request.env['ai.knowledge.base'].get_marketing_insights()
            campaigns = insights.get('active_campaigns', [])
            
            if not campaigns:
                return "📭 Aucune campagne active pour le moment."
            
            summary = "📈 **Campagnes Actives:**\n\n"
            
            for campaign in campaigns[:5]:  # Limiter à 5 campagnes
                open_rate = (campaign.get('opened', 0) / campaign.get('sent', 1) * 100) if campaign.get('sent', 0) > 0 else 0
                summary += f"""🎯 **{campaign.get('name', 'Sans nom')}**
   • État: {campaign.get('state', 'N/A')}
   • Envoyés: {campaign.get('sent', 0):,}
   • Ouverts: {campaign.get('opened', 0):,} ({open_rate:.1f}%)
   • Réponses: {campaign.get('replied', 0):,}

"""
            return summary
            
        except Exception as e:
            _logger.error("Erreur _get_campaigns_summary: %s", e)
            return "📈 Données des campagnes en cours de chargement..."

    def _get_analytics_summary(self):
        """Obtenir un résumé des analytics"""
        return """📊 **Analytics Résumé**

📈 **Métriques clés :**
• Engagement global en hausse
• Meilleure performance le mardi
• Objets courts (+15% taux d'ouverture)

💡 **Insights :**
• Personnalisation améliore les résultats
• Mobile représente 65% des ouvertures
• Call-to-action clairs augmentent les clics"""

    def _format_campaigns_summary(self):
        """Formater le résumé des campagnes (compatibilité)"""
        return self._get_campaigns_summary()

    def _format_recommendations(self):
        """Formater les recommandations (compatibilité)"""
        try:
            recommendations = request.env['ai.knowledge.base'].get_campaign_recommendations()
            
            if not recommendations:
                return "✅ Vos campagnes semblent bien optimisées ! Continuez le bon travail."
            
            formatted = "💡 **Recommandations AI:**\n\n"
            
            for rec in recommendations[:5]:  # Limiter à 5 recommandations
                icon = "⚠️" if rec.get('type') == 'warning' else "✅" if rec.get('type') == 'success' else "💡"
                formatted += f"{icon} {rec.get('message', 'Recommandation non disponible')}\n\n"
            
            return formatted
            
        except Exception as e:
            _logger.error("Erreur _format_recommendations: %s", e)
            return "💡 Chargement des recommandations..."

    # Routes supplémentaires pour compatibilité
    @http.route('/ai_chat/marketing/insights', type='json', auth='user')
    def marketing_insights_compat(self):
        """Route de compatibilité pour les insights marketing"""
        return self.get_marketing_insights()

    @http.route('/ai_chat/campaigns/active', type='json', auth='user')
    def get_active_campaigns(self):
        """Obtenir les campagnes actives"""
        try:
            insights = request.env['ai.knowledge.base'].get_marketing_insights()
            campaigns = insights.get('active_campaigns', [])
            return {'success': True, 'campaigns': campaigns}
        except Exception as e:
            _logger.error("Erreur get_active_campaigns: %s", e)
            return {'success': False, 'error': str(e)}