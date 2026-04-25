{
    'name': 'مقترحات وشكاوى نواعم',
    'version': '1.0',
    'summary': 'إدارة المقترحات والشكاوى الواردة من تطبيق العميل',
    'description': 'موديول متكامل لاستقبال وإدارة الشكاوى والمقترحات مع دعم الـ API وتتبع الحالات.',
    'category': 'Customer Relationship',
    'author': 'Nawaem',
    'depends': ['base', 'mail','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/feedback_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
