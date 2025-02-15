import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your clingy girlfriend bot 💕")

async def valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Baby, tum kahan the? I was missing you so much! 🥺")

def run_bot():
    print("Starting bot...")
    # Create new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("valentine", valentine))
    
    print("Bot is running...")
    # Run the bot in the event loop
    loop.run_until_complete(application.run_polling(allowed_updates=Update.ALL_TYPES))

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    run_flask()
