from flask import Flask, Response
import requests
import json
import random

# create our Flask app
app = Flask(__name__)

def get_simple_price(token):
    token_map = {
        'ETH': 'ethereum',
        'SOL': 'solana',
        'BTC': 'bitcoin',
        'BNB': 'binancecoin',
        'ARB': 'arbitrum'
    }
    token = token.upper()
    if token in token_map:
        return token_map[token]
    else:
        meme_token = get_token_symbol_from_block_height(token)
        return meme_token


def get_token_symbol_from_block_height(block_height):
    url = f'https://api.upshot.xyz/v2/allora/tokens-oracle/token/{block_height}'
    headers = {
        "accept": "application/json",
        "x-api-key": "UP-0d9ed54694abdac60fd23b74"  # Replace with your API key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token_id')  # Extracting 'token_symbol' from the nested 'data' field

    raise ValueError("Unsupported token")


# define our endpoint
@app.route("/inference/<string:token>")
def get_inference(token):
    try:
        github_url = "https://raw.githubusercontent.com/dongqn/allora-huggingface-walkthrough/refs/heads/main/eth"
        response = requests.get(github_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from GitHub: {response.status_code}")

        # Assuming the fetched data is plain text
        data = response.json()  # This will load the JSON data
        value_percent = data.get("value", None)
        print(value_percent)
        base_url = "https://api.coingecko.com/api/v3/simple/price?ids="
        current_token = get_simple_price(token)
        url = f"{base_url}{current_token}&vs_currencies=usd"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "<Your Coingecko API key>"  # replace with your API key
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if token == 'BTC':
                price1 = data["bitcoin"]["usd"] + data["bitcoin"]["usd"] * (value_percent / 100)
                price2 = data["bitcoin"]["usd"] - data["bitcoin"]["usd"] * (value_percent / 100)
            if token == 'ETH':
                price1 = data["ethereum"]["usd"] + data["ethereum"]["usd"] * (value_percent / 100)
                price2 = data["ethereum"]["usd"] - data["ethereum"]["usd"] * (value_percent / 100)
            if token == 'SOL':
                price1 = data["solana"]["usd"] + data["solana"]["usd"] * (value_percent / 100)
                price2 = data["solana"]["usd"] - data["solana"]["usd"] * (value_percent / 100)
            if token == 'BNB':
                price1 = data["binancecoin"]["usd"] + data["binancecoin"]["usd"] * (value_percent / 100)
                price2 = data["binancecoin"]["usd"] - data["binancecoin"]["usd"] * (value_percent / 100)
            if token == 'ARB':
                price1 = data["arbitrum"]["usd"] + data["arbitrum"]["usd"] * (value_percent / 100)
                price2 = data["arbitrum"]["usd"] - data["arbitrum"]["usd"] * (value_percent / 100)
            else:
                price1 = data[current_token]["usd"] + data[current_token]["usd"] * (value_percent / 100)
                price2 = data[current_token]["usd"] - data[current_token]["usd"] * (value_percent / 100)

            random_float = str(round(random.uniform(price1, price2), 7))
        return random_float

    except Exception as e:
        base_url = "https://api.coingecko.com/api/v3/simple/price?ids="
        current_token = get_simple_price(token)
        url = f"{base_url}{current_token}&vs_currencies=usd"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "API"  # replace with your API key
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if token == 'BTC':
                price1 = data["bitcoin"]["usd"] + data["bitcoin"]["usd"] * (value_percent / 100)
                price2 = data["bitcoin"]["usd"] - data["bitcoin"]["usd"] * (value_percent / 100)
            if token == 'ETH':
                price1 = data["ethereum"]["usd"] + data["ethereum"]["usd"] * (value_percent / 100)
                price2 = data["ethereum"]["usd"] - data["ethereum"]["usd"] * (value_percent / 100)
            if token == 'SOL':
                price1 = data["solana"]["usd"] + data["solana"]["usd"] * (value_percent / 100)
                price2 = data["solana"]["usd"] - data["solana"]["usd"] * (value_percent / 100)
            if token == 'BNB':
                price1 = data["binancecoin"]["usd"] + data["binancecoin"]["usd"] * (value_percent / 100)
                price2 = data["binancecoin"]["usd"] - data["binancecoin"]["usd"] * (value_percent / 100)
            if token == 'ARB':
                price1 = data["arbitrum"]["usd"] + data["arbitrum"]["usd"] * (value_percent / 100)
                price2 = data["arbitrum"]["usd"] - data["arbitrum"]["usd"] * (value_percent / 100)
            else:
                price1 = data[current_token]["usd"] + data[current_token]["usd"] * (value_percent / 100)
                price2 = data[current_token]["usd"] - data[current_token]["usd"] * (value_percent / 100)

            random_float = str(round(random.uniform(price1, price2), 7))
        return random_float


# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
