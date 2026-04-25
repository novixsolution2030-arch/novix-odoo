# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    delivery_system_commission = fields.Float(
        string='System Commission (%)',
        config_parameter='novix_delivery_core.system_commission',
        default=15.0,
        help="Default commission rate taken by the platform per order."
    )
    delivery_base_km_price = fields.Float(
        string='Base Price per KM',
        config_parameter='novix_delivery_core.base_km_price',
        default=1.5,
        help="Base price calculation for distance in SAR."
    )
    delivery_max_distance = fields.Float(
        string='Max Delivery Distance (KM)',
        config_parameter='novix_delivery_core.max_distance',
        default=30.0,
        help="Maximum allowed distance between merchant and customer."
    )
    delivery_bidding_time = fields.Integer(
        string='Bidding Time Limit (Seconds)',
        config_parameter='novix_delivery_core.bidding_time',
        default=60,
        help="Time allowed for drivers to submit bids."
    )
    delivery_min_wallet_balance = fields.Float(
        string='Minimum Wallet Balance for Drivers',
        config_parameter='novix_delivery_core.min_wallet_balance',
        default=0.0,
        help="Drivers with a balance below this cannot receive new orders."
    )
    delivery_agent_commission = fields.Float(
        string='Agent Recharge Commission (%)',
        config_parameter='novix_delivery_core.agent_commission',
        default=2.0,
        help="Percentage of the recharge amount given to the agent as a commission."
    )
    delivery_base_fee = fields.Float(
        string='Delivery Base Fee (SAR)',
        config_parameter='novix_delivery_core.delivery_base_fee',
        default=10.0,
        help="القيمة الأولية (الحد الأدنى) لتوصيل الطلبات."
    )
    delivery_km_price = fields.Float(
        string='Delivery Price per KM (SAR)',
        config_parameter='novix_delivery_core.delivery_km_price',
        default=1.5,
        help="سعر الكيلومتر الواحد لطلبات التوصيل."
    )

    # === تسعيرة التاكسي المشاوير ===
    taxi_base_fee = fields.Float(
        string='Taxi Base Fee / Start Fare (SAR)',
        config_parameter='novix_delivery_core.taxi_base_fee',
        default=8.0,
        help="رسوم فتح العداد (القيمة الأولية) لمشاوير التاكسي."
    )
    taxi_km_price = fields.Float(
        string='Taxi Price per KM (SAR)',
        config_parameter='novix_delivery_core.taxi_km_price',
        default=2.0,
        help="سعر الكيلومتر الواحد للتاكسي."
    )