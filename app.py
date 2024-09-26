from flask import Flask, Response
import requests
import json
import random

# create our Flask app
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

# define our endpoint for price inference
@app.route("/inference/<string:token>")
def get_inference(token):
    try:
        value_percent = 5  # You can dynamically adjust this percentage based on your strategy
        print(f"Prediction percentage: {value_percent}%")

        # Prepare API URL and headers
        current_token = get_simple_price(token)
        if not current_token:
            return f"Unsupported token: {token}", 400

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={current_token}&vs_currencies=usd"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-JFn8hKYwt2fqCuowhqRZuMFM"  # Replace with your API key if needed
        }

        # Call the CoinGecko API to get the current price
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            current_price = data[current_token]["usd"]

            # Apply percentage to calculate price range for prediction
            price1 = current_price + current_price * (value_percent / 100)
            price2 = current_price - current_price * (value_percent / 100)

            # Generate a random price within the calculated range
            predicted_price = round(random.uniform(price1, price2), 7)
            return str(predicted_price)
        else:
            return f"Failed to fetch price for {token}: {response.status_code}", 400

    except Exception as e:
        return str(e), 400

# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
    
