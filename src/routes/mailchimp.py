from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests

mailchimp_bp = Blueprint('mailchimp_bp', __name__)

MAILCHIMP_API_KEY = '0f7ddd0bbb0f34b5a75a02824ff698ef-us22'
MAILCHIMP_LIST_ID = '9114485dd9'
MAILCHIMP_DATACENTER = 'us22'

@mailchimp_bp.route('/subscribe', methods=['POST'])
@cross_origin()
def subscribe():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    member_info = {
        'email_address': email,
        'status': 'subscribed',
        'merge_fields': {
            'FNAME': name
        }
    }

    url = f'https://{MAILCHIMP_DATACENTER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members'
    headers = {
        'Authorization': f'apikey {MAILCHIMP_API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=member_info, headers=headers)
        
        if response.status_code == 400:
            # Handle member already exists or other client errors
            error_data = response.json()
            if 'title' in error_data and 'Member Exists' in error_data['title']:
                return jsonify({'message': 'Email already subscribed', 'status': 'already_subscribed'}), 200
            else:
                return jsonify({'error': error_data.get('detail', 'Bad request')}), 400
        elif response.status_code == 200:
            return jsonify({'message': 'Successfully subscribed', 'status': 'subscribed'}), 200
        else:
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500


