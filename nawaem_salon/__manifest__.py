{
    'name': 'Nawaem Salon & Reels Management',
    'version': '1.1',
    'category': 'Marketing',
    'summary': 'إدارة الصالونات، اشتراكات الريلز، ونظام مراجعة الفيديوهات قبل النشر',
    'depends': ['base','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
