from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_type = fields.Selection(selection_add=[
        ('salon', 'صالون تجميل (إعلانات ريلز)')
    ], ondelete={'salon': 'set default'})
    
    is_subscribed = fields.Boolean(string='مشترك نشط', default=False)
    subscription_end_date = fields.Date(string='تاريخ نهاية الاشتراك')
    
class NawaemReel(models.Model):
    _name = 'nawaem.reel'
    _description = 'فيديوهات ريلز الأناقة'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # تم دمج الترتيب ليعتمد على الـ sequence أولاً ثم الأحدث
    _order = 'sequence, create_date desc' 

    name = fields.Char(string='عنوان الفيديو', required=True, tracking=True)
    youtube_id = fields.Char(string='YouTube ID', help="يتم تحديثه تلقائياً بعد الرفع", tracking=True)
    description = fields.Text(string='الوصف والهاشتاقات')
    
    salon_id = fields.Many2one('res.partner', string='الصالون المسؤول', 
                                domain=[('user_type', '=', 'salon')], required=True, tracking=True)
    
    # --- الحقول المجلوبة من الكلاس الثاني لتسهيل API الـ Go ---
    salon_name = fields.Char(related='salon_id.name', string='اسم الصالون', readonly=True)
    expert_image = fields.Char(string='رابط الصورة المباشر', help="رابط خارجي لصورة الخبيرة أو مسار الصورة في أودو")
    sequence = fields.Integer(string='الترتيب', default=10)
    # --------------------------------------------------------
    
    temp_video_path = fields.Char(string='مسار الفيديو المؤقت', readonly=True)
    
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('pending', 'بانتظار المراجعة'),
        ('approved', 'تمت الموافقة (جاري الرفع)'),
        ('published', 'منشور'),
        ('rejected', 'مرفوض')
    ], string='الحالة', default='draft', tracking=True)

    # إحصائيات الأداء 
    views_count = fields.Integer(string='المشاهدات', default=0, readonly=True)
    calls_count = fields.Integer(string='الاتصالات', default=0, readonly=True)
    likes_count = fields.Integer(string='الإعجابات', default=0, readonly=True)

    active = fields.Boolean(string='مفعل', default=True)

    # --- قيد قاعدة البيانات المجلوب من الكلاس الثاني ---
    _sql_constraints = [
        ('youtube_id_unique', 'unique(youtube_id)', 'معرف يوتيوب هذا موجود مسبقاً!')
    ]

    # --- دوال التحكم في حالة الفيديو ---
    def action_submit(self):
        self.ensure_one()
        self.state = 'pending'

    def action_approve(self):
        self.ensure_one()
        self.state = 'approved'

    def action_set_published(self, yt_id):
        self.write({
            'state': 'published',
            'youtube_id': yt_id
        })

    def action_reject(self):
        return {
            'name': 'سبب الرفض',
            'type': 'ir.actions.act_window',
            'res_model': 'nawaem.reel.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_reel_id': self.id}
        }