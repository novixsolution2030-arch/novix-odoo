{
    'name': 'Nawaem Booking & Orders',
    'version': '1.0',
    'category': 'Operations',
    'summary': 'Manage customer bookings, product orders, and provider tracking',
    'description': """
        إدارة الطلبات والحجوزات لتطبيق نواعم.
        - دورة حياة الطلب (مسودة، انتظار، مقبول، مكتمل، ملغي).
        - ربط الطلبات بالمحافظ لخصم العمولة التلقائي.
        - التحقق من الطاقة الاستيعابية.
        - الإلغاء التلقائي للطلبات المعلقة.
    """,
    'author': 'Novix',
    'depends': ['base','nawaem_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/cron_jobs.xml',
        'views/nawaem_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
