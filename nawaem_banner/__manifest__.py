{
    'name': 'Nawaem App Banners',
    'version': '1.0',
    'summary': 'إدارة بنرات العروض لتطبيق نواعم',
    'category': 'Website',
    'author': 'Technical Admin',
    'depends': ['base','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/banner_views.xml',
    ],
    'installable': True,
    'application': False,
}