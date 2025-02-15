import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Initialize Flask app
app = Flask(__name__)

# Get Telegram bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Bhagavad Gita API Base URL
API_BASE_URL = "https://bhagavadgita.io/api/v2"

# Initialize bot application
bot_app = Application.builder().token(TOKEN).build()

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
async def shlok(update: Update, context: CallbackContext):
    """Handles the /shlok command."""
    message = get_random_shloka()
    await update.message.reply_text(message, parse_mode="Markdown")

# Add command handler to bot application
bot_app.add_handler(CommandHandler("shlok", shlok))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates via webhook."""
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK", 200

@app.route("/")
def home():
    return "🚀 Telegram Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
