import os
from flask import Flask, request as flask_request
import requests
import json

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
PORT = int(os.environ.get("PORT", 5000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# System prompt for the AI
SYSTEM_PROMPT = """ai assistant"""

def get_ai_response(user_message):
    """Get response from OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-3-opus:beta",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        else:
            return "Hmm, kuch problem hai... Can you message me later? 🥺"
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "Arey baby, something went wrong. Try again? ❤️"

def send_telegram_message(chat_id, text):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=data)
    print(f"Telegram API response: {response.text}")
    return response

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook_handler():
    """Handle incoming webhook updates from Telegram."""
    # Get the update from Telegram
    update = flask_request.json
    print(f"Received update: {json.dumps(update, indent=2)}")
    
    # Check if this is a message with text
    if 'message' in update and 'text' in update['message']:
        chat_id = update['message']['chat']['id']
        user_message = update['message']['text']
        
        # Handle commands
        if user_message == '/start':
            send_telegram_message(chat_id, "Hello! I'm your clingy girlfriend bot 💕")
        elif user_message == '/valentine':
            send_telegram_message(chat_id, "Baby, tum kahan the? I was missing you so much! 🥺")
        else:
            # Get AI response
            ai_response = get_ai_response(user_message)
            print(f"AI response: {ai_response}")
            
            # Send response back to user
            send_telegram_message(chat_id, ai_response)
    
    return "OK"

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/set_webhook')
def set_webhook():
    """Set the webhook for Telegram."""
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    return f"Webhook set to {webhook_url}. Response: {response.text}"

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=PORT)
