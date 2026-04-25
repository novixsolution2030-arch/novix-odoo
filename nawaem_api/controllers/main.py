# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class NawaemAPI(http.Controller):

    # ---------------------------------------------------------
    # دالات مساعدة (Helpers)
    # ---------------------------------------------------------
    
    def _validate_api_key(self):
        client_key = request.httprequest.headers.get('X-Odoo-API-Key')
        expected_key = request.env['ir.config_parameter'].sudo().get_param('nawaem.api_key', default='47645bd6e7137d6d9b300d6ca498d2ab8a08a0e9')
        return client_key == expected_key

    def _json_response(self, data, status=200):
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=status
        )

    def _get_params(self):
        if request.httprequest.data:
            try:
                return json.loads(request.httprequest.data)
            except:
                return {}
        return request.params

    def _get_image_url(self, model, res_id, field):
        if not res_id: return False
        return f"/web/image?model={model}&id={res_id}&field={field}"

    # ---------------------------------------------------------
    # 1. نظام الكتالوج والمصادقة
    # ---------------------------------------------------------

    @http.route('/api/nawaem/catalog', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def get_catalog(self, **kw):
        if not self._validate_api_key():
            return self._json_response({'status': 401, 'message': 'Unauthorized'}, status=401)
        
        try:
            category_id = kw.get('category_id')
            
            # 1. جلب الأقسام والبنرات دائماً (لضمان ظهورها في كل الشاشات)
            all_categories = request.env['nawaem.category'].sudo().search([('active', '=', True)])
            cat_list = []
            for cat in all_categories:
                cat_list.append({
                    'id': cat.id,
                    'name': cat.name,
                    'category_type': cat.category_type,
                    'image_url': self._get_image_url('nawaem.category', cat.id, 'image'),
                })

            # داخل دالة get_catalog في أودو
                all_banners = request.env['nawaem.banner'].sudo().search([])
                banner_list = []
                for b in all_banners:
                    # 🔴 جرب تغيير 'image' إلى 'image_1920' إذا كنت تستخدم حقل أودو القياسي
                    # أو تأكد من الاسم الذي وضعته في الموديل
                    img_url = self._get_image_url('nawaem.banner', b.id, 'image') 
                    
                    banner_list.append({
                        'id': b.id,
                        'title': b.name,
                        'image_url': img_url,
                    })

            # تهيئة كائن البيانات النهائي
            response_data = {
                'categories': cat_list,
                'banners': banner_list,
                'products': []
            }

            # 2. إذا كان المستخدم داخل قسم معين، نجلب منتجاته أو خدماته
            if category_id:
                category = request.env['nawaem.category'].sudo().browse(int(category_id))
                if category.exists():
                    if category.category_type == 'service':
                        items = request.env['nawaem.service'].sudo().search([
                            ('category_id', '=', category.id),
                            ('active', '=', True)
                        ])
                        for s in items:
                            response_data['products'].append({
                                'id': s.id,
                                'name': s.name,
                                'price': s.price,
                                'rating': 4.5,
                                'reviews': 10,
                                'image_url': self._get_image_url('nawaem.service', s.id, 'image_main'),
                            })
                    
                    elif category.category_type == 'product':
                        items = request.env['nawaem.product'].sudo().search([
                            ('category_id', '=', category.id),
                            ('active', '=', True)
                        ])
                        for p in items:
                            response_data['products'].append({
                                'id': p.id,
                                'name': p.name,
                                'price': p.price,
                                'rating': 5.0,
                                'reviews': 5,
                                'image_url': self._get_image_url('nawaem.product', p.id, 'image_main')
                            })
            else:
                # اختياري: إذا لم يتم اختيار قسم، يمكن عرض المنتجات المميزة (Featured)
                featured = request.env['nawaem.product'].sudo().search([('active', '=', True)], limit=10)
                for p in featured:
                    response_data['products'].append({
                        'id': p.id,
                        'name': p.name,
                        'price': p.price,
                        'rating': 5.0,
                        'image_url': self._get_image_url('nawaem.product', p.id, 'image_main')
                    })

            return self._json_response({'status': 'success', 'data': response_data})

        except Exception as e:
            return self._json_response({'status': 'error', 'message': str(e)}, status=500)
    # 2. نظام سلة التسوق الاحترافي (الموحد)
    # ---------------------------------------------------------

    @http.route('/api/nawaem/cart/checkout', type='json', auth='public', methods=['POST'], csrf=False)
    def checkout_cart(self, **kw):
        params = kw
        items = params.get('items', [])
        customer_id = params.get('customer_id')

        try:
            c_id = int(customer_id)
            order = request.env['nawaem.order'].sudo().search([
                ('customer_id', '=', c_id),
                ('state', '=', 'draft')
            ], limit=1)

            if not order:
                order = request.env['nawaem.order'].sudo().create({
                    'customer_id': c_id,
                    'state': 'draft',
                    'start_time_float': 0.0, # 🟢 إعطاء قيمة افتراضية لتجاوز required=True
                })

            order.order_line_ids.sudo().unlink()
            
            # مصفوفة لتخزين المزودين لضمان المطابقة
            vendor_ids = []

            for item in items:
                i_type = item.get('type')
                p_id = int(item.get('provider_id'))
                vendor_ids.append(p_id)

                line_vals = {
                    'order_id': order.id,
                    'line_type': i_type,
                    'quantity': float(item.get('quantity', 1)),
                    'price_unit': float(item.get('price', 0)),
                }

                if i_type == 'service':
                    service_id = int(item.get('item_id'))
                    line_vals.update({'service_id': service_id})
                else:
                    product_id = int(item.get('item_id'))
                    line_vals.update({'product_id': product_id})
                
                request.env['nawaem.order.line'].sudo().create(line_vals)

            # 🟢 معالجة ذكية للبيانات العامة
            update_data = {
                'note': params.get('note', ''),
                'start_time_float': 10.0, # وقت افتراضي، يمكن تحديثه من Flutter لاحقاً
            }

            # التأكد من تنسيق التاريخ والوقت (Datetime)
            b_date = params.get('booking_date')
            if b_date:
                # إذا وصل تاريخ فقط (YYYY-MM-DD)، نحوله لتنسيق Datetime المتوقع
                if len(b_date) == 10:
                    update_data['booking_date'] = b_date + " 10:00:00"
                else:
                    update_data['booking_date'] = b_date

            # ربط المزود الأول بالطلب لتجاوز الـ Constrains
            if vendor_ids:
                update_data['provider_id'] = vendor_ids[0]

            order.sudo().write(update_data)

            # تنفيذ عملية التقسيم إذا كان هناك أكثر من مزود
            order.action_split_multi_vendor_order()

            return {
                'status': 200,
                'order_id': order.id,
                'message': 'Success'
            }

        except Exception as e:
            return {'status': 500, 'message': str(e)}

    # دالة جلب السلة (لأغراض العرض فقط)
    @http.route('/api/nawaem/cart/get', type='json', auth='public', methods=['POST'], csrf=False)
    def get_cart_details(self, **kw):
        customer_id = kw.get('customer_id')
        order = request.env['nawaem.order'].sudo().search([
            ('customer_id', '=', int(customer_id)),
            ('state', '=', 'draft')
        ], limit=1)

        if not order:
            return {'status': 404, 'message': 'Empty'}

        return {
            'status': 200,
            'data': {
                'order_id': order.id,
                'total': order.total_amount,
                'items': [{
                    'name': l.service_id.name if l.line_type == 'service' else l.product_id.name,
                    'price': l.price_unit,
                    'qty': l.quantity
                } for l in order.order_line_ids]
            }
        }

    # ---------------------------------------------------------
    # 3. نظام تتبع الريلز
    # ---------------------------------------------------------

    @http.route('/api/nawaem/reels/track', type='http', auth='public', methods=['POST'], csrf=False)
    def track_reel_interaction(self, **kw):
        if not self._validate_api_key(): return self._json_response({'status': 401}, status=401)
        params = self._get_params()
        reel_id = params.get('reel_id')
        action = params.get('action') 

        try:
            reel = request.env['nawaem.reel'].sudo().browse(int(reel_id))
            if reel.exists():
                if action == 'view': reel.sudo().write({'views_count': reel.views_count + 1})
                return self._json_response({'status': 200})
            return self._json_response({'status': 404}, status=404)
        except Exception as e:
            return self._json_response({'status': 500}, status=500)