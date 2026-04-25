{
    'name': 'عناوين عملاء نواعم',
    'version': '1.0',
    'summary': 'إدارة عناوين العملاء والمواقع الجغرافية',
    'description': 'موديول مخصص لحفظ وإدارة عناوين العملاء (منزل، عمل، أخرى) مع دعم الإحداثيات للربط مع تطبيق فلاتر.',
    'category': 'Customer Relationship',
    'author': 'Nawaem',
    'depends': ['base', 'nawaem_core'],  # تم إضافة nawaem_core لضمان وراثة القائمة الرئيسية
    'data': [
        'security/ir.model.access.csv',
        'views/address_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
