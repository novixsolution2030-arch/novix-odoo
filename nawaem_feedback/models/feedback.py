from odoo import models, fields, api, _

class NawaemFeedback(models.Model):
    _name = 'nawaem.feedback'
    _description = 'مقترحات وشكاوى نواعم'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='رقم المرجع', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='العميل', required=True)
    feedback_type = fields.Selection([
        ('suggestion', 'مقترح'),
        ('complaint', 'شكوى')
    ], string='نوع الطلب', required=True, tracking=True)
    
    message = fields.Text(string='نص الرسالة', required=True)
    attached_image = fields.Binary(string='صورة مرفقة', attachment=True)
    
    state = fields.Selection([
        ('new', 'جديد'),
        ('reviewed', 'قيد المراجعة'),
        ('resolved', 'تم الحل'),
        ('closed', 'مغلق')
    ], string='الحالة', default='new', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('nawaem.feedback') or _('New')
        return super(NawaemFeedback, self).create(vals)

    def action_review(self):
        self.state = 'reviewed'

    def action_resolve(self):
        self.state = 'resolved'

    def action_close(self):
        self.state = 'closed'
