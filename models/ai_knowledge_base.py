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

    @api.model
    def search_knowledge(self, query, language='multi', category=None, limit=5):
        """Rechercher dans la base de connaissances"""
        domain = [('is_active', '=', True)]
        
        # Filtre par langue
        if language != 'multi':
            domain.append(('language', 'in', [language, 'multi']))
        
        # Filtre par catégorie
        if category:
            domain.append(('category', '=', category))
        
        # Recherche textuelle
        query_lower = query.lower()
        
        # Recherche par question et mots-clés
        knowledge_entries = self.search(domain)
        scored_entries = []
        
        for entry in knowledge_entries:
            score = 0
            
            # Score basé sur la correspondance de la question
            if query_lower in entry.question.lower():
                score += 10
            
            # Score basé sur les mots-clés
            for keyword in entry.keywords:
                if keyword.name.lower() in query_lower:
                    score += 5
            
            # Score basé sur la réponse
            if query_lower in entry.answer.lower():
                score += 2
            
            # Bonus pour priorité et usage
            score += entry.priority
            score += min(entry.usage_count * 0.1, 5)  # Max 5 points bonus
            
            if score > 0:
                scored_entries.append((score, entry))
        
        # Trier par score et retourner les meilleurs résultats
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry[1] for entry in scored_entries[:limit]]

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

    name = fields.Char(string='Mot-clé', required=True)
    knowledge_base_ids = fields.Many2many('ai.knowledge.base', string='Entrées associées')

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
        """Créer une réponse de chat avec IA améliorée"""
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
            
            # Détecter la langue si non fournie
            if not language or language == 'auto':
                language = self._detect_language(user_message)
            
            # Rechercher dans la base de connaissances
            knowledge_entries = self.env['ai.knowledge.base'].search_knowledge(
                user_message, 
                language=language,
                limit=3
            )
            
            response_data = {}
            
            if knowledge_entries:
                best_match = knowledge_entries[0]
                best_match.increment_usage()
                
                # Formater la réponse avec données dynamiques
                response_message = self._format_response_with_data(
                    best_match.answer, 
                    best_match.category
                )
                
                confidence = 0.9
                quick_actions = self._parse_quick_actions(best_match.quick_actions)
                
                response_data = {
                    'knowledge_base_id': best_match.id,
                    'detected_language': language,
                    'category': best_match.category,
                    'confidence': confidence,
                    'quick_actions': quick_actions
                }
            else:
                # Réponse de fallback intelligente
                response_message = self._generate_smart_fallback(user_message, language)
                confidence = 0.3
                quick_actions = self._get_default_quick_actions(language)
                
                response_data = {
                    'detected_language': language,
                    'fallback': True,
                    'confidence': confidence,
                    'quick_actions': quick_actions
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
            return {
                'response': self._get_error_message(language),
                'error': True,
                'quick_actions': self._get_default_quick_actions(language)
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
        """Actions rapides par défaut selon la langue"""
        actions_map = {
            'ar': [
                {'text': '📊 نظرة عامة', 'action': 'marketing_overview'},
                {'text': '📈 أداء الحملات', 'action': 'view_campaigns'}
            ],
            'fr': [
                {'text': '📊 Aperçu', 'action': 'marketing_overview'},
                {'text': '📈 Performance', 'action': 'view_campaigns'}
            ],
            'en': [
                {'text': '📊 Overview', 'action': 'marketing_overview'},
                {'text': '📈 Performance', 'action': 'view_campaigns'}
            ]
        }
        
        return actions_map.get(language, actions_map['en'])

    def _generate_smart_fallback(self, user_message, language):
        """Générer une réponse de fallback intelligente"""
        fallback_messages = {
            'ar': "عذراً، لم أفهم سؤالك تماماً. هل يمكنك إعادة صياغته أو اختيار أحد الخيارات أدناه؟",
            'fr': "Désolé, je n'ai pas bien compris votre question. Pouvez-vous la reformuler ou choisir une option ci-dessous ?",
            'en': "Sorry, I didn't quite understand your question. Could you rephrase it or choose an option below?"
        }
        
        return fallback_messages.get(language, fallback_messages['en'])

    def _get_error_message(self, language):
        """Messages d'erreur selon la langue"""
        error_messages = {
            'ar': "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
            'fr': "Désolé, une erreur est survenue. Veuillez réessayer.",
            'en': "Sorry, an error occurred. Please try again."
        }
        
        return error_messages.get(language, error_messages['en'])

    def _detect_language(self, message):
        """Détecter la langue du message"""
        import re
        
        # Regex pour l'arabe
        if re.search(r'[\u0600-\u06FF]', message):
            return 'ar'
        
        # Mots-clés français
        french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'une', 'pour', 'avec', 'sur', 'dans', 'bonjour', 'salut']
        message_lower = message.lower()
        
        for word in french_words:
            if word in message_lower:
                return 'fr'
        
        return 'en'  # Par défaut anglais

    @api.model  
    def get_marketing_insights(self):
        """Proxy vers la méthode de ai.knowledge.base"""
        return self.env['ai.knowledge.base'].get_marketing_insights()