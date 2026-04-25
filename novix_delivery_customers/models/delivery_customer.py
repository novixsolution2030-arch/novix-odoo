# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartnerCustomer(models.Model):
    _inherit = 'res.partner'

    # Customer Identifiers
    is_app_customer = fields.Boolean(string='Is App Customer', default=False, index=True)
    is_phone_verified = fields.Boolean(
        string='Phone Verified', 
        default=False, 
        readonly=True, 
        help="Strictly updated via Golang API post OTP validation."
    )
    
    # Address Management (Used when type == 'delivery')
    address_label = fields.Selection([
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other')
    ], string='Address Label', default='other')
    
    address_lat = fields.Float(string='Latitude', digits=(10, 7))
    address_lng = fields.Float(string='Longitude', digits=(10, 7))