from odoo import models, fields

class NawaemPortfolio(models.Model):
    _name = 'nawaem.portfolio'
    _description = 'Nawaem Provider Portfolio'

    name = fields.Char(string='عنوان العمل', required=True)
    provider_id = fields.Many2one('res.partner', string='مزود الخدمة', required=True, domain="[('user_type', '=', 'provider')]")
    category_id = fields.Many2one('nawaem.category', string='القسم التابع له', required=True)
    
    media_type = fields.Selection([
        ('image', 'صورة'),
        ('video', 'فيديو (رابط)')
    ], string='نوع الميديا', required=True, default='image')
    
    image = fields.Image(string='الصورة')
    video_url = fields.Char(string='رابط الفيديو')



class NawaemExpertImage(models.Model):
    _name = 'nawaem.expert.image'
    _description = 'Expert Images for Mobile App'
    _rec_name = 'partner_id'

    # ربط الصورة بالخبير
    partner_id = fields.Many2one(
        'res.partner', 
        string='الخبيرة', 
        required=True, 
        ondelete='cascade',
        domain=[('user_type', '=', 'provider')] # لضمان اختيار المزودات فقط
    )
    
    # الصورة المخصصة للتطبيق (أبعاد متوسطة لسرعة التحميل)
    app_image = fields.Image(
        string="صورة التطبيق", 
        max_width=512, 
        max_height=512, 
        verify_resolution=True
    )

    # حقل نصي للملاحظات
    notes = fields.Text(string="ملاحظات")