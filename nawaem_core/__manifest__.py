{
    'name': 'Nawaem Core',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Core module for Nawaem App (Users, Providers, Agents)',
    'description': """
        هذا الموديول يمثل النواة الأساسية لتطبيق نواعم.
        - إدارة أنواع المستخدمين (عميل، مزود خدمة، وكيل).
        - توليد الكود الفريد لمزودي الخدمة والوكلاء.
    """,
    'author': 'Novix',
    'depends': ['base', 'contacts'],
    'data': [
        'security/nawaem_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
