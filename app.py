from flask import Flask
import random

app = Flask(__name__)

# In-memory storage for tracking the previous inference (probability of win)
inference_history = {
    'republican_win_prob': 0.5  # Start at 50% chance
}

# Endpoint to generate a daily inference
@app.route("/daily_inference")
def daily_inference():
    try:
        # Simulate a random fluctuation in the probability (within +/- 5%)
        fluctuation = random.uniform(-0.05, 0.05)
        today_prob = round(inference_history['republican_win_prob'] + fluctuation, 4)

        # Keep probability within [0, 1] range
        today_prob = max(0, min(1, today_prob))

        # Update the inference history with today's value
        inference_history['republican_win_prob'] = today_prob

        # Return only the inference result as a float number
        return str(today_prob)

    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8800, debug=True)
