from odoo import models, fields

class NawaemCategory(models.Model):
    _name = 'nawaem.category'
    _description = 'Nawaem Category'

    name = fields.Char(string='اسم القسم', required=True)
    category_type = fields.Selection([
        ('service', 'قسم خدمات'),
        ('product', 'قسم منتجات')
    ], string='نوع القسم', required=True, default='service')
    image = fields.Image(string='صورة القسم')
    active = fields.Boolean(default=True, string='نشط')
