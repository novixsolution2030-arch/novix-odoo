from odoo import http
from odoo.http import request

class NawaemFeedbackAPI(http.Controller):
    
    @http.route('/api/nawaem/feedback/submit', type='json', auth='public', methods=['POST'], csrf=False)
    def submit_feedback(self, **kw):
        params = kw
        customer_id = params.get('customer_id')
        f_type = params.get('feedback_type')
        message = params.get('message')
        image_base64 = params.get('image')

        if not customer_id or not f_type or not message:
            return {'status': 400, 'message': 'البيانات الأساسية مطلوبة (العميل، النوع، الرسالة)'}

        try:
            feedback = request.env['nawaem.feedback'].sudo().create({
                'customer_id': int(customer_id),
                'feedback_type': f_type,
                'message': message,
                'attached_image': image_base64,
            })
            return {
                'status': 200, 
                'message': 'تم استلام طلبك بنجاح', 
                'ticket_id': feedback.name
            }
        except Exception as e:
            return {'status': 500, 'message': str(e)}
