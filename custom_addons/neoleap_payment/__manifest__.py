{
    'name': 'pos NeoLeap Payment Gateway',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'NeoLeap Payment Gateway Integration for Odoo 18',
    'description': """
NeoLeap Payment Gateway Integration
==================================

This module integrates NeoLeap payment gateway with Odoo 18, providing:
- Payment provider for e-commerce and invoices
- POS terminal integration with WebSocket communication
- Complete payment processing workflow
- Support for both online and terminal payments
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'payment',
        'website_sale',
        'point_of_sale',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/pos_payment_method_views.xml',
        'views/payment_transaction_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'neoleap_payment/static/src/js/pos_neoleap.js',
            'neoleap_payment/static/src/xml/pos_neoleap.xml',
        ],
        'web.assets_frontend': [
            'neoleap_payment/static/src/js/payment_form.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook_set_neoleap_credentials', # <--- Added this line
}
