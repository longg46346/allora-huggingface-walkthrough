from decimal import Decimal
from flask import Flask, request, jsonify
import requests
import random
import json

# Create our Flask app
app = Flask(__name__)

# Function to get token symbol from block height
def get_token_symbol_from_block_height(block_height):
    url = f'https://api.upshot.xyz/v2/allora/tokens-oracle/token/{block_height}'
    headers = {
        "accept": "application/json",
        "x-api-key": "UP-0d9ed54694abdac60fd23b74"  # Replace with your API key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token_id')
    else:
        raise ValueError("Unable to retrieve token from this block height")

# Function to get meme coin price from the API
def fetch_meme_coin_price(token):
    base_url = "https://api.coingecko.com/api/v3/simple/price?ids="
    url = f"{base_url}{token}&vs_currencies=usd"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-fEqTDd4Ub2TqSQ8U5qspfucj"  # Replace with your API key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data[token]["usd"]
    else:
        raise Exception(f"Unable to retrieve price for token {token}")

# Function to predict price based on block height
def predict_price(block_height):
    # Get token from block height
    token = get_token_symbol_from_block_height(block_height)

    # Get the meme coin price
    price = fetch_meme_coin_price(token)

    # Generate a random price within 10% of the actual price
    price1 = price + price * 0.10
    price2 = price - price * 0.10
    random_price = round(random.uniform(price1, price2), 7)

    return random_price

# Create an endpoint to predict the price
@app.route("/predict/<string:block_height>", methods=["GET"])
def predict_endpoint(block_height):
    try:
        # Call the predict_price function with block height
        predicted_price = predict_price(block_height)

        # Use Decimal to format the price with fixed precision
        predicted_price_decimal = Decimal(predicted_price).quantize(Decimal('0.00000001'))

        # Return the predicted price as a plain number (string format)
        return str(predicted_price_decimal)
    except Exception as e:
        # Handle exceptions by returning an error in JSON format
        return jsonify({"error": str(e)}), 500

# Run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
