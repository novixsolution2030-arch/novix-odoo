# -*- coding: utf-8 -*-
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_type = fields.Selection([
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('merchant', 'Merchant'),
        ('agent', 'Recharge Agent'),
        ('admin', 'System Admin')
    ], string='App User Type', default='customer', index=True, tracking=True)

    is_available = fields.Boolean(
        string='Is Online', 
        default=False, 
        help="يستخدم هذا الحقل للمناديب فقط لتحديد حالتهم اللحظية"
    )