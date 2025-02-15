import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# API Endpoint
API_URL = "https://bhagavadgita.io/api/v1/verses/random"
API_HEADERS = {"Authorization": "Bearer YOUR_API_KEY"}  # Replace with your API key if needed

def get_random_shloka():
    """Fetch a random Bhagavad Gita shloka and explanation."""
    try:
        response = requests.get(API_URL, headers=API_HEADERS)
        if response.status_code == 200:
            data = response.json()
            verse = data["text"]
            translation = data["translations"][0]["description"]
            chapter = data["chapter"]["chapter_number"]
            verse_number = data["verse_number"]
            
            return f"📖 *Bhagavad Gita* (Chapter {chapter}, Verse {verse_number})\n\n" \
                   f"🔹 *Shloka:* \n_{verse}_\n\n" \
                   f"💡 *Meaning:* \n_{translation}_"
        else:
            return "⚠️ Unable to fetch the shloka. Try again later."
    except Exception as e:
        return f"Error: {e}"

def send_shloka(update: Update, context: CallbackContext) -> None:
    """Handles the /shlok command."""
    message = get_random_shloka()
    update.message.reply_text(message, parse_mode="Markdown")

def main():
    """Start the Telegram bot."""
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)  # Replace with your bot token
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("shlok", send_shloka))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
