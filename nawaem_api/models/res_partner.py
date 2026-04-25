from odoo import models, fields,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # إضافة حقول الموقع الجغرافي الخاصة بتطبيق نواعم
    nawaem_latitude = fields.Float(string='خط العرض (Latitude)', digits=(16, 7))
    nawaem_longitude = fields.Float(string='خط الطول (Longitude)', digits=(16, 7))
    nawaem_password = fields.Char(string='App Password')
    fcm_token = fields.Char(string='FCM Token (Firebase)', help="يستخدم لإرسال الإشعارات المباشرة لهاتف المستخدم")
    temporary_close = fields.Boolean(
        string='إغلاق مؤقت (استراحة)', 
        default=False,
        help='قم بتفعيل هذا الزر لإيقاف استقبال الحجوزات مؤقتاً وإظهار رسالة للعملاء بأن الخبيرة في استراحة.'
    )
    last_active_date = fields.Datetime(string='آخر ظهور', default=fields.Datetime.now)

    def send_push_notification(self, title, body):
        """دالة مركزية لإرسال البيانات إلى محرك Go ليقوم بضخها"""
        self.ensure_one()
        if not self.fcm_token:
            return False

        # ⚠️ استبدل الرابط برابط محرك Go الخاص بك
        go_engine_url = "http://127.0.0.1:3000/api/notifications/send"
        payload = {
            "token": self.fcm_token,
            "title": title,
            "body": body
        }
        
        try:
            # نستخدم timeout قصير حتى لا يتعطل أودو إذا تأخر محرك Go
            response = requests.post(go_engine_url, json=payload, timeout=3)
            return response.status_code == 200
        except Exception as e:
            _logger.error(f"فشل الاتصال بمحرك Go لإرسال الإشعار: {e}")
            return False

    @api.model
    def cron_check_abandoned_carts(self):
        """وظيفة مجدولة تعمل كل ساعة للبحث عن السلات المتروكة"""
        # جلب الطلبات (المسودات) التي مر عليها أكثر من 3 ساعات ولم تتأكد
        domain = [
            ('state', '=', 'draft'),
            ('write_date', '<=', fields.Datetime.subtract(fields.Datetime.now(), hours=3))
        ]
        abandoned_orders = self.env['sale.order'].search(domain)

        for order in abandoned_orders:
            if order.partner_id.fcm_token:
                order.partner_id.send_push_notification(
                    title="سلتك بانتظارك! 🛒",
                    body=f"يا {order.partner_id.name}، منتجاتك في السلة اشتاقت ليك، أكملي طلبك الآن."
                )
                # تحديث الوقت حتى لا نرسل له إشعاراً كل ساعة (تجنب الإزعاج)
                order.write({'write_date': fields.Datetime.now()})
    def write(self, vals):
        # 1. تنفيذ التعديل الأساسي أولاً
        res = super(ResPartner, self).write(vals)
        
        # 2. إذا كان التعديل يتضمن إعادة فتح الحجوزات (temporary_close = False)
        if 'temporary_close' in vals and vals['temporary_close'] is False:
            for partner in self:
                partner._process_waitlist_notifications()
                
        return res

    def _process_waitlist_notifications(self):
        """
        تبحث هذه الدالة عن كل العملاء المنتظرين للخبيرة في تاريخ اليوم وما بعده،
        وترسل لهم إشعارات، ثم تغلق الطلب.
        """
        today = fields.Date.context_today(self)
        
        # جلب الطلبات المعلقة لهذه الخبيرة
        waitlists = self.env['nawaem.waitlist'].search([
            ('provider_id', '=', self.id),
            ('status', '=', 'pending'),
            ('requested_date', '>=', today) # تجاهل التواريخ القديمة
        ])

        for wl in waitlists:
            # 🔴 استدعاء دالة الإرسال (FCM)
            self._send_fcm_notification_to_customer(wl.customer_id, self.name)
            
            # تحديث حالة الطلب لكي لا يتم إرسال الإشعار مرة أخرى
            wl.write({'status': 'notified'})

    def _send_fcm_notification_to_customer(self, customer, provider_name):
        """
        منطقة ربط Firebase Cloud Messaging
        """
        if not customer.fcm_token:
            return # إذا لم يكن للعميل توكن، نتجاوز
            
        title = "المواعيد متاحة الآن! 🥳"
        body = f"أخبار رائعة! الخبيرة {provider_name} أصبحت متاحة لاستقبال الحجوزات، سارعي قبل امتلاء الجدول."
        
        # يمكنك هنا استدعاء مكتبة requests لإرسال الإشعار مباشرة إلى Firebase
        # أو تسجيلها في جدول الإشعارات الخاص بك ليتولى محرك Go إرسالها
        # مثال وهمي:
        # self.env['nawaem.notification'].create({'user_id': customer.id, 'title': title, 'body': body})