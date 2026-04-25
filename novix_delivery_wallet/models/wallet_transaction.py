# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WalletTransaction(models.Model):
    _name = 'wallet.transaction'
    _description = 'Wallet Transaction Ledger'
    _order = 'create_date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string='Transaction Ref', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Account Holder', required=True, tracking=True)
    
    transaction_type = fields.Selection([
        ('credit', 'Credit (Add Funds)'),
        ('debit', 'Debit (Deduct Funds)')
    ], string='Type', required=True, tracking=True)
    
    amount = fields.Float(string='Amount', required=True, tracking=True)
    
    agent_id = fields.Many2one(
        'res.partner', 
        string='Processed By (Agent)', 
        default=lambda self: self.env.user.partner_id,
        readonly=True,
        tracking=True
    )

    # 2. تحديث مصادر الحركات لتشمل عمولة الوكيل
    source = fields.Selection([
        ('manual', 'Manual Adjustment'),
        ('order', 'Order Payment / Payout'),
        ('commission', 'System Commission Deduction'),
        ('topup', 'Wallet Top-up (Recharge)'),
        ('agent_commission', 'Agent Recharge Reward') # المصدر الجديد
    ], string='Source', default='manual', required=True)
    
    order_id = fields.Many2one('delivery.order', string='Related Order', help="Linked order if applicable")
    description = fields.Char(string='Description', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # حقل مستقبلي للربط مع القيود المحاسبية الرسمية لـ Odoo
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('wallet.transaction') or _('New')
        return super(WalletTransaction, self).create(vals_list)

    def action_post(self):
        # جلب نسبة عمولة الوكيل من إعدادات النظام
        agent_commission_pct = float(self.env['ir.config_parameter'].sudo().get_param('novix_delivery_core.agent_commission', default=0.0))
        
        for tx in self:
            if tx.amount <= 0:
                raise UserError(_("Amount must be strictly positive."))
            
            tx.write({'state': 'posted'})

            # 3. المنطق التجاري: توليد عمولة الوكيل آلياً
            if tx.source == 'topup' and tx.transaction_type == 'credit' and agent_commission_pct > 0:
                agent = tx.agent_id
                
                # التحقق من أن منفذ العملية هو وكيل معتمد وليس المندوب نفسه أو مدير عام
                if agent and agent.is_recharge_agent:
                    commission_amount = (tx.amount * agent_commission_pct) / 100.0
                    
                    # إنشاء حركة إيداع في محفظة الوكيل
                    self.env['wallet.transaction'].create({
                        'partner_id': agent.id,
                        'transaction_type': 'credit',
                        'amount': commission_amount,
                        'source': 'agent_commission',
                        'description': f"Reward for recharging {tx.partner_id.name} (Ref: {tx.name})",
                        'state': 'posted' # ترحيل فوري
                    })

    def action_cancel(self):
        for tx in self:
            if tx.state == 'posted':
                raise UserError(_("Cannot cancel a posted transaction. You must create a reversing entry."))
            tx.write({'state': 'cancelled'})