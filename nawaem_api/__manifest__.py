{
    'name': 'Nawaem API Gateway',
    'version': '1.0',
    'category': 'Technical',
    'summary': 'Custom JSON REST API for Golang Middleware',
    'description': """
        بوابة الربط البرمجية المخصصة لتطبيق نواعم.
        - مصممة للتخاطب السريع مع خوادم Golang.
        - إدارة المصادقة وجلب الكتالوج.
    """,
    'author': 'Novix',
    'depends': ['base','nawaem_core','nawaem_salon'],
    'data': [ 'security/ir.model.access.csv','views/interactions_view.xml','views/res_partner.xml','views/nawaem_waitlist.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
