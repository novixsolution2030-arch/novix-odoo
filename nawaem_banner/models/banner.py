from odoo import models, fields

class NawaemBanner(models.Model):
    _name = 'nawaem.banner'
    _description = 'Nawaem App Banners'
    _order = 'sequence, id'

    name = fields.Char(string='عنوان البنر (Title)', required=True)
    subtitle = fields.Char(string='النص الفرعي (Subtitle)')
    image = fields.Image(string='صورة البنر', max_width=1920, max_height=1080, required=True)
    sequence = fields.Integer(string='الترتيب', default=10)
    active = fields.Boolean(string='مفعل', default=True)
    link_url = fields.Char(string='رابط التوجيه (اختياري)', help="رابط لتحويل العميل عند الضغط على البنر في التطبيق")