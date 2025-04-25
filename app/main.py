
from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib
import base64
import os

app = Flask(__name__)

API_KEY = os.getenv("LBANK_API_KEY")
API_SECRET = os.getenv("LBANK_API_SECRET")
API_URL = "https://api.lbank.info/v2"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(params, secret):
    sorted_params = sorted(params.items())
    query_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign = hmac.new(secret.encode(), query_str.encode(), hashlib.sha256).hexdigest()
    return sign

def place_order(symbol, side, amount):
    endpoint = "/supplement/place_order"
    url = API_URL + endpoint
    params = {
        "api_key": API_KEY,
        "symbol": symbol,
        "side": side,
        "type": "market",
        "size": amount,
        "timestamp": get_timestamp()
    }
    params["sign"] = sign(params, API_SECRET)
    response = requests.post(url, data=params)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    signal = data.get("signal", "").lower()
    if signal not in ["long", "short"]:
        return jsonify({"status": "invalid signal"}), 400

    # Example balance fraction: 10% of 1000 units (adjust in prod)
    trade_amount = 100  # replace with dynamic balance * 0.10
    side = "buy" if signal == "long" else "sell"
    symbol = "sol_usdt"

    res = place_order(symbol=symbol, side=side, amount=trade_amount)
    return jsonify({"status": "order sent", "exchange_response": res}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
