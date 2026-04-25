from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class NawaemProduct(models.Model):
    _name = 'nawaem.product'
    _description = 'Nawaem Product'

    name = fields.Char(string='اسم المنتج', required=True)
    provider_id = fields.Many2one('res.partner', string='مزود الخدمة / البائع', required=True, domain="[('user_type', '=', 'provider')]")
    category_id = fields.Many2one('nawaem.category', string='القسم', required=True, domain="[('category_type', '=', 'product')]")
    
    price = fields.Float(string='السعر', required=True)
    description = fields.Text(string='وصف المنتج', required=True)
    promo_video_url = fields.Char(string='رابط فيديو ترويجي (يوتيوب)')
    
    # --- التحديث الجديد: الشحن والتوصيل ---
    shipping_scope = fields.Selection([
        ('local', 'داخل النطاق الجغرافي (الولاية/المدينة)'),
        ('all', 'جميع الولايات'),
        ('specific', 'مناطق / ولايات محددة')
    ], string='نطاق التوصيل', required=True, default='local')
    
    delivery_fee = fields.Float(string='رسوم التوصيل', required=True, default=0.0)
    
    # الاعتماد على نموذج الولايات الافتراضي في أودو
    allowed_state_ids = fields.Many2many('res.country.state', string='المناطق المتاح التوصيل لها')
    
    payment_methods = fields.Selection([
        ('cod', 'كاش عند الاستلام')
    ], string='طرق الدفع', required=True, default='cod')

    image_main = fields.Image(string='الصورة الرئيسية', required=True)
    image_sub_1 = fields.Image(string='صورة فرعية 1', required=True)
    image_sub_2 = fields.Image(string='صورة فرعية 2', required=True)
    image_sub_3 = fields.Image(string='صورة فرعية 3', required=True)

    active = fields.Boolean(default=True, string='متاح')
    provider_name = fields.Char(related='provider_id.name', string='اسم المزود', readonly=True)
    category_name = fields.Char(related='category_id.name', string='اسم القسم', readonly=True)
    @api.constrains('price', 'delivery_fee', 'shipping_scope', 'allowed_state_ids')
    def _check_pricing_and_shipping(self):
        for record in self:
            if record.price < 0:
                raise ValidationError(_("سعر المنتج لا يمكن أن يكون بالسالب."))
            if record.delivery_fee < 0:
                raise ValidationError(_("رسوم التوصيل لا يمكن أن تكون بالسالب."))
            # قيد برمجي صارم: إجبار المزود على اختيار المناطق إذا حدد "مناطق محددة"
            if record.shipping_scope == 'specific' and not record.allowed_state_ids:
                raise ValidationError(_("لقد اخترت 'مناطق محددة' للشحن، يجب عليك تحديد هذه المناطق من القائمة."))