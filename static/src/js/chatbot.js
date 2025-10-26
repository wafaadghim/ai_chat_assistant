odoo.define('ai_chat_assistant.chatbot', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    console.log("🚀 AI Chat Assistant - Advanced Messenger Style Loading...");

    // Configuration du chatbot
    var ChatConfig = {
        apiEndpoints: {
            process: '/ai_chat/process',
            insights: '/ai_chat/marketing/insights',
            recommendations: '/ai_chat/recommendations',
            createSession: '/ai_chat/session/create',
            quickAction: '/ai_chat/quick_action'
        },
        currentSession: null,
        isTyping: false,
        isOpen: false,
        autoSuggestions: [
            "ما أفضل قناة إعلانية هذا الشهر؟",
            "اعطني تقرير الحملات الأقل أداء",
            "توصيات لتحسين معدل الفتح",
            "تحليل أداء الحملات الحالية",
            "What's the best advertising channel this month?",
            "Give me report on underperforming campaigns",
            "Recommendations to improve open rate"
        ],
        welcomeMessages: {
            ar: `مرحباً! 👋 أنا مساعد الذكاء الاصطناعي المتخصص في التسويق.

🎯 يمكنني مساعدتك في:
• تحليل أداء الحملات التسويقية  
• تقديم توصيات لتحسين النتائج
• الإجابة على أسئلة حول استراتيجية التسويق
• تحليل البيانات وتقديم رؤى ذكية

كيف يمكنني مساعدتك اليوم؟`,
            
            fr: `Bonjour! 👋 Je suis l'assistant IA spécialisé en marketing.

🎯 Je peux vous aider avec:
• Analyse des performances de campagnes
• Recommandations d'optimisation  
• Questions sur la stratégie marketing
• Analyse de données et insights intelligents

Comment puis-je vous aider aujourd'hui?`,
            
            en: `Hello! 👋 I'm your AI Marketing Assistant.

🎯 I can help you with:
• Campaign performance analysis
• Optimization recommendations
• Marketing strategy questions  
• Data analysis and smart insights

How can I help you today?`
        }
    };

    // Classe principale du chatbot
    var AIChatbot = {
        
        init: function() {
            console.log("✅ Initializing Advanced AI Chatbot...");
            this.createLauncher();
            this.bindGlobalEvents();
        },

        createLauncher: function() {
            // Supprimer launcher existant
            $('.chat-launcher').remove();
            
            var launcher = $(`
                <button class="chat-launcher" title="AI Marketing Assistant - Click to chat">
                    🤖
                </button>
            `);
            
            launcher.on('click', this.toggleChat.bind(this));
            $('body').append(launcher);
            
            console.log("✅ Chat launcher created with Odoo styling");
        },

        toggleChat: function() {
            if (ChatConfig.isOpen) {
                this.closeChat();
            } else {
                this.openChat();
            }
        },

        openChat: function() {
            if (ChatConfig.isOpen) return;
            
            console.log("🎯 Opening advanced chat widget...");
            ChatConfig.isOpen = true;
            
            // Créer session si nécessaire
            if (!ChatConfig.currentSession) {
                this.createSession().then((sessionData) => {
                    this.createChatWidget(sessionData.welcome_message);
                }).catch(() => {
                    this.createChatWidget();
                });
            } else {
                this.createChatWidget();
            }
        },

        createChatWidget: function(welcomeMessage = null) {
            $('.chat-widget').remove();
            
            var widget = $(`
                <div class="chat-widget">
                    <div class="chat-header">
                        <div class="chat-header-content">
                            <div class="chat-avatar">🤖</div>
                            <div class="chat-header-info">
                                <h3>AI Assistant</h3>
                                <div class="status">
                                    <div class="status-dot"></div>
                                    En ligne - Prêt à vous aider
                                </div>
                            </div>
                        </div>
                        <button class="chat-close" title="Fermer">✕</button>
                    </div>
                    <div class="chat-messages">
                        <div class="messages-container"></div>
                    </div>
                    <div class="quick-suggestions">
                        <div class="suggestions-title">Suggestions rapides</div>
                        <div class="suggestions-list"></div>
                    </div>
                    <div class="chat-input-area">
                        <div class="input-container">
                            <textarea class="chat-input" placeholder="Tapez votre question ici..." rows="1"></textarea>
                        </div>
                        <div class="input-actions">
                            <button class="chat-options" title="Options">⚙️</button>
                            <button class="chat-send" title="Envoyer">➤</button>
                        </div>
                    </div>
                </div>
            `);
            
            $('body').append(widget);
            
            // Animation d'entrée
            setTimeout(() => widget.addClass('show'), 50);
            
            // Bind events
            this.bindChatEvents(widget);
            
            // Message de bienvenue
            var defaultMessage = welcomeMessage || this.getWelcomeMessage();
            setTimeout(() => {
                this.addMessage('bot', defaultMessage);
                this.loadQuickSuggestions();
            }, 500);
            
            // Focus sur input
            setTimeout(() => widget.find('.chat-input').focus(), 800);
        },

        bindChatEvents: function(widget) {
            var self = this;
            
            // Fermer chat
            widget.find('.chat-close').on('click', () => this.closeChat());
            
            // Envoyer message
            widget.find('.chat-send').on('click', () => this.sendMessage());
            
            // Enter pour envoyer (sans Shift)
            widget.find('.chat-input').on('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    self.sendMessage();
                }
            });
            
            // Auto-resize textarea
            widget.find('.chat-input').on('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
            
            // Click sur suggestions
            widget.on('click', '.suggestion-btn', function() {
                var suggestionText = $(this).text();
                widget.find('.chat-input').val(suggestionText);
                self.sendMessage();
            });
            
            // Actions rapides
            widget.on('click', '.action-btn', function() {
                var actionType = $(this).data('action');
                self.executeQuickAction(actionType);
            });
        },

        closeChat: function() {
            var widget = $('.chat-widget');
            widget.removeClass('show');
            ChatConfig.isOpen = false;
            setTimeout(() => widget.remove(), 300);
        },

        sendMessage: function() {
            var input = $('.chat-input');
            var message = input.val().trim();
            
            if (!message || ChatConfig.isTyping) return;
            
            // Ajouter message utilisateur
            this.addMessage('user', message);
            input.val('');
            input.css('height', 'auto');
            
            // Traiter le message
            this.processMessage(message);
        },

        processMessage: function(message) {
            var self = this;
            ChatConfig.isTyping = true;
            
            // Afficher indicateur de frappe
            this.showTypingIndicator();
            
            // Appel API vers le backend Odoo
            ajax.jsonRpc(ChatConfig.apiEndpoints.process, 'call', {
                message: message,
                session_id: ChatConfig.currentSession
            }).then(function(result) {
                self.hideTypingIndicator();
                ChatConfig.isTyping = false;
                
                if (result.success) {
                    self.addMessage('bot', result.response);
                    
                    // Mettre à jour session
                    if (result.session_id) {
                        ChatConfig.currentSession = result.session_id;
                    }
                    
                    // Afficher actions rapides si disponibles
                    if (result.quick_actions && result.quick_actions.length > 0) {
                        self.showQuickActions(result.quick_actions);
                    }
                } else {
                    self.addMessage('bot', result.error || 'Désolé, une erreur est survenue. Veuillez réessayer.');
                }
            }).catch(function(error) {
                console.error('Erreur API chatbot:', error);
                self.hideTypingIndicator();
                ChatConfig.isTyping = false;
                self.addMessage('bot', 'Désolé, je ne peux pas traiter votre demande actuellement. Veuillez réessayer plus tard.');
            });
        },

        addMessage: function(type, text) {
            var container = $('.messages-container');
            var timestamp = new Date().toLocaleTimeString('fr-FR', {
                hour: '2-digit', 
                minute: '2-digit'
            });
            
            var messageElement = $(`
                <div class="chat-message ${type}">
                    <div class="message-avatar">${type === 'user' ? '👤' : '🤖'}</div>
                    <div class="chat-bubble">${text}</div>
                </div>
                <div class="message-time">${timestamp}</div>
            `);
            
            container.append(messageElement);
            this.scrollToBottom();
        },

        showTypingIndicator: function() {
            var container = $('.messages-container');
            var typingElement = $(`
                <div class="typing-indicator">
                    <div class="typing-avatar">🤖</div>
                    <div class="typing-bubble">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            `);
            
            container.append(typingElement);
            this.scrollToBottom();
        },

        hideTypingIndicator: function() {
            $('.typing-indicator').remove();
        },

        scrollToBottom: function() {
            var messagesArea = $('.chat-messages');
            messagesArea.scrollTop(messagesArea[0].scrollHeight);
        },

        loadQuickSuggestions: function() {
            var suggestionsContainer = $('.suggestions-list');
            suggestionsContainer.empty();
            
            // Charger les suggestions aléatoires
            var shuffled = ChatConfig.autoSuggestions.sort(() => 0.5 - Math.random());
            var selected = shuffled.slice(0, 3);
            
            selected.forEach(function(suggestion) {
                var btn = $(`<button class="suggestion-btn">${suggestion}</button>`);
                suggestionsContainer.append(btn);
            });
        },

        showQuickActions: function(actions) {
            var container = $('.messages-container');
            var actionsHtml = '<div class="quick-actions-container"><div class="actions-title">Actions rapides:</div>';
            
            actions.forEach(function(action) {
                actionsHtml += `<button class="action-btn" data-action="${action.action}">${action.text}</button>`;
            });
            
            actionsHtml += '</div>';
            container.append(actionsHtml);
            this.scrollToBottom();
        },

        executeQuickAction: function(actionType) {
            var self = this;
            
            ajax.jsonRpc(ChatConfig.apiEndpoints.quickAction, 'call', {
                action: actionType
            }).then(function(result) {
                if (result.success) {
                    self.addMessage('bot', result.message);
                    
                    if (result.data) {
                        // Afficher des données supplémentaires si disponibles
                        console.log('Action data:', result.data);
                    }
                } else {
                    self.addMessage('bot', 'Cette action n\'est pas disponible pour le moment.');
                }
            }).catch(function(error) {
                console.error('Erreur action rapide:', error);
                self.addMessage('bot', 'Erreur lors de l\'exécution de l\'action.');
            });
        },

        createSession: function() {
            return ajax.jsonRpc(ChatConfig.apiEndpoints.createSession, 'call', {});
        },

        getWelcomeMessage: function() {
            // Détecter la langue de l'utilisateur (simple heuristic)
            var userLang = (navigator.language || navigator.userLanguage || 'en').substring(0, 2);
            
            return ChatConfig.welcomeMessages[userLang] || ChatConfig.welcomeMessages['en'];
        },

        bindGlobalEvents: function() {
            var self = this;
            
            // ESC pour fermer
            $(document).on('keydown', function(e) {
                if (e.key === 'Escape' && ChatConfig.isOpen) {
                    self.closeChat();
                }
            });
            
            // Clic en dehors pour fermer (optionnel)
            $(document).on('click', function(e) {
                if (ChatConfig.isOpen && 
                    !$(e.target).closest('.chat-widget, .chat-launcher').length) {
                    // Optionnel: décommenter pour fermer en cliquant en dehors
                    // self.closeChat();
                }
            });
        }
    };

    // Auto-initialisation quand le DOM est prêt
    $(document).ready(function() {
        setTimeout(function() {
            AIChatbot.init();
            console.log("✅ AI Chat Assistant initialized successfully with advanced features");
        }, 1000);
    });

    // Export pour usage externe
    return AIChatbot;
});