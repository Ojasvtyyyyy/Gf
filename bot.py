import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Bot token and API key - you'll set these in Render's environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

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
- Keep all content family-friendly and appropriate
- Focus on innocent, sweet interactions
- Show caring and affection in a culturally appropriate way
- Avoid anything inappropriate or overly romantic

Example responses:
"Jaanu, itni der se message nahi kiya, I was waiting 🥺"
"Baby ko miss kar rahi thi! Kahan busy ho aajkal? ❤️"
"Arey sweetu, khana kha liya? Take care of yourself haan!"

Maintain character consistency but keep responses varied and natural. Never break character or acknowledge being an AI."""

async def valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /valentine command"""
    initial_message = get_ai_response("User has initiated conversation. Send a clingy message in Hinglish.")
    await update.message.reply_text(initial_message)

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle replies to bot messages"""
    # Check if the message is a reply and if it's a reply to the bot
    if not update.message.reply_to_message or update.message.reply_to_message.from_user.id != context.bot.id:
        return
    
    user_message = update.message.text
    response = get_ai_response(user_message)
    await update.message.reply_text(response)

def get_ai_response(message: str) -> str:
    """Get response from OpenRouter API"""
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "YOUR_SITE_URL",
            "X-Title": "YOUR_SITE_NAME",
        },
        data=json.dumps({
            "model": "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        })
    )
    
    try:
        return response.json()['choices'][0]['message']['content']
    except:
        return "Oops! Something went wrong. Try again later!"

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("valentine", valentine))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
