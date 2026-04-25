# -*- coding: utf-8 -*-
{
    'name': 'Novix Delivery Wallet',
    'version': '1.0',
    'category': 'Accounting/Delivery',
    'summary': 'Sub-ledger for Customer, Driver, and Merchant Wallets',
    'author': 'NOVIX',
    'depends': ['account', 'novix_delivery_orders', 'novix_delivery_core',],
    'data': [
        'security/ir.model.access.csv',
        'data/wallet_sequence.xml',
        'views/wallet_transaction_views.xml',
        'views/res_partner_inherit_views.xml',
        'views/wallet_menus.xml',
    ],
    'installable': True,
    'application': False,
}