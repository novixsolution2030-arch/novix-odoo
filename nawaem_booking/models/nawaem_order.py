from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class NawaemOrder(models.Model):
    _name = 'nawaem.order'
    _description = 'نظام طلبات نواعم المتطور'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='رقم الطلب', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='العميل', required=True, domain=[('user_type', '=', 'customer')])
    provider_id = fields.Many2one('res.partner', string='المزود المسؤول', tracking=True)
    parent_id = fields.Many2one('nawaem.order', string='الطلب الرئيسي', ondelete='cascade')
    child_ids = fields.One2many('nawaem.order', 'parent_id', string='الطلبات الفرعية للمزودين')
    
    order_type = fields.Selection([
        ('service', 'خدمة فقط'),
        ('product', 'منتجات فقط'),
        ('mixed', 'مختلط (خدمات ومنتجات)')
    ], string='تصنيف الطلب', compute='_compute_order_details', store=True)

    state = fields.Selection([
        ('draft', 'سلة التسوق'),
        ('pending', 'بانتظار المزود'),
        ('accepted', 'تم القبول'),
        ('arrived', 'وصل للموقع'),
        ('completed', 'مكتمل'),
        ('rejected', 'مرفوض'),
        ('cancelled', 'ملغي')
    ], string='الحالة', default='draft', tracking=True)

    booking_date = fields.Datetime(string='موعد الحجز / وقت التوصيل', tracking=True)
    schedule_type = fields.Selection([
        ('fixed', 'حجز موعد مؤكد (خدمة)'),
        ('flexible', 'وقت توصيل مرن (منتج)')
    ], string='نوع الجدولة', compute='_compute_order_details', store=True)

    note = fields.Text(string='ملاحظات العميل')
    reject_reason = fields.Text(string='سبب الرفض')
    order_line_ids = fields.One2many('nawaem.order.line', 'order_id', string='عناصر الطلب')
    
    subtotal = fields.Float(string='إجمالي الأصناف', compute='_compute_totals', store=True)
    total_trip_fees = fields.Float(string='رسوم المشوار', compute='_compute_totals', store=True)
    total_delivery_fees = fields.Float(string='رسوم التوصيل', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='الإجمالي الكلي', compute='_compute_totals', store=True)
    
    start_time_float = fields.Float(string='وقت البداية المختار', required=True)
    end_time_float = fields.Float(string='وقت النهاية المتوقع', compute='_compute_booking_times', store=True)

    @api.depends('start_time_float', 'order_line_ids.service_id', 'order_line_ids.line_type')
    def _compute_booking_times(self):
        for record in self:
            total_duration_minutes = 0
            if record.order_line_ids:
                for line in record.order_line_ids:
                    if line.line_type == 'service' and line.service_id:
                        total_duration_minutes += line.service_id.duration if line.service_id.service_type == 'fixed' else line.service_id.max_duration
            
            if total_duration_minutes == 0:
                total_duration_minutes = 30
            record.end_time_float = record.start_time_float + (total_duration_minutes / 60.0)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('nawaem.order') or _('New')
        return super(NawaemOrder, self).create(vals)

    @api.depends('order_line_ids.line_type')
    def _compute_order_details(self):
        for order in order:
            types = order.order_line_ids.mapped('line_type')
            order.order_type = 'mixed' if 'service' in types and 'product' in types else ('service' if 'service' in types else 'product')
            order.schedule_type = 'fixed' if 'service' in types else 'flexible'

    @api.depends('order_line_ids.price_subtotal', 'order_line_ids.item_fee')
    def _compute_totals(self):
        for order in self:
            order.subtotal = sum(line.price_subtotal for line in order.order_line_ids)
            service_lines = order.order_line_ids.filtered(lambda l: l.line_type == 'service')
            order.total_trip_fees = max(service_lines.mapped('item_fee')) if service_lines else 0.0
            product_lines = order.order_line_ids.filtered(lambda l: l.line_type == 'product')
            order.total_delivery_fees = sum(product_lines.mapped('item_fee'))
            order.total_amount = order.subtotal + order.total_trip_fees + order.total_delivery_fees

    # --- دالة الإرسال المركزية لمحرك Go ---
    def _send_notification_to_go(self, title, body):
        self.ensure_one()
        if not self.customer_id.fcm_token:
            _logger.info(f"Skipping notification for {self.name}: No FCM Token found.")
            return False

        # تأكد من استخدام الرابط الصحيح (IP السيرفر والمنفذ 3001)
        go_url = "http://YOUR_SERVER_IP:3001/api/v1/notifications/send-direct" 
        payload = {
            "user_id": self.customer_id.id,
            "title": title,
            "body": body
        }
        try:
            requests.post(go_url, json=payload, timeout=5)
            return True
        except Exception as e:
            _logger.error(f"Failed to send notification to Go engine: {e}")
            return False

    # === دوال العمليات مع الإشعارات ===
    def action_send_to_provider(self):
        """عندما يؤكد العميل طلبه من السلة"""
        if not self.order_line_ids:
            raise ValidationError(_("لا يمكن إرسال طلب فارغ."))
        self.state = 'pending'
        self._send_notification_to_go(
            "تم استلام طلبك بنجاح! ✨",
            f"طلبك رقم {self.name} بانتظار موافقة المزود. سنقوم بإبلاغك فور قبوله."
        )

    def action_accept(self):
        for rec in self:
            rec.state = 'accepted'
            rec._send_notification_to_go(
                "طلبك في الطريق! 🚀", 
                f"تم قبول طلبك رقم {rec.name} من قبل المزود. استعدي لخدمتك!"
            )

    def action_mark_arrived(self):
        self.state = 'arrived'
        self._send_notification_to_go(
            "وصلنا إلى موقعك! 📍", 
            f"المزود بانتظارك الآن لتنفيذ الطلب {self.name}."
        )

    def action_complete(self):
        self.state = 'completed'
        self._send_notification_to_go(
            "نعيماً لكِ! ✨", 
            f"شكراً لاستخدامك نواعم! نرجو تقييم تجربتك للطلب {self.name}."
        )

    def action_reject(self):
        for rec in self:
            if not rec.reject_reason:
                raise ValidationError(_("يجب كتابة سبب الرفض أولاً."))
            rec.state = 'rejected'
            rec._send_notification_to_go(
                "نعتذر عن تنفيذ طلبك 😔", 
                f"تعذر قبول الطلب {rec.name}. السبب: {rec.reject_reason}"
            )

    def action_cancel(self):
        for rec in self:
            if rec.state in ('draft', 'pending'):
                rec.write({'state': 'cancelled'})
                rec._send_notification_to_go("تم الإلغاء ❌", f"لقد تم إلغاء طلبك رقم {rec.name} بنجاح.")
                if rec.child_ids: rec.child_ids.action_cancel()
            else:
                raise ValidationError(_("لا يمكن إلغاء الطلب بعد قبوله."))
        return True

    def action_split_multi_vendor_order(self):
        self.ensure_one()
        vendors = self.order_line_ids.mapped('provider_id')
        if len(vendors) <= 1:
            self.provider_id = vendors[0].id if vendors else False
            self.action_send_to_provider()
            return True

        for vendor in vendors:
            child_order = self.copy({
                'name': self.name + ' - ' + (vendor.name or ''),
                'parent_id': self.id,
                'provider_id': vendor.id,
                'order_line_ids': [],
                'state': 'pending',
            })
            vendor_lines = self.order_line_ids.filtered(lambda l: l.provider_id == vendor)
            for line in vendor_lines: line.write({'order_id': child_order.id})

        self.write({'state': 'pending', 'provider_id': False})
        self._send_notification_to_go(
            "جاري معالجة طلباتك 🌸", 
            f"تم تقسيم طلبك رقم {self.name} على {len(vendors)} مزودين لضمان أفضل خدمة."
        )
        return True

    @api.model
    def cron_check_abandoned_carts(self):
        import datetime
        two_hours_ago = fields.Datetime.now() - datetime.timedelta(hours=2)
        abandoned_orders = self.search([
            ('state', '=', 'draft'),
            ('write_date', '<=', two_hours_ago),
            ('customer_id.fcm_token', '!=', False)
        ])
        for order in abandoned_orders:
            order._send_notification_to_go(
                "سلتك بانتظارك! 🛒",
                f"يا {order.customer_id.name}، هناك أشياء جميلة بانتظارك في السلة."
            )
            order.write({'write_date': fields.Datetime.now()})

class NawaemOrderLine(models.Model):
    _name = 'nawaem.order.line'
    _description = 'تفاصيل طلب نواعم'

    order_id = fields.Many2one('nawaem.order', string='الطلب', ondelete='cascade')
    line_type = fields.Selection([('service', 'خدمة'), ('product', 'منتج')], string='النوع', required=True)
    service_id = fields.Many2one('nawaem.service', string='الخدمة')
    product_id = fields.Many2one('nawaem.product', string='المنتج')
    provider_id = fields.Many2one('res.partner', string='المزود المالك للصنف', compute='_compute_line_provider', store=True)
    quantity = fields.Float(string='الكمية', default=1.0)
    price_unit = fields.Float(string='سعر الوحدة')
    item_fee = fields.Float(string='رسوم إضافية', compute='_compute_item_fee', store=True)
    price_subtotal = fields.Float(string='الإجمالي', compute='_compute_subtotal', store=True)

    @api.depends('service_id', 'product_id', 'line_type')
    def _compute_line_provider(self):
        for line in self:
            line.provider_id = line.service_id.provider_id if line.line_type == 'service' else line.product_id.provider_id

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self: line.price_subtotal = line.quantity * line.price_unit

    @api.depends('line_type', 'service_id', 'product_id', 'quantity')
    def _compute_item_fee(self):
        for line in self:
            if line.line_type == 'service' and line.service_id:
                line.item_fee = getattr(line.service_id, 'trip_fee', 0.0)
            elif line.line_type == 'product' and line.product_id:
                line.item_fee = getattr(line.product_id, 'delivery_fee', 0.0) * line.quantity
            else:
                line.item_fee = 0.0