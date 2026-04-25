# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError # تأكد من استدعاء هذه المكتبة
class DeliveryOrderLine(models.Model):
    _name = 'delivery.order.line'
    _description = 'Delivery Order Line (Cart Item)'

    order_id = fields.Many2one('delivery.order', string='Order Reference', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.list_price


class DeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    
    # Core Entities
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_app_customer', '=', True)], required=True, tracking=True)
    merchant_id = fields.Many2one('res.partner', string='Merchant', domain=[('is_merchant', '=', True)], required=True, tracking=True)
    driver_id = fields.Many2one('res.partner', string='Assigned Driver', domain=[('is_driver', '=', True)], tracking=True)
    distance_km = fields.Float(string='Distance (KM)', tracking=True)
    delivery_fee = fields.Float(string='Delivery Fee', tracking=True)

    # الحقول المالية المحسوبة
    items_total = fields.Float(string='Items Total', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='Total Amount (Items + Delivery)', compute='_compute_totals', store=True)
    # Updated State Machine
    state = fields.Selection([
        ('draft', 'Cart / Drafting'),
        ('pending_merchant', 'Awaiting Merchant Approval'),
        ('merchant_accepted', 'Merchant Preparing'),
        ('bidding', 'Bidding (Searching Driver)'),
        ('driver_assigned', 'Driver On the Way to Pickup'),
        ('delivering', 'Order Picked Up / Delivering'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    # Cart & Payment
    order_line_ids = fields.One2many('delivery.order.line', 'order_id', string='Order Lines (Cart)')
    payment_method = fields.Selection([
        ('cash', 'Cash on Delivery (COD)'),
        ('wallet', 'Wallet Balance'),
        ('online', 'Online Payment (Card)')
    ], string='Payment Method', required=True, default='cash', tracking=True)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('reserved', 'Reserved (Escrow)'),
        ('paid', 'Paid')
    ], string='Payment Status', default='unpaid', tracking=True)
    # Core Entities (أضف هذا الحقل تحت هذه المنطقة)
    order_type = fields.Selection([
        ('food', 'Food Delivery'),
        ('parcel', 'Parcel Delivery'),
        ('ride', 'Passenger Ride')
    ], string='Service Type', required=True, default='food', tracking=True)
    # Locations
    pickup_lat = fields.Float(string='Pickup Latitude', related='merchant_id.store_lat', store=True)
    pickup_lng = fields.Float(string='Pickup Longitude', related='merchant_id.store_lng', store=True)
    dropoff_lat = fields.Float(string='Dropoff Latitude')
    dropoff_lng = fields.Float(string='Dropoff Longitude')
    distance_km = fields.Float(string='Estimated Distance (KM)')

    # Financials
    goods_cost = fields.Float(string='Cost of Goods', compute='_compute_goods_cost', store=True, tracking=True)
    delivery_fee = fields.Float(string='Agreed Delivery Fee', default=0.0, tracking=True)
    system_commission_amount = fields.Float(string='System Commission', compute='_compute_commission', store=True)
    total_amount = fields.Float(string='Total to Pay', compute='_compute_total', store=True)
    merchant_id = fields.Many2one(
        'res.partner', 
        string='Merchant/Pickup Point', 
        domain=[('is_merchant', '=', True)], 
        tracking=True
    )
    @api.depends('order_line_ids.price_unit', 'order_line_ids.quantity', 'delivery_fee')
    def _compute_totals(self):
        for order in self:
            # جمع قيمة سطور السلة (المنتجات)
            items_sum = sum(line.price_unit * line.quantity for line in order.order_line_ids)
            order.items_total = items_sum
            
            # الإجمالي النهائي = المنتجات + التوصيل
            order.total_amount = items_sum + order.delivery_fee
    # 2. إضافة قيد التحقق الديناميكي
    @api.constrains('order_type', 'merchant_id')
    def _check_merchant_requirement(self):
        for order in self:
            if order.order_type in ['food', 'parcel'] and not order.merchant_id:
                raise ValidationError(_("Merchant is required for Food and Parcel delivery orders."))

    # 3. تعديل دالة الإرسال لتجاوز المتجر في طلبات التاكسي
    def action_submit_order(self):
        for order in self:
            if order.order_type == 'ride':
                # التاكسي ينتقل للمزايدة مباشرة
                order.write({'state': 'bidding'})
            else:
                # الطعام والطرود تحتاج متجر وسلة
                if not order.order_line_ids and order.order_type == 'food':
                    raise ValidationError(_("Cannot submit an empty cart for food orders."))
                order.write({'state': 'pending_merchant'})
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('delivery.order') or _('New')
        return super(DeliveryOrder, self).create(vals_list)

    @api.depends('order_line_ids.price_subtotal')
    def _compute_goods_cost(self):
        for order in self:
            order.goods_cost = sum(order.order_line_ids.mapped('price_subtotal'))

    @api.depends('goods_cost', 'delivery_fee', 'merchant_id')
    def _compute_commission(self):
        for order in self:
            commission_rate = order.merchant_id.custom_commission_rate
            if not commission_rate:
                commission_rate = float(self.env['ir.config_parameter'].sudo().get_param('novix_delivery_core.system_commission', default=15.0))
            order.system_commission_amount = (order.delivery_fee * commission_rate) / 100.0

    @api.depends('goods_cost', 'delivery_fee')
    def _compute_total(self):
        for order in self:
            order.total_amount = order.goods_cost + order.delivery_fee

    # State Transition Actions
    def action_submit_to_merchant(self):
        if not self.order_line_ids:
            raise models.ValidationError("Cannot submit an empty cart.")
        self.write({'state': 'pending_merchant'})

    def action_merchant_accept(self):
        self.write({'state': 'merchant_accepted'})

    def action_start_bidding(self):
        self.write({'state': 'bidding'})

    def action_cancel_order(self):
        self.write({'state': 'cancelled'})

    def action_set_delivered(self):
        """ يتم استدعاؤها من Golang عندما يؤكد المندوب تسليم الطلب """
        for order in self:
            if order.state != 'delivering':
                continue
            
            # 1. تغيير حالة الطلب
            order.write({'state': 'delivered'})
            
            # 2. إنشاء حركة خصم العمولة من محفظة المندوب (إذا كان الدفع كاش)
            if order.payment_method == 'cash' and order.system_commission_amount > 0:
                self.env['wallet.transaction'].create({
                    'partner_id': order.driver_id.id,
                    'transaction_type': 'debit',
                    'amount': order.system_commission_amount,
                    'source': 'commission',
                    'order_id': order.id,
                    'description': f"System Commission Deduction for Order {order.name} (COD)",
                    'state': 'posted' # ترحيل الحركة المالية فوراً
                })