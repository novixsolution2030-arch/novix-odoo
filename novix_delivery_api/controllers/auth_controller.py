# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from ..utils.security import require_api_key

class AuthAPIController(http.Controller):

    @http.route('/api/v1/auth/sync_user', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def sync_user(self, **kwargs):
        """
        يستقبل بيانات العميل أو المندوب من Golang ويقوم بإنشائه أو جلبه
        Payload: {"phone": "+9665...", "name": "...", "role": "customer|driver"}
        """
        try:
            payload = json.loads(request.httprequest.data)
            phone = payload.get('phone')
            role = payload.get('role', 'customer')

            if not phone:
                return Response(json.dumps({'error': 'Phone number is required'}), status=400, mimetype='application/json')

            Partner = request.env['res.partner'].sudo()
            user = Partner.search([('mobile', '=', phone)], limit=1)

            if not user:
                vals = {
                    'name': payload.get('name', 'New User'),
                    'mobile': phone,
                }
                if role == 'customer':
                    vals['is_app_customer'] = True
                elif role == 'driver':
                    vals['is_driver'] = True
                user = Partner.create(vals)

            return Response(json.dumps({
                'status': 'success',
                'user_id': user.id,
                'is_verified': user.is_phone_verified if role == 'customer' else user.verification_status == 'verified'
            }), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')


    @http.route('/api/v1/auth/verify_otp_success', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def verify_otp_success(self, **kwargs):
        """
        يستدعيه Golang بعد نجاح التحقق من OTP في Redis
        Payload: {"user_id": 123}
        """
        try:
            payload = json.loads(request.httprequest.data)
            user_id = payload.get('user_id')

            user = request.env['res.partner'].sudo().browse(user_id)
            if not user.exists():
                return Response(json.dumps({'error': 'User not found'}), status=404, mimetype='application/json')

            user.is_phone_verified = True

            return Response(json.dumps({'status': 'success', 'message': 'Phone verified successfully'}), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')


    @http.route('/api/v1/auth/bind_device', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def bind_device(self, **kwargs):
        """
        يستدعيه Golang للتحقق من ارتباط جهاز المندوب
        Payload: {"driver_id": 123, "device_id": "UUID-..."}
        """
        try:
            payload = json.loads(request.httprequest.data)
            driver_id = payload.get('driver_id')
            device_id = payload.get('device_id')

            driver = request.env['res.partner'].sudo().browse(driver_id)
            if not driver.exists() or not driver.is_driver:
                return Response(json.dumps({'error': 'Driver not found'}), status=404, mimetype='application/json')

            # إذا لم يكن لديه جهاز مسجل، قم بتسجيله
            if not driver.registered_device_id:
                driver.registered_device_id = device_id
                return Response(json.dumps({'status': 'success', 'action': 'bound'}), status=200, mimetype='application/json')
            
            # إذا كان الجهاز المسجل مختلفاً عن الجهاز القادم في الطلب (محاولة دخول من جهاز آخر)
            elif driver.registered_device_id != device_id:
                return Response(json.dumps({
                    'status': 'error', 
                    'error': 'Account is bound to another device. Contact administration.'
                }), status=403, mimetype='application/json')

            # إذا كان هو نفس الجهاز
            return Response(json.dumps({'status': 'success', 'action': 'verified'}), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')