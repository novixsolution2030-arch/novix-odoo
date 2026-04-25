{
    'name': 'Nawaem Catalog',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Catalog management (Categories, Services, Products, Portfolios)',
    'description': """
        إدارة الكتالوج لتطبيق نواعم.
        - الأقسام الرئيسية (خدمات تجميل، منتجات محلية).
        - الخدمات وإدارة الأسعار والطاقة الاستيعابية.
        - المنتجات وتفاصيل الشحن.
        - معرض الأعمال (سابقة الأعمال للمزودين).
    """,
    'author': 'Novix',
    'depends': ['base','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/nawaem_category_views.xml',
        'views/nawaem_service_views.xml',
        'views/nawaem_product_views.xml',
        'views/provider_schedule_views.xml',
        'views/nawaem_portfolio_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
