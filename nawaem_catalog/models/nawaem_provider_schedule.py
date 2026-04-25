from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class NawaemProviderSchedule(models.Model):
    _name = 'nawaem.provider.schedule'
    _description = 'جدول أوقات عمل المزودين'
    _order = 'day_of_week, start_time'

    provider_id = fields.Many2one(
        'res.partner', 
        string='المزود', 
        required=True, 
        ondelete='cascade',
        domain="[('user_type', '=', 'provider')]"
    )
    
    day_of_week = fields.Selection([
        ('0', 'الإثنين'),
        ('1', 'الثلاثاء'),
        ('2', 'الأربعاء'),
        ('3', 'الخميس'),
        ('4', 'الجمعة'),
        ('5', 'السبت'),
        ('6', 'الأحد')
    ], string='اليوم', required=True)
    
    # استخدام Float لتمويل الوقت (مثلاً 9.5 تعني 9:30) لسهولة الحساب في Go
    start_time = fields.Float(string='من الساعة', required=True)
    end_time = fields.Float(string='إلى الساعة', required=True)
    
    is_active_day = fields.Boolean(string='يوم عمل نشط', default=True)

    @api.constrains('start_time', 'end_time')
    def _check_time_range(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError(_("وقت البدء يجب أن يكون قبل وقت الانتهاء."))
            if record.start_time < 0 or record.end_time > 24:
                raise ValidationError(_("الوقت يجب أن يكون بين 0 و 24."))

    _sql_constraints = [
        ('unique_provider_day', 'unique(provider_id, day_of_week)', 'هذا المزود لديه جدول مسجل لهذا اليوم بالفعل!')
    ]