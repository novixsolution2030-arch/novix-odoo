{
    'name': 'Nawaem Wallet',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Wallet management for Providers and Agents',
    'description': """
        إدارة المحافظ الإلكترونية لمزودي الخدمة والوكلاء.
        - تسجيل الحركات المالية (شحن، خصم).
        - حساب الرصيد التلقائي.
    """,
    'author': 'Novix',
    'depends': ['base','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/wallet_transaction_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
