# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from ..utils.security import require_api_key

class AgentAPIController(http.Controller):

    @http.route('/api/v1/agent/recharge_driver', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def recharge_driver_wallet(self, **kwargs):
        """
        يستدعيه Golang عندما يقوم الوكيل بشحن رصيد مندوب من خلال تطبيق الوكلاء.
        يتم خصم المبلغ من الوكيل، وإيداعه للمندوب، واحتساب العمولة.
        Payload: {"agent_id": 20, "driver_phone": "+24912345678", "amount": 5000}
        """
        try:
            payload = json.loads(request.httprequest.data)
            agent_id = payload.get('agent_id')
            driver_phone = payload.get('driver_phone')
            amount = float(payload.get('amount', 0.0))

            if amount <= 0:
                return Response(json.dumps({'error': 'Amount must be greater than zero'}), status=400, mimetype='application/json')

            # 1. التحقق من الوكيل ورصيده
            agent = request.env['res.partner'].sudo().browse(agent_id)
            if not agent.exists() or not agent.is_recharge_agent:
                return Response(json.dumps({'error': 'Invalid Agent'}), status=403, mimetype='application/json')
            
            if agent.wallet_balance < amount:
                return Response(json.dumps({'error': 'Insufficient agent balance'}), status=400, mimetype='application/json')

            # 2. التحقق من المندوب
            driver = request.env['res.partner'].sudo().search([('mobile', '=', driver_phone), ('is_driver', '=', True)], limit=1)
            if not driver:
                return Response(json.dumps({'error': 'Driver not found with this phone number'}), status=404, mimetype='application/json')

            WalletTx = request.env['wallet.transaction'].sudo()
            
            # 3. خصم المبلغ من محفظة الوكيل (Debit)
            WalletTx.create({
                'partner_id': agent.id,
                'transaction_type': 'debit',
                'amount': amount,
                'source': 'manual', # خصم مقابل تحويل
                'description': f"Transfer to driver {driver.name}",
                'state': 'posted'
            })

            # 4. إيداع المبلغ في محفظة المندوب (Credit) - هذا سيولد عمولة الوكيل آلياً بناءً على الكود السابق
            topup_tx = WalletTx.create({
                'partner_id': driver.id,
                'agent_id': agent.id,
                'transaction_type': 'credit',
                'amount': amount,
                'source': 'topup',
                'description': f"Recharge via Agent {agent.name}",
                'state': 'posted'
            })

            return Response(json.dumps({
                'status': 'success',
                'message': 'Driver recharged successfully',
                'driver_new_balance': driver.wallet_balance,
                'agent_new_balance': agent.wallet_balance
            }), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')