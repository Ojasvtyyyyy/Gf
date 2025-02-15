import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Initialize Flask app
app = Flask(__name__)

# Get Telegram bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT = Bot(TOKEN)

# Bhagavad Gita API Base URL
API_BASE_URL = "https://bhagavadgita.io/api/v2"

# Initialize dispatcher
dispatcher = Dispatcher(BOT, None, use_context=True)

# Function to fetch a random shloka
def get_random_shloka():
    """Fetch a random Bhagavad Gita shloka and explanation."""
    import random
    chapter_number = random.randint(1, 18)
    verse_number = random.randint(1, 75)

    response = requests.get(f"{API_BASE_URL}/chapters/{chapter_number}/verses/{verse_number}/")
    
    if response.status_code == 200:
        data = response.json()
        shloka_text = data.get("text", "No verse found.")
        translation = data.get("translations", [{}])[0].get("description", "No translation available.")

        return f"📖 *Bhagavad Gita* (Chapter {chapter_number}, Verse {verse_number})\n\n" \
               f"🔹 *Shloka:* \n_{shloka_text}_\n\n" \
               f"💡 *Meaning:* \n_{translation}_"
    return "⚠️ Unable to fetch the shloka. Try again later."

# Command handler for /shlok
def shlok(update: Update, context: CallbackContext) -> None:
    """Handles the /shlok command."""
    message = get_random_shloka()
    update.message.reply_text(message, parse_mode="Markdown")

# Add command handler to dispatcher
dispatcher.add_handler(CommandHandler("shlok", shlok))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates via webhook."""
    update = Update.de_json(request.get_json(), BOT)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "🚀 Telegram Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
