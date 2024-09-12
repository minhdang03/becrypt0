from flask import Blueprint, jsonify, request
import requests
import xml.etree.ElementTree as ET

api_bp = Blueprint('api', __name__)

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
        "transAmount": trans_amount,
        "tradeType": "BUY",
        "page": 1,
        "rows": 1,
        "payTypes": []
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            return float(data['data'][0]['adv']['price'])
        return None
    except Exception as e:
        print(f"Error fetching USDT P2P price: {e}")
        return None

def get_usd_price():
    url = 'https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx'
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for exrate in root.findall('Exrate'):
            if exrate.get('CurrencyCode') == 'USD':
                return float(exrate.get('Sell').replace(',', ''))
        return None
    except Exception as e:
        print(f"Error fetching USD price: {e}")
        return None

@api_bp.route('/all-prices')
def all_prices():
    btc_price = get_crypto_price('BTCUSDT')
    usdt_p2p_price = get_usdt_p2p_price('VND', '20000000')
    usd_price = get_usd_price()

    return jsonify({
        'btc_price': btc_price,
        'usdt_p2p_price': usdt_p2p_price,
        'usd_price': usd_price
    })

@api_bp.route('/btc-price')
def btc_price():
    price = get_crypto_price('BTCUSDT')
    return jsonify({'price': price})

@api_bp.route('/usdt-p2p-price')
def usdt_p2p_price():
    fiat = request.args.get('fiat', 'VND')
    trans_amount = request.args.get('transAmount', '20000000')
    price = get_usdt_p2p_price(fiat, trans_amount)
    return jsonify({'price': price})

@api_bp.route('/usd-price')
def usd_price():
    price = get_usd_price()
    return jsonify({'price': price})