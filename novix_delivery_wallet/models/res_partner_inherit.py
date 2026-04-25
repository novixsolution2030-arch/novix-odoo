# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartnerWallet(models.Model):
    _inherit = 'res.partner'

    wallet_transaction_ids = fields.One2many('wallet.transaction', 'partner_id', string='Transactions')
    wallet_balance = fields.Float(string='Wallet Balance', compute='_compute_wallet_balance')
    is_eligible_for_orders = fields.Boolean(
        string='Eligible for Orders', 
        compute='_compute_eligibility', 
        store=False, # لا يتم تخزينه لأنه يعتمد على إعدادات عامة تتغير
        help="Checks if wallet balance is above the minimum threshold."
    )
    is_recharge_agent = fields.Boolean(string='Is Recharge Agent', default=False, index=True)
    @api.depends('wallet_balance')
    def _compute_eligibility(self):
        min_balance = float(self.env['ir.config_parameter'].sudo().get_param('novix_delivery_core.min_wallet_balance', default=0.0))
        for partner in self:
            if partner.is_driver:
                partner.is_eligible_for_orders = partner.wallet_balance >= min_balance
            else:
                partner.is_eligible_for_orders = False
    @api.depends('wallet_transaction_ids.amount', 'wallet_transaction_ids.state', 'wallet_transaction_ids.transaction_type')
    def _compute_wallet_balance(self):
        for partner in self:
            # نجمع الإيداعات (Credit)
            credits = sum(partner.wallet_transaction_ids.filtered(
                lambda t: t.state == 'posted' and t.transaction_type == 'credit'
            ).mapped('amount'))
            
            # نجمع السحوبات (Debit)
            debits = sum(partner.wallet_transaction_ids.filtered(
                lambda t: t.state == 'posted' and t.transaction_type == 'debit'
            ).mapped('amount'))
            
            partner.wallet_balance = credits - debits