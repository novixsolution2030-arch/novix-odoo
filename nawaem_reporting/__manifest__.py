{
    'name': 'Nawaem Reporting System',
    'version': '1.0',
    'category': 'Service-Custom',
    'summary': 'نظام التبليغ بين العملاء ومزودي الخدمة لتطبيق نواعم',
    'depends': ['base', 'sale', 'mail','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/report_views.xml',
    ],
    'installable': True,
    'application': False,
}