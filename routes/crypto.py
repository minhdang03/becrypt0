from flask import Blueprint, jsonify, request, render_template, Flask
import requests

crypto_bp = Blueprint('crypto', __name__)

def get_crypto_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
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
            price = float(data['data'][0]['adv']['price'])
            return round(price)
        else:
            print("No data available")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
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
    price = get_usdt_p2p_price('VND', '20000000')
    if price is not None:
        return jsonify({"price": price})
    else:
        return jsonify({"error": "Không thể lấy giá"}), 500

@crypto_bp.route('/usd-price')
def get_usd_price_route():
    # Implement the logic to fetch USD price from Vietcombank here
    # Return the price as JSON
    pass


