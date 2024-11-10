from flask import Flask, request, jsonify
import requests
from datetime import datetime
import base64
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Daraja API credentials. Ensure to place in .env file

CONSUMER_KEY = 'Nik3oXyBB1AIZBjuLRzXGjcN8nxKA4DJmVGFYTRmm2LGrwHv'
CONSUMER_SECRET = 'qJf2O81qAFLSFV1kRjGbUUP5vITQb9ttLll81b5CcGa2AcDTmqrDMUdzNWqJOQ1l'
BUSINESS_SHORTCODE = '174379'
PASSKEY = ''
CALLBACK_URL = 'https://your-callback-url.com/callback'

#--------------Ensure to place in .env file----------------------#
# Function to get the access token

def get_access_token():
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    response_json = response.json()
    return response_json['access_token']

# Function to generate the password

def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = BUSINESS_SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    return password, timestamp

# Endpoint

@app.route('/payment', methods=['POST'])
def payment():
    data = request.json
    phone_number = data.get('phone')
    amount = data.get('amount')
    
    if not phone_number or not amount:
        return jsonify({'error': 'Phone number and amount are required'}), 400

    access_token = get_access_token()
    password, timestamp = generate_password()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'BusinessShortCode': BUSINESS_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': BUSINESS_SHORTCODE,
        'PhoneNumber': phone_number,
        'CallBackURL': CALLBACK_URL,
        'AccountReference': 'Jakey',
        'TransactionDesc': 'Payment for order'
    }

    stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'


    response = requests.request("GET", 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', json=payload, headers = { 'Authorization': 'Basic TmlrM29YeUJCMUFJWkJqdUxSelhHamNOOG54S0E0REptVkdGWVRSbW0yTEdyd0h2OnFKZjJPODFxQUZMU0ZWMWtSakdiVVVQNXZJVFFiOXR0TGxsODFiNUNjR2EyQWNEVG1xckRNVWR6TldxSk9RMWw=' })
    #print(response.text.encode('utf8'))
    #response = requests.post(stk_push_url, json=payload, headers=headers)
    response_json = response.json()

    # response
    if response.status_code == 200:
        return jsonify({
            'message': 'STK push sent successfully',
            'response': response_json
        }), 200
    else:
        return jsonify({
            'error': 'Failed to send STK push',
            'details': response_json
        }), 500

if __name__ == '__main__':
    app.run(debug=True)