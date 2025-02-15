import os
from flask import Flask, request as flask_request
import requests
import json
import google.generativeai as genai

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
PORT = int(os.environ.get("PORT", 5000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Configure Google AI
genai.configure(api_key=GOOGLE_API_KEY)

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
- flirt alot
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
    """Get response from Gemini API"""
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create chat
        chat = model.start_chat(history=[])
        
        # Add system prompt
        chat.send_message(SYSTEM_PROMPT)
        
        # Get response
        response = chat.send_message(user_message)
        
        if response.text:
            return response.text
        else:
            print("Empty response from Gemini")
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
    update = flask_request.json
    print(f"Received update: {json.dumps(update, indent=2)}")
    
    if 'message' in update and 'text' in update['message']:
        chat_id = update['message']['chat']['id']
        user_message = update['message']['text']
        
        if user_message == '/start':
            send_telegram_message(chat_id, "Hello! I'm your clingy girlfriend bot 💕")
        elif user_message == '/valentine':
            send_telegram_message(chat_id, "Baby, tum kahan the? I was missing you so much! 🥺")
        else:
            ai_response = get_ai_response(user_message)
            print(f"AI response: {ai_response}")
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
    app.run(host='0.0.0.0', port=PORT)
