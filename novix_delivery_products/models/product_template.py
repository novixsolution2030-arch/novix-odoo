# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class DeliveryMenuCategory(models.Model):
    """ كلاس أقسام المنيو داخل المتجر (مثلاً: مقبلات، وجبات رئيسية، مشروبات) """
    _name = 'delivery.menu.category'
    _description = 'Merchant Menu Category'
    _order = 'sequence, id'

    name = fields.Char(string='Category Name', required=True, translate=True)
    merchant_id = fields.Many2one(
        'res.partner', 
        string='Merchant', 
        domain=[('is_merchant', '=', True)], 
        required=True,
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(string='Display Order', default=10)
    active = fields.Boolean(default=True)


class ProductTemplate(models.Model):
    """ وراثة المنتجات لإضافة خصائص تطبيق التوصيل """
    _inherit = 'product.template'

    # 1. الربط بالمتجر وقسم المنيو
    merchant_id = fields.Many2one(
        'res.partner', 
        string='Merchant / Store', 
        domain=[('is_merchant', '=', True)], 
        index=True,
        tracking=True
    )
    
    menu_category_id = fields.Many2one(
        'delivery.menu.category', 
        string='Menu Category',
        domain="[('merchant_id', '=', merchant_id)]",
        help="القسم الذي سيظهر فيه المنتج داخل منيو المتجر في التطبيق"
    )

    # 2. خصائص العرض في التطبيق
    is_app_available = fields.Boolean(
        string='Show in App', 
        default=True, 
        index=True,
        help="تعطيل هذا الخيار سيخفي المنتج من التطبيق فوراً (مثلاً عند نفاد الكمية)"
    )
    
    preparation_time = fields.Integer(
        string='Prep Time (Mins)', 
        default=15,
        help="الوقت المتوقع لتجهيز هذه الوجبة بالدقائق"
    )
    
    calories = fields.Integer(string='Calories (Kcal)', help="السعرات الحرارية للوجبة")

    # 3. إعدادات السعر والضريبة (تأكيد الحقول القياسية التي سيستخدمها Go)
    # list_price: السعر الأساسي (موجود مسبقاً في أودو)
    # description_sale: وصف المنتج أو المكونات (موجود مسبقاً في أودو)

    # 4. منطق برمجي لضمان سلامة البيانات
    @api.onchange('merchant_id')
    def _onchange_merchant_id(self):
        """ مسح قسم المنيو إذا تغير المتجر لضمان عدم حدوث تعارض """
        if self.menu_category_id and self.menu_category_id.merchant_id != self.merchant_id:
            self.menu_category_id = False

    @api.model
    def create(self, vals):
        """ ضمان تسمية المنتجات وتصنيفها بشكل صحيح عند الإنشاء """
        # يمكنك إضافة منطق هنا مثل التحقق من وجود صورة للمنتج قبل تفعيله في التطبيق
        return super(ProductTemplate, self).create(vals)