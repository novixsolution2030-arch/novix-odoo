from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class WalletTransaction(models.Model):
    _name = 'nawaem.wallet.transaction'
    _description = 'Wallet Transaction'
    _order = 'create_date desc'

    name = fields.Char(string='المرجع', required=True, copy=False, readonly=True, default='/')
    partner_id = fields.Many2one('res.partner', string='صاحب المحفظة', required=True, domain="[('user_type', 'in', ['provider', 'agent'])]")
    transaction_type = fields.Selection([
        ('deposit', 'إيداع/شحن'),
        ('commission', 'خصم عمولة'),
        ('transfer', 'تحويل')
    ], string='نوع الحركة', required=True)
    
    amount = fields.Float(string='المبلغ', required=True)
    date = fields.Datetime(string='التاريخ', default=fields.Datetime.now, required=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('done', 'مكتمل'),
        ('cancelled', 'ملغي')
    ], string='الحالة', default='draft', required=True)
    description = fields.Text(string='البيان/الوصف')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('nawaem.wallet.trx') or '/'
        return super(WalletTransaction, self).create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("يجب أن يكون المبلغ أكبر من صفر."))
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
