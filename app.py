from flask import Flask, jsonify
import requests
import random
import numpy as np
from datetime import datetime, timedelta


app = Flask(__name__)

# Map token symbols to CoinGecko API ids
def get_simple_price(token):
    token_map = {
        'ETH': 'ethereum',
        'SOL': 'solana',
        'BTC': 'bitcoin',
        'BNB': 'binancecoin',
        'ARB': 'arbitrum'
    }
    token = token.upper()
    return token_map.get(token, None)


def get_historical_prices(token):
    current_token = get_simple_price(token)
    if not current_token:
        return None


    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    url = f"https://api.coingecko.com/api/v3/coins/{current_token}/market_chart?vs_currency=usd&days=7&interval=daily"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prices = [entry[1] for entry in data['prices']]  
        return prices
    return None


def calculate_volatility(prices):
    log_returns = np.diff(np.log(prices))  
    volatility = np.std(log_returns) 
    return volatility


@app.route("/inference/<string:token>")
def get_inference(token):
    try:

        historical_prices = get_historical_prices(token)
        if not historical_prices:
            return jsonify({"error": f"Failed to fetch historical prices for {token}"}), 400


        volatility = calculate_volatility(historical_prices)
        current_price = historical_prices[-1] 


        price1 = current_price + current_price * volatility
        price2 = current_price - current_price * volatility


        predicted_price = round(random.uniform(price1, price2), 7)


        return str(predicted_price)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
