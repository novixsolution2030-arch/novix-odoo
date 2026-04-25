# -*- coding: utf-8 -*-
{
    'name': 'Novix Delivery Fleet',
    'version': '1.0',
    'category': 'Operations/Delivery',
    'summary': 'Manage Delivery Drivers, KYC, and Fleet Integration',
    'author': 'NOVIX',
    'depends': ['contacts', 'fleet', 'novix_delivery_core'],
    'data': [
        'views/delivery_driver_views.xml',
        'views/fleet_menus.xml',
    ],
    'installable': True,
    'application': False,
}