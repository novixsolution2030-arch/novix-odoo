# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DeliveryMerchantCategory(models.Model):
    _name = 'delivery.merchant.category'
    _description = 'Merchant Categories'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    icon = fields.Image(string='Category Icon', max_width=128, max_height=128)
    active = fields.Boolean(default=True)
    merchant_ids = fields.Many2many('res.partner', 'merchant_category_rel', 'category_id', 'partner_id', string='Merchants')

class ResPartnerMerchant(models.Model):
    _inherit = 'res.partner'

    # Merchant Identifiers
    is_merchant = fields.Boolean(string='Is a Merchant/Branch', default=False, index=True)
    merchant_type = fields.Selection([
        ('main', 'Main Store (HQ)'),
        ('branch', 'Branch')
    ], string='Merchant Level', default='main')
    
    # Branding
    merchant_banner = fields.Image(
        string='Main Banner', 
        max_width=1920, 
        max_height=600, 
        help="Banner image for the application. Optimal resolution is 1920x600."
    )
    
    # Branch Management
    branch_ids = fields.One2many(
        'res.partner', 
        'parent_id', 
        string='Branches', 
        domain=[('is_merchant', '=', True), ('merchant_type', '=', 'branch')]
    )
    branches_count = fields.Integer(compute='_compute_branches_count', string='Branches Count')

    # Operational Fields
    merchant_category_ids = fields.Many2many(
        'delivery.merchant.category', 
        'merchant_category_rel', 
        'partner_id', 
        'category_id', 
        string='Store Categories'
    )
    is_open = fields.Boolean(string='Currently Accepting Orders', default=True)
    preparation_time = fields.Integer(string='Avg. Prep Time (Mins)', default=15)
    
    # Financial Override
    custom_commission_rate = fields.Float(string='Custom Commission (%)')
    
    # Geolocation fields
    store_lat = fields.Float(string='Latitude', digits=(10, 7))
    store_lng = fields.Float(string='Longitude', digits=(10, 7))

    @api.depends('branch_ids')
    def _compute_branches_count(self):
        for record in self:
            record.branches_count = len(record.branch_ids)

    @api.onchange('parent_id')
    def _onchange_parent_id_merchant(self):
        if self.parent_id and self.parent_id.is_merchant:
            self.merchant_type = 'branch'
            self.is_merchant = True