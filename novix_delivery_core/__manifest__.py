{
    'name': 'Novix Delivery Super App',
    'version': '1.0',
    'summary': 'Integrated Core for Delivery, Ride-Hailing, and Bidding',
    'category': 'Operations/Logistics',
    'depends': ['base', 'mail', 'product', 'uom'],
    'data': [
        'security/ir.model.access.csv',
         'security/delivery_security.xml',
        'views/settings_view.xml',
         'views/res_users_view.xml',
        
    ],
    'installable': True,
    'application': True,
}