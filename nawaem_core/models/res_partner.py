from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_type = fields.Selection([
        ('customer', 'عميل'),
        ('provider', 'مزود خدمة'),
        ('agent', 'وكيل')
    ], string='نوع المستخدم', default='customer', required=True)

    unique_code = fields.Char(string='الكود الفريد', readonly=True, copy=False)
    
    # حقول إضافية لمزود الخدمة والوكيل
    commercial_name = fields.Char(string='الاسم التجاري')
    national_id = fields.Char(string='الهوية الوطنية')
    commercial_register = fields.Char(string='السجل التجاري')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('user_type') in ['provider', 'agent','customer'] and not vals.get('unique_code'):
                vals['unique_code'] = self.env['ir.sequence'].next_by_code('nawaem.unique.code') or '/'
        return super(ResPartner, self).create(vals_list)


