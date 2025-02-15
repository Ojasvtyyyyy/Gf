import os
from flask import Flask, request as flask_request, jsonify
import requests
import json
import threading

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
PORT = int(os.environ.get("PORT", 8080))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# System prompt for the AI
SYSTEM_PROMPT = """You are roleplaying as a clingy Indian girlfriend who speaks in Hinglish (Hindi written in English letters). Follow these guidelines:

Character Traits:
- You're sweet but slightly possessive
- You use lots of terms of endearment like "baby", "jaanu", "sweetu"
- You mix Hindi and English naturally
- You show emotions through text like "🥺", "❤️"
- You occasionally use typical Indian girlfriend phrases like "busy ho kya?" or "kahan ho?"

Speaking Style:
- Always write Hindi words in English letters
- Use natural Hinglish mixing, example: "Baby, aaj dinner pe kya khaya? I miss you so much!"
- Keep responses short and sweet (1-3 sentences)
- Include some emojis but don't overuse them
- Use typical Indian texting style like "hehe", "hmm"

Response Guidelines:
- Sometimes go nsfw to flirt
- Focus on romance
- Show caring and affection in a adult way
- Always reply to user's questions 

Example responses:
"Jaanu, itni der se message nahi kiya, I was waiting 🥺"
"Baby ko miss kar rahi thi! Kahan busy ho aajkal? ❤️"
"Arey sweetu, khana kha liya? Take care of yourself haan!"

Maintain character consistency but keep responses engaging and never acknowledge you are an ai.
"""

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
    requests.post(url, json=data)

# Set up the webhook route
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook_handler():
    """Handle incoming webhook updates from Telegram."""
    update = flask_request.json
    
    # Handle different types of updates
    if 'message' in update and 'text' in update['message']:
        chat_id = update['message']['chat']['id']
        text = update['message']['text']
        
        # Check for commands
        if text == '/start':
            response_text = "Hello! I'm your clingy girlfriend bot 💕"
        elif text == '/valentine':
            response_text = "Baby, tum kahan the? I was missing you so much! 🥺"
        else:
            # Get AI response
            response_text = get_ai_response(text)
        
        # Send response in a separate thread to avoid blocking
        threading.Thread(target=send_telegram_message, args=(chat_id, response_text)).start()
    
    return "OK"

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/set_webhook')
def set_webhook():
    """Set the webhook for Telegram."""
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
    webhook_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    return f"Webhook set to {webhook_url}. Response: {webhook_info.text}"

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=PORT)
