from odoo import models, fields, api

class NawaemAddress(models.Model):
    _name = 'nawaem.address'
    _description = 'عناوين العملاء'
    _rec_name = 'title'

    customer_id = fields.Many2one('res.partner', string='العميل', required=True, ondelete='cascade')
    address_type = fields.Selection([
        ('home', 'المنزل'), 
        ('work', 'العمل'), 
        ('other', 'آخر')
    ], string='نوع العنوان', required=True, default='home')
    
    title = fields.Char(string='عنوان مختصر', help="مثال: منزل الوالد، مكتب الشركة")
    full_address = fields.Text(string='العنوان التفصيلي', required=True)
    latitude = fields.Float(string='خط العرض (Latitude)', digits=(10, 7))
    longitude = fields.Float(string='خط الطول (Longitude)', digits=(10, 7))
    is_default = fields.Boolean(string='عنوان افتراضي', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        # في حال تم تعيين عنوان كافتراضي، يمكننا إزالة الافتراضي من العناوين القديمة لنفس العميل
        for vals in vals_list:
            if vals.get('is_default') and vals.get('customer_id'):
                self.search([('customer_id', '=', vals.get('customer_id'))]).write({'is_default': False})
        return super(NawaemAddress, self).create(vals_list)

    def write(self, vals):
        if vals.get('is_default'):
            for record in self:
                self.search([('customer_id', '=', record.customer_id.id), ('id', '!=', record.id)]).write({'is_default': False})
        return super(NawaemAddress, self).write(vals)
