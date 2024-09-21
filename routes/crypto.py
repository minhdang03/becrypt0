from routes.blog_form import BlogForm
from flask import Blueprint, request, jsonify, render_template, current_app, url_for, redirect, session, flash, send_from_directory
from models.config import db
from models.blogs import Blog
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from utils.decorators import role_required
from werkzeug.utils import secure_filename  # Thay đổi import từ flask sang werkzeug
import logging
import os
import bleach
from html import unescape
import uuid


crypto_bp = Blueprint('crypto', __name__)

API_KEY = 'YOUR_API_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'

def get_signature(query_string):
    return hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_crypto_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Error fetching crypto price: {e}")
        return None

def get_usdt_p2p_price(fiat, trans_amount):
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    payload = {
        "asset": "USDT",
        "fiat": fiat,
        "merchantCheck": True,
        "page": 1,
        "rows": 10,
        "tradeType": "BUY",
        "transAmount": trans_amount
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            return float(data['data'][0]['adv']['price'])
        return None
    except Exception as e:
        print(f"Error fetching USDT P2P price: {e}")
        return None

@crypto_bp.route('/')
@crypto_bp.route('/crypto')
def crypto_page():
    return render_template('crypto.html')

@crypto_bp.route('/crypto-price')
def crypto_price():
    symbol = request.args.get('symbol')
    price = get_crypto_price(symbol)
    if price is not None:
        return jsonify({"price": price})
    else:
        return jsonify({"error": "Không thể lấy giá"}), 500

@crypto_bp.route('/usdt-p2p-price')
def get_usdt_p2p_price_route():
    fiat = request.args.get('fiat', 'VND')
    trans_amount = request.args.get('transAmount', '20000000')
    price = get_usdt_p2p_price(fiat, trans_amount)
    if price is not None:
        return jsonify({"price": price})
    else:
        return jsonify({"error": "Không thể lấy giá"}), 500

@crypto_bp.route('/usd-price')
def get_usd_price_route():
    # Implement the logic to fetch USD price from Vietcombank here
    # Return the price as JSON
    pass
