# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartnerDriver(models.Model):
    _inherit = 'res.partner'

    is_driver = fields.Boolean(string='Is a Driver', default=False, index=True)
    
    # Operational Status (Updated via Golang API)
    driver_status = fields.Selection([
        ('offline', 'Offline'),
        ('online', 'Online - Available'),
        ('busy', 'Busy - On Delivery')
    ], string='Operational Status', default='offline', tracking=True)
    
    # KYC & Verification
    national_id = fields.Char(string='National ID / Iqama', tracking=True)
    verification_status = fields.Selection([
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], string='KYC Status', default='pending', tracking=True)
    
    # Fleet Integration
    vehicle_id = fields.Many2one('fleet.vehicle', string='Assigned Vehicle')
    
    # Real-time Tracking Data (Last known location synced from Redis/Golang)
    current_lat = fields.Float(string='Current Latitude', digits=(10, 7))
    current_lng = fields.Float(string='Current Longitude', digits=(10, 7))
    registered_device_id = fields.Char(
        string='Registered Device ID', 
        tracking=True, 
        help="Unique identifier for the driver's mobile device to prevent multi-device login."
    )

    def action_unbind_device(self):
        """ يمسح معرف الجهاز للسماح للمندوب بتسجيل الدخول من هاتف جديد """
        for record in self:
            if record.registered_device_id:
                record.registered_device_id = False
                # تسجيل الحركة في الـ Chatter للمراقبة الأمنية
                record.message_post(body="تم فك ارتباط جهاز المندوب بواسطة الإدارة والسماح بتسجيل الدخول من جهاز جديد.")