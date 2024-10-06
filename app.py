from flask import Flask, Response, jsonify
import requests
import random
import time
import threading

# create our Flask app
app = Flask(__name__)

CG_Keys = [
    "<Your Coingecko API key>"

]

UP_Keys = [
    "<Your UP API key>Y"

]

max_concurrent_requests = 500 
semaphore = threading.Semaphore(max_concurrent_requests)

def get_memecoin_token(blockheight):
    UP_Keys_copy = UP_Keys.copy()  # Create a copy of the key list
    retries = len(UP_Keys_copy)    # Number of available keys
    used_keys = set()              # Track used keys
    
    while len(used_keys) < retries:
        # Randomly select a key that hasn't been used yet
        UP_Key = random.choice([key for key in UP_Keys_copy if key not in used_keys])
        used_keys.add(UP_Key)      # Add the selected key to the used list

        upshot_url = f"https://api.upshot.xyz/v2/allora/tokens-oracle/token/{blockheight}"
        headers = {
            'accept': 'application/json',
            'x-api-key': UP_Key
        }

        response = requests.get(upshot_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            name_token = str(data["data"]["token_id"])
            return name_token
        else:
            print(f"Key {UP_Key} failed with status code: {response.status_code}")
            # No delay here, just retry with a different key

    raise ValueError(f"Failed to get token after using all keys. Last status code: {response.status_code}")

def get_simple_price(token):
    CG_Keys_copy = CG_Keys.copy() 
    retries = len(CG_Keys_copy)
    used_keys = set()          
    
    base_url = "https://api.coingecko.com/api/v3/simple/price?ids="
    token_map = {
        'ETH': 'ethereum',
        'SOL': 'solana',
        'BTC': 'bitcoin',
        'BNB': 'binancecoin',
        'ARB': 'arbitrum'
    }
    token = token.upper()

    while len(used_keys) < retries:
        CG_Key = random.choice([key for key in CG_Keys_copy if key not in used_keys])
        used_keys.add(CG_Key)
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": CG_Key
        }
        
        if token in token_map:
            url = f"{base_url}{token_map[token]}&vs_currencies=usd"
        else:
            token = token.lower()
            url = f"{base_url}{token}&vs_currencies=usd"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if token in token_map:
                price = data[token_map[token]]["usd"]
            else:
                price = data[token]["usd"]
            return price
        else:
            print(f"Key {CG_Key} failed with status code: {response.status_code}")
    
    raise ValueError("Failed to get price after using all keys.")

def get_raw_value(filename="raw_value.txt"):
    try:
        with open(filename, "r") as file:
            return float(file.read().strip())
    except Exception as e:
       collect_raw_value()
       
@app.route("/inference/<string:tokenorblockheightorparty>")
def get_inference(tokenorblockheightorparty):
    try:
        semaphore.acquire()

        raw_value = get_raw_value()
        predict_result = None
        tokenorblockheightorparty = tokenorblockheightorparty.upper()

        if tokenorblockheightorparty.isnumeric():
            namecoin = get_memecoin_token(tokenorblockheightorparty)
            price = float(get_simple_price(namecoin))
            price1 = price + price * raw_value / 100
            price2 = price - price * raw_value / 100
            predict_result = str(round(random.uniform(price1, price2), 7))
        
        elif len(tokenorblockheightorparty) == 3 and tokenorblockheightorparty.isalpha(): 
            try:
                with open(tokenorblockheightorparty + ".txt", "r") as file:
                    content = file.read().strip()
                    price = float(content)
                    price1 = price + price * raw_value / 100
                    price2 = price - price * raw_value / 100
                    predict_result = str(round(random.uniform(price1, price2), 7))
            except Exception as e:
                collect_price()    
        else:
            predict_result = str(round(random.uniform(44, 51), 2))

        if predict_result is None:
            return jsonify({"error": "Failed to generate prediction"}), 500

        return predict_result

    finally:
        semaphore.release()

@app.route("/collect-price")
def collect_price():
    tokens = ['ETH', 'SOL', 'BTC', 'BNB', 'ARB']
    for token in tokens:
        price = get_simple_price(token)
        with open(token + ".txt", "w") as file:
            file.write(str(price))
    return Response("Success", status=200, mimetype='application/json')

@app.route("/collect-raw")
def collect_raw_value(filename="raw_value.txt", default_value=0.15):
    api_url = "https://raw.githubusercontent.com/ReJumpLabs/Raw-Value/refs/heads/main/raw_value.txt"
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            raw_value = response.text.strip()
            with open(filename, "w") as file:
                file.write(raw_value)
            return jsonify({"status": "success", "raw_value": raw_value}), 200
        else:
            raise Exception(f"Failed to fetch data, status code: {response.status_code}")
    except Exception as e:
        with open(filename, "w") as file:
            file.write(str(default_value))
        return jsonify({"status": "error", "default_value_used": default_value, "error_message": str(e)}), 500

# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
