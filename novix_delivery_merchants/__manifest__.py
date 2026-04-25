# -*- coding: utf-8 -*-
{
    'name': 'Novix Delivery Customers',
    'version': '1.0',
    'category': 'Operations/Delivery',
    'summary': 'Manage End Customers, Phone Verification, and Delivery Addresses',
    'author': 'NOVIX',
    'depends': ['contacts', 'novix_delivery_core'],
    'data': [
        'views/delivery_merchant_views.xml',
        'views/merchant_menus.xml',
    ],
    'installable': True,
    'application': False,
}