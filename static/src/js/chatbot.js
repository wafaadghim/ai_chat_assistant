odoo.define('ai_chat_assistant.chat_widget', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');
    var ajax = require('web.ajax');

    var _t = core._t;

    var AIChatWidget = Widget.extend({
        template: 'ai_chat_assistant.chat_widget',
        
        events: {
            'click .ai-send-btn': '_onSendMessage',
            'keypress .ai-chat-input': '_onKeyPress',
            'click .ai-quick-action': '_onQuickAction',
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.session_id = options.session_id || false;
            this.language = options.language || 'fr';
        },

        start: function () {
            this._super.apply(this, arguments);
            this._initializeChat();
            return $.when();
        },

        _initializeChat: function () {
            // Créer une nouvelle session si nécessaire
            if (!this.session_id) {
                this._createNewSession();
            }
            
            // Message de bienvenue
            this._addWelcomeMessage();
        },

        _createNewSession: function () {
            var self = this;
            ajax.rpc('/ai_chat/create_session', {
                session_type: 'marketing'
            }).then(function (result) {
                self.session_id = result.session_id;
            });
        },

        _addWelcomeMessage: function () {
            const welcomeMessages = {
                'fr': "👋 Bonjour ! Je suis votre assistant marketing IA. Comment puis-je vous aider aujourd'hui ?",
                'en': "👋 Hello! I'm your AI marketing assistant. How can I help you today?",
                'ar': "👋 مرحبا! أنا مساعدك للتسويق بالذكاء الاصطناعي. كيف يمكنني مساعدتك اليوم؟"
            };
            
            const message = welcomeMessages[this.language] || welcomeMessages['en'];
            this._addMessageToChat(message, 'bot');
        },

        _onSendMessage: function () {
            const input = this.$('.ai-chat-input');
            const message = input.val().trim();
            
            if (message) {
                this._sendAIMessage(message);
                input.val('');
            }
        },

        _onKeyPress: function (event) {
            if (event.which === 13 && !event.shiftKey) {
                event.preventDefault();
                this._onSendMessage();
            }
        },

        _onQuickAction: function (event) {
            const action = $(event.currentTarget).data('action');
            const text = $(event.currentTarget).text();
            
            // Simuler l'envoi du message pour l'action rapide
            this._sendAIMessage(text);
        },

        _sendAIMessage: function (userMessage) {
            var self = this;
            
            // Ajouter le message utilisateur
            this._addMessageToChat(userMessage, 'user');
            
            // Afficher l'indicateur de frappe
            this._showTypingIndicator();
            
            // Envoyer au serveur (langue détectée automatiquement)
            ajax.rpc('/ai_chat/get_response', {
                'message': userMessage,
                'session_id': this.session_id
                // Note: langue détectée automatiquement par le backend
            }).then(function (result) {
                self._hideTypingIndicator();
                
                if (!result.success || result.error) {
                    self._addMessageToChat(result.answer || result.response || 'Erreur de connexion', 'bot');
                } else {
                    // L'endpoint retourne 'answer' pas 'response'
                    self._addMessageToChat(result.answer || result.response, 'bot');
                    
                    // Log pour debug
                    console.log('🤖 Réponse reçue:', {
                        success: result.success,
                        language: result.language,
                        source: result.source,
                        confidence: result.confidence
                    });
                    
                    // Ajouter les actions rapides si disponibles
                    if (result.quick_actions && result.quick_actions.length > 0) {
                        self._addQuickActions(result.quick_actions);
                    }
                }
            }).catch(function (error) {
                self._hideTypingIndicator();
                console.error('🚨 Erreur connexion serveur:', error);
                
                // Réessayer une fois avant le fallback
                console.log('🔄 Tentative de reconnexion à la base de données...');
                
                setTimeout(function() {
                    ajax.rpc('/ai_chat/get_response', {
                        'message': userMessage,
                        'session_id': self.session_id
                        // Note: langue détectée automatiquement par le backend
                    }).then(function (retryResult) {
                        if (retryResult && retryResult.success && !retryResult.error) {
                            console.log('✅ Reconnexion réussie - réponse de la base de données');
                            self._addMessageToChat(retryResult.answer || retryResult.response, 'bot');
                        } else {
                            console.log('⚠️ Reconnexion échouée - utilisation fallback temporaire');
                            const fallbackResponse = self._getDatabaseConnectionError(userMessage, self.language);
                            self._addMessageToChat(fallbackResponse, 'bot');
                        }
                    }).catch(function() {
                        console.log('❌ Reconnexion impossible - fallback temporaire');
                        const fallbackResponse = self._getDatabaseConnectionError(userMessage, self.language);
                        self._addMessageToChat(fallbackResponse, 'bot');
                    });
                }, 1000); // Attendre 1 seconde avant de réessayer
            });
        },

        _getDatabaseConnectionError: function (userMessage, language) {
            // Messages d'erreur de connexion qui encouragent la spécificité
            const connectionErrors = {
                'fr': `
                    <div style="border-left: 4px solid #ffc107; padding: 15px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0;">
                        <h4 style="color: #856404; margin-top: 0;">⚠️ Connexion à la base de données interrompue</h4>
                        <p><strong>Votre question :</strong> "${userMessage}"</p>
                        <p style="color: #856404;">Je tente de récupérer une réponse précise depuis ma base PostgreSQL...</p>
                        <p><strong>En attendant, reformulez votre question de manière plus spécifique :</strong></p>
                        <ul style="color: #856404;">
                            <li>"Quel est mon taux d'ouverture email cette semaine ?"</li>
                            <li>"Montre-moi les performances de ma dernière campagne"</li>
                            <li>"Comment améliorer mes conversions email ?"</li>
                            <li>"Créer une nouvelle campagne marketing"</li>
                        </ul>
                        <p><em style="color: #856404;">Plus votre question est précise, plus ma réponse depuis la base sera exacte.</em></p>
                        <button onclick="location.reload()" style="background: #ffc107; color: #856404; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; margin-top: 10px;">
                            🔄 Reconnecter à la base de données
                        </button>
                    </div>
                `,
                'en': `
                    <div style="border-left: 4px solid #ffc107; padding: 15px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0;">
                        <h4 style="color: #856404; margin-top: 0;">⚠️ Database connection interrupted</h4>
                        <p><strong>Your question:</strong> "${userMessage}"</p>
                        <p style="color: #856404;">I'm trying to get a precise answer from my PostgreSQL database...</p>
                        <p><strong>Meanwhile, rephrase your question more specifically:</strong></p>
                        <ul style="color: #856404;">
                            <li>"What is my email open rate this week?"</li>
                            <li>"Show me my latest campaign performance"</li>
                            <li>"How to improve my email conversions?"</li>
                            <li>"Create a new marketing campaign"</li>
                        </ul>
                        <p><em style="color: #856404;">The more specific your question, the more accurate my database response.</em></p>
                        <button onclick="location.reload()" style="background: #ffc107; color: #856404; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; margin-top: 10px;">
                            🔄 Reconnect to database
                        </button>
                    </div>
                `,
                'ar': `
                    <div style="border-left: 4px solid #ffc107; padding: 15px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0; direction: rtl; text-align: right;">
                        <h4 style="color: #856404; margin-top: 0;">⚠️ انقطع الاتصال بقاعدة البيانات</h4>
                        <p><strong>سؤالك:</strong> "${userMessage}"</p>
                        <p style="color: #856404;">أحاول الحصول على إجابة دقيقة من قاعدة PostgreSQL...</p>
                        <p><strong>في الوقت الحالي، أعد صياغة سؤالك بشكل أكثر تحديداً:</strong></p>
                        <ul style="color: #856404; text-align: right;">
                            <li>"ما هو معدل فتح بريدي الإلكتروني هذا الأسبوع؟"</li>
                            <li>"أظهر لي أداء حملتي الأخيرة"</li>
                            <li>"كيف أحسن تحويلات البريد الإلكتروني؟"</li>
                            <li>"إنشاء حملة تسويقية جديدة"</li>
                        </ul>
                        <p><em style="color: #856404;">كلما كان سؤالك أكثر دقة، كانت إجابتي من قاعدة البيانات أكثر دقة.</em></p>
                        <button onclick="location.reload()" style="background: #ffc107; color: #856404; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; margin-top: 10px;">
                            🔄 إعادة الاتصال بقاعدة البيانات
                        </button>
                    </div>
                `
            };
            
            return connectionErrors[language] || connectionErrors['en'];
        },

        _getStaticAIResponse: function (userMessage, language) {
            // CORRECTION : Définir 'responses' localement
            const responses = {
                'fr': {
                    'greeting': "Bonjour ! Comment puis-je vous aider avec votre marketing aujourd'hui ?",
                    'performance': "Voici un aperçu de vos performances marketing. Pour des données précises, veuillez vous connecter au serveur.",
                    'campaigns': "Analysons vos campagnes. Les détails complets nécessitent une connexion serveur.",
                    'help': "Je peux vous aider avec l'analyse marketing, les campagnes, et les recommandations.",
                    'analytics': "Voici vos analytics marketing. Connexion serveur requise pour les données en temps réel.",
                    'default': "Je comprends votre question sur le marketing. Veuillez réessayer quand la connexion sera rétablie."
                },
                'en': {
                    'greeting': "Hello! How can I help you with your marketing today?",
                    'performance': "Here's an overview of your marketing performance. Connect to server for precise data.",
                    'campaigns': "Let's analyze your campaigns. Full details require server connection.",
                    'help': "I can help you with marketing analysis, campaigns, and recommendations.",
                    'analytics': "Here are your marketing analytics. Server connection required for real-time data.",
                    'default': "I understand your marketing question. Please try again when connection is restored."
                },
                'ar': {
                    'greeting': "مرحبا! كيف يمكنني مساعدتك في التسويق اليوم؟",
                    'performance': "إليك نظرة عامة على أداء التسويق. اتصل بالخادم للحصول على بيانات دقيقة.",
                    'campaigns': "دعنا نحلل حملاتك. التفاصيل الكاملة تتطلب اتصال بالخادم.",
                    'help': "يمكنني مساعدتك في تحليل التسويق والحملات والتوصيات.",
                    'analytics': "إليك تحليلات التسويق الخاصة بك. اتصال الخادم مطلوب للبيانات الفورية.",
                    'default': "أفهم سؤالك حول التسويق. يرجى المحاولة مرة أخرى عند استعادة الاتصال."
                }
            };
            
            // Déterminer la clé de réponse appropriée
            const key = this._determineResponseKey(userMessage);
            
            return responses[language]?.[key] || responses['en']?.[key] || responses['en']['default'];
        },

        _determineResponseKey: function (message) {
            const msgLower = message.toLowerCase();
            
            // Détection de salutations
            if (msgLower.includes('bonjour') || msgLower.includes('hello') || msgLower.includes('مرحبا') ||
                msgLower.includes('salut') || msgLower.includes('hi') || msgLower.includes('أهلا')) {
                return 'greeting';
            }
            
            // Détection de questions sur performance
            if (msgLower.includes('performance') || msgLower.includes('أداء') || msgLower.includes('résultat') ||
                msgLower.includes('efficacité') || msgLower.includes('metrics') || msgLower.includes('مقاييس')) {
                return 'performance';
            }
            
            // Détection de questions sur campagnes
            if (msgLower.includes('campaign') || msgLower.includes('campagne') || msgLower.includes('حملة') ||
                msgLower.includes('email') || msgLower.includes('newsletter') || msgLower.includes('بريد')) {
                return 'campaigns';
            }
            
            // Détection de demandes d'aide
            if (msgLower.includes('help') || msgLower.includes('aide') || msgLower.includes('مساعدة') ||
                msgLower.includes('comment') || msgLower.includes('how') || msgLower.includes('كيف')) {
                return 'help';
            }
            
            // Détection d'analytics
            if (msgLower.includes('analytics') || msgLower.includes('analyse') || msgLower.includes('تحليل') ||
                msgLower.includes('rapport') || msgLower.includes('report') || msgLower.includes('تقرير')) {
                return 'analytics';
            }
            
            return 'default';
        },

        _addMessageToChat: function (message, type, showTimestamp = true) {
            const chatContainer = this.$('.ai-chat-messages');
            const timestamp = showTimestamp ? new Date().toLocaleTimeString() : '';
            
            const messageElement = $(`
                <div class="message ${type}-message">
                    <div class="message-content">
                        ${message}
                    </div>
                    ${timestamp ? `<div class="message-timestamp">${timestamp}</div>` : ''}
                </div>
            `);
            
            chatContainer.append(messageElement);
            chatContainer.scrollTop(chatContainer[0].scrollHeight);
        },

        _addQuickActions: function (actions) {
            const actionsContainer = $('<div class="quick-actions-container">');
            
            actions.forEach(action => {
                const button = $(`
                    <button class="ai-quick-action btn btn-sm btn-outline-primary" 
                            data-action="${action.action}">
                        ${action.text}
                    </button>
                `);
                actionsContainer.append(button);
            });
            
            this.$('.ai-chat-messages').append(actionsContainer);
        },

        _showTypingIndicator: function () {
            const indicator = $(`
                <div class="message bot-message typing-indicator">
                    <div class="message-content">
                        <span class="typing-dots">
                            <span></span><span></span><span></span>
                        </span>
                        Assistant en train d'écrire...
                    </div>
                </div>
            `);
            
            this.$('.ai-chat-messages').append(indicator);
            this.$('.ai-chat-messages').scrollTop(this.$('.ai-chat-messages')[0].scrollHeight);
        },

        _hideTypingIndicator: function () {
            this.$('.typing-indicator').remove();
        }
    });

    return AIChatWidget;
});