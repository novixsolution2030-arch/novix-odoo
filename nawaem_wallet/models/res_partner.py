from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # حقل حسابي لجلب الرصيد الإجمالي من جدول الحركات
    wallet_balance = fields.Float(string='رصيد المحفظة', compute='_compute_wallet_balance', store=True)
    is_available = fields.Boolean(string='متاح لاستقبال الطلبات', default=True, tracking=True)

    def _compute_wallet_balance(self):
        for partner in self:
            # الرصيد = الإيداعات - (الخصومات + التحويلات)
            domain = [('partner_id', '=', partner.id), ('state', '=', 'done')]
            transactions = self.env['nawaem.wallet.transaction'].search(domain)
            
            deposits = sum(transactions.filtered(lambda t: t.transaction_type == 'deposit').mapped('amount'))
            deductions = sum(transactions.filtered(lambda t: t.transaction_type in ['commission', 'transfer']).mapped('amount'))
            
            partner.wallet_balance = deposits - deductions

class WalletTransaction(models.Model):
    _name = 'nawaem.wallet.transaction'
    _description = 'Wallet Transaction'
    _order = 'create_date desc'

    name = fields.Char(string='المرجع', required=True, copy=False, readonly=True, default='/')
    partner_id = fields.Many2one('res.partner', string='صاحب المحفظة', required=True)
    wallet_balance = fields.Float(string='رصيد المحفظة', compute='_compute_wallet_balance')

    # === الحقل المفقود الذي تم إصلاحه ===
    agent_id = fields.Many2one('res.partner', string='الوكيل المسؤول', domain="[('user_type', '=', 'agent')]")
    
    transaction_type = fields.Selection([
        ('deposit', 'إيداع/شحن'),
        ('commission', 'خصم عمولة'),
        ('transfer', 'تحويل/خصم')
    ], string='نوع الحركة', required=True)
    
    amount = fields.Float(string='المبلغ', required=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('done', 'مكتمل'),
        ('cancelled', 'ملغي')
    ], string='الحالة', default='done', required=True) # تم جعله done افتراضياً لعمليات Go
    description = fields.Text(string='البيان/الوصف')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('nawaem.wallet.trx') or '/'
        return super(WalletTransaction, self).create(vals_list)