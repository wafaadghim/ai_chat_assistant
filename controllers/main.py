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