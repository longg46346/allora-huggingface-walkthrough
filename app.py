from flask import Flask, Response, jsonify
import requests
import random
import json

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

# Initialize a dictionary to store past inferences and regrets
past_inferences = {}
past_regrets = {}

# Define a function to calculate regret
def calculate_regret(new_inference, token):
    if token in past_inferences:
        previous_inference = past_inferences[token]
        regret = new_inference - previous_inference
        return regret
    else:
        return None

# define our endpoint for price inference
@app.route("/inference/<string:token>")
def get_inference(token):
    try:
        value_percent = 5  # You can dynamically adjust this percentage based on your strategy

        # Prepare API URL and headers
        current_token = get_simple_price(token)
        if not current_token:
            return jsonify({"error": f"Unsupported token: {token}"}), 400

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={current_token}&vs_currencies=usd"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "<Your Coingecko API key>"  # Replace with your API key if needed
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

            # Calculate regret
            regret = calculate_regret(predicted_price, token)
            if regret is not None:
                regret_type = "Positive regret (better performance)" if regret > 0 else "Negative regret (worse performance)"
            else:
                regret_type = "No previous inference to calculate regret."

            # Update past inferences and regrets
            past_inferences[token] = predicted_price
            past_regrets[token] = regret if regret is not None else 0

            # Return the result as JSON
            return str(predicted_price)
        else:
            return f"Failed to fetch price for {token}: {response.status_code}", 400

    except Exception as e:
        return str(e), 400

# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
