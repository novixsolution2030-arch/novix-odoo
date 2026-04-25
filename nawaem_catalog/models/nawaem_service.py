from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class NawaemService(models.Model):
    _name = 'nawaem.service'
    _description = 'Nawaem Service'

    name = fields.Char(string='اسم الخدمة', required=True)
    provider_id = fields.Many2one('res.partner', string='مزود الخدمة', required=True, domain="[('user_type', '=', 'provider')]")
    category_id = fields.Many2one('nawaem.category', string='القسم', required=True, domain="[('category_type', '=', 'service')]")
    
    price = fields.Float(string='سعر الخدمة', required=True)
    max_persons = fields.Integer(string='أقصى عدد أفراد (0 = مفتوح)', default=1, required=True)
    description = fields.Text(string='وصف مختصر', required=True)
    
    # إلزام بـ 4 صور على الأقل حسب التحليل
    image_main = fields.Image(string='الصورة الرئيسية', required=True)
    image_sub_1 = fields.Image(string='صورة فرعية 1', required=True)
    image_sub_2 = fields.Image(string='صورة فرعية 2', required=True)
    image_sub_3 = fields.Image(string='صورة فرعية 3', required=True)
    
    active = fields.Boolean(default=True, string='متاح')
    service_type = fields.Selection([
        ('fixed', 'مدة ثابتة'),
        ('variable', 'مدة متغيرة (مفتوحة)')
    ], string='نوع الحجز', default='fixed', required=True)

    # 🔴 حقول الوقت بالدقائق
    duration = fields.Integer(string='مدة الخدمة (بالدقائق)', default=60, help="تستخدم للخدمات الثابتة")
    max_duration = fields.Integer(string='الحد الأقصى المتوقع (بالدقائق)', default=120, help="تستخدم للخدمات المفتوحة لحجز الجدول")
    # أضف هذا الحقل داخل كلا النموذجين في أودو
    provider_name = fields.Char(related='provider_id.name', string='اسم المزود', readonly=True)
    category_name = fields.Char(related='category_id.name', string='اسم القسم', readonly=True)
    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price < 0:
                raise ValidationError(_("سعر الخدمة لا يمكن أن يكون بالسالب."))
