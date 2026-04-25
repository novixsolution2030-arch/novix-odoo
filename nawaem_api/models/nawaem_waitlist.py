from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class NawaemWaitlist(models.Model):
    _name = 'nawaem.waitlist'
    _description = 'قائمة انتظار العملاء (أعلمني)'
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('res.partner', string='العميل', required=True, domain="[('user_type', '=', 'customer')]")
    provider_id = fields.Many2one('res.partner', string='مزودة الخدمة', required=True, domain="[('user_type', '=', 'provider')]")
    requested_date = fields.Date(string='تاريخ الحجز المطلوب', required=True)
    
    status = fields.Selection([
        ('pending', 'في الانتظار'),
        ('notified', 'تم الإشعار'),
        ('cancelled', 'ملغى')
    ], string='الحالة', default='pending', required=True)

    # 🔴 حماية هندسية: منع العميل من تسجيل أكثر من طلب لنفس الخبيرة في نفس اليوم
    @api.constrains('customer_id', 'provider_id', 'requested_date', 'status')
    def _check_duplicate_request(self):
        for record in self:
            if record.status == 'pending':
                domain = [
                    ('customer_id', '=', record.customer_id.id),
                    ('provider_id', '=', record.provider_id.id),
                    ('requested_date', '=', record.requested_date),
                    ('status', '=', 'pending'),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(_("يوجد طلب انتظار نشط مسبقاً لهذا العميل في نفس التاريخ!"))