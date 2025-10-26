# -*- coding: utf-8 -*-
{
    'name': 'AI Chat Assistant',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Assistant de Chat IA pour Odoo avec support marketing multilingue',
    'description': """
AI Chat Assistant - Assistant Intelligent Multilingue

Fonctionnalites principales :
* Chatbot IA integre style Messenger
* Support multilingue (Arabe, Francais, Anglais)  
* Insights marketing intelligents
* Recommandations d optimisation automatiques
* Analytics avances des campagnes
* Interface moderne en bas a droite
* Base de connaissances extensible

Le chatbot apparait sous forme de bulle en bas a droite de toutes les pages Odoo
et fournit des recommandations marketing basees sur l intelligence artificielle.

Installation :
1. Installer le module
2. Le chatbot s active automatiquement
3. Cliquer sur la bulle pour commencer
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/chatbot_views.xml',
        'views/chatbot_templates.xml',
        'data/demo_knowledge_base.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}