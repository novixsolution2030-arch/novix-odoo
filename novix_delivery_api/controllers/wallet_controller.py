# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from ..utils.security import require_api_key

class WalletAPIController(http.Controller):

    @http.route('/api/v1/wallet/status', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_wallet_status(self, **kwargs):
        """
        يستدعيه Golang للتحقق من رصيد المندوب وأهليته قبل بث أي طلب جديد إليه.
        Query Params: ?partner_id=123
        """
        try:
            partner_id = kwargs.get('partner_id')
            if not partner_id:
                return Response(json.dumps({'error': 'partner_id parameter is required'}), status=400, mimetype='application/json')

            partner = request.env['res.partner'].sudo().browse(int(partner_id))
            if not partner.exists():
                return Response(json.dumps({'error': 'Partner not found'}), status=404, mimetype='application/json')

            return Response(json.dumps({
                'status': 'success',
                'partner_id': partner.id,
                'wallet_balance': partner.wallet_balance,
                'is_eligible_for_orders': partner.is_eligible_for_orders if partner.is_driver else True
            }), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')


    @http.route('/api/v1/wallet/transactions', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_wallet_transactions(self, **kwargs):
        """
        جلب كشف حساب مبسط للمندوب أو العميل لعرضه في التطبيق.
        Query Params: ?partner_id=123&limit=20&offset=0
        """
        try:
            partner_id = kwargs.get('partner_id')
            limit = int(kwargs.get('limit', 20))
            offset = int(kwargs.get('offset', 0))

            if not partner_id:
                return Response(json.dumps({'error': 'partner_id parameter is required'}), status=400, mimetype='application/json')

            transactions = request.env['wallet.transaction'].sudo().search(
                [('partner_id', '=', int(partner_id)), ('state', '=', 'posted')],
                limit=limit,
                offset=offset,
                order='create_date desc'
            )

            tx_list = []
            for tx in transactions:
                tx_list.append({
                    'reference': tx.name,
                    'type': tx.transaction_type,
                    'amount': tx.amount,
                    'source': tx.source,
                    'description': tx.description,
                    'date': tx.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            return Response(json.dumps({
                'status': 'success',
                'partner_id': int(partner_id),
                'transactions': tx_list
            }), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')