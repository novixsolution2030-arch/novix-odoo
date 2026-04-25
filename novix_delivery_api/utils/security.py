# -*- coding: utf-8 -*-
from odoo.http import request, Response
import json
from functools import wraps

# في بيئة الإنتاج، يجب وضع هذا المفتاح في ملف odoo.conf أو متغيرات البيئة
MASTER_API_KEY = "novix_super_secret_golang_key_2026"

def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(json.dumps({'error': 'Missing or Invalid Authorization Header'}), status=401, mimetype='application/json')
        
        token = auth_header.split(' ')[1]
        if token != MASTER_API_KEY:
            return Response(json.dumps({'error': 'Unauthorized API Key'}), status=403, mimetype='application/json')
            
        return func(*args, **kwargs)
    return wrapper