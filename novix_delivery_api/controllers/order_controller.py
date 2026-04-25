# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from ..utils.security import require_api_key

class OrderAPIController(http.Controller):

    @http.route('/api/v1/orders/create', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def create_order(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data)
            order_type = payload.get('order_type')
            
            # 1. بناء هيكل الطلب الأساسي وتضمين رسوم التوصيل
            order_vals = {
                'customer_id': payload.get('customer_id'),
                'order_type': order_type,
                'payment_method': payload.get('payment_method', 'cash'),
                'dropoff_lat': payload.get('dropoff_lat'),
                'dropoff_lng': payload.get('dropoff_lng'),
                'distance_km': payload.get('distance_km', 0.0),
                'delivery_fee': payload.get('delivery_fee', 0.0), # <-- الحقل الجديد
            }

            # 2. معالجة المتاجر والسلة
            if order_type in ['food', 'parcel']:
                if not payload.get('merchant_id'):
                    return Response(json.dumps({'error': 'Merchant ID is required'}), status=400, mimetype='application/json')
                
                order_vals['merchant_id'] = payload.get('merchant_id')
                
                order_lines = []
                for item in payload.get('cart_items', []):
                    order_lines.append((0, 0, {
                        'product_id': item.get('product_id'),
                        'name': item.get('name', 'Item'),
                        'quantity': item.get('qty', 1),
                        'price_unit': item.get('price', 0.0),
                    }))
                
                order_vals['order_line_ids'] = order_lines

            # 3. إنشاء الطلب في قاعدة البيانات
            Order = request.env['delivery.order'].sudo()
            new_order = Order.create(order_vals)

            return Response(json.dumps({
                'status': 'success',
                'order_id': new_order.id,
                'total_amount': new_order.total_amount, # إرجاع الإجمالي للتأكيد
                'current_state': new_order.state
            }), status=201, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

    @http.route('/api/v1/orders/status', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def update_order_status(self, **kwargs):
        """
        يحدث حالة الطلب.
        Payload: {"order_id": 10, "action": "merchant_accept|start_bidding|set_delivered|cancel"}
        """
        try:
            payload = json.loads(request.httprequest.data)
            order = request.env['delivery.order'].sudo().browse(payload.get('order_id'))
            
            if not order.exists():
                return Response(json.dumps({'error': 'Order not found'}), status=404, mimetype='application/json')

            action = payload.get('action')
            
            if action == 'merchant_accept':
                order.action_merchant_accept()
            elif action == 'start_bidding':
                order.action_start_bidding()
            elif action == 'set_delivered':
                # هذه الدالة تقوم آلياً بخصم العمولة من محفظة المندوب كما برمجناها سابقاً
                order.action_set_delivered()
            elif action == 'cancel':
                order.action_cancel_order()
            else:
                return Response(json.dumps({'error': 'Invalid action'}), status=400, mimetype='application/json')

            return Response(json.dumps({
                'status': 'success',
                'new_state': order.state
            }), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')


    @http.route('/api/v1/bidding/accept', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def accept_winning_bid(self, **kwargs):
        """
        يستقبل العرض الفائز فقط من Golang لتوثيقه في Odoo وإسناد الطلب للمندوب.
        Payload: {
            "order_id": 10, 
            "driver_id": 45, 
            "bid_amount": 15.0, 
            "estimated_time": 20
        }
        """
        try:
            payload = json.loads(request.httprequest.data)
            
            # 1. إنشاء سجل العرض الفائز مباشرة في Odoo
            Bid = request.env['delivery.bid'].sudo()
            winning_bid = Bid.create({
                'order_id': payload.get('order_id'),
                'driver_id': payload.get('driver_id'),
                'bid_amount': payload.get('bid_amount'),
                'estimated_time': payload.get('estimated_time', 0),
                'state': 'pending' # سيتم تحويله إلى accepted فوراً عبر الدالة
            })

            # 2. استدعاء دالة القبول لإنهاء المزايدة وربط المندوب وتحديث التسعيرة
            winning_bid.action_accept_bid()

            return Response(json.dumps({
                'status': 'success',
                'message': 'Bid accepted and driver assigned',
                'order_state': winning_bid.order_id.state
            }), status=200, mimetype='application/json')

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')