# -*- coding: utf-8 -*-
{
    'name': 'Novix Delivery Orders',
    'version': '1.0',
    'category': 'Operations/Delivery',
    'summary': 'Core Order Management and State Machine',
    'author': 'NOVIX',
   'depends': [
        'product', # تمت الإضافة لدعم السلة والأصناف
        'novix_delivery_core',
        'novix_delivery_merchants',
        'novix_delivery_fleet',
        'novix_delivery_customers'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/order_sequence.xml',
        'views/delivery_order_views.xml',
        'views/order_menus.xml',
    ],
    'installable': True,
    'application': False,
}