from odoo import models, fields, api

class NawaemReview(models.Model):
    _name = 'nawaem.review'
    _description = 'التقييمات والتعليقات'
    _order = 'create_date desc'

    customer_id = fields.Many2one('res.partner', string='العميل', required=True, domain=[('user_type', '=', 'customer')])
    
    # تحديد الهدف المراد تقييمه
    provider_id = fields.Many2one('res.partner', string='مزود الخدمة', domain=[('user_type', 'in', ['provider', 'salon'])])
    service_id = fields.Many2one('nawaem.service', string='الخدمة')
    product_id = fields.Many2one('nawaem.product', string='المنتج') 
    
    rating = fields.Integer(string='التقييم', required=True, default=5)
    comment = fields.Text(string='التعليق')
    reel_id = fields.Many2one('nawaem.reel', string='الريلز', required=True)
class NawaemReelInteraction(models.Model):
    _name = 'nawaem.reel.interaction'
    _description = 'تفاعلات الريلز'
    _order = 'create_date desc'

    reel_id = fields.Many2one('nawaem.reel', string='الريلز', required=True)
    customer_id = fields.Many2one('res.partner', string='العميل', required=True)
    interaction_type = fields.Selection([
        ('like', 'إعجاب'),
        ('share', 'مشاركة'),
        ('comment', 'تعليق')
    ], string='نوع التفاعل', required=True)
    
    comment_text = fields.Text(string='نص التعليق')

    # Trigger: تحديث عداد الإعجابات في الريلز تلقائياً عند إضافة إعجاب
    @api.model_create_multi
    def create(self, vals_list):
        records = super(NawaemReelInteraction, self).create(vals_list)
        for rec in records:
            if rec.interaction_type == 'like' and rec.reel_id:
                rec.reel_id.likes_count += 1
        return records