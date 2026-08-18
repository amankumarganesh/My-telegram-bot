import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============================================================
# FLASK SERVER (Keep-Alive for Render)
# ============================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ============================================================
# CONFIGURATION
# ============================================================
# Render Environment Variables se Token uthayega
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Agar Render ke Environment tab me add nahi kiya to yahan direct quotes me dal sakte hain
# BOT_TOKEN = "Aapka_Telegram_Bot_Token_Yahan"

# ============================================================
# START COMMAND
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "👋 Welcome!\n\n"
        "I am your Trading Information Bot.\n\n"
        "You can ask me about:\n"
        "📈 Stock market\n"
        "🎨 Color trading\n"
        "📊 Trading indicators\n"
        "📚 Basic trading concepts\n\n"
        "Examples:\n"
        "• What is the stock market?\n"
        "• What is RSI?\n"
        "• Explain moving average\n"
        "• What is color trading?\n\n"
        "⚠️ Trading involves risk. Information from this bot "
        "is not guaranteed financial advice."
    )
    await update.message.reply_text(message)

# ============================================================
# MESSAGE HANDLER
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip().lower()

    # Greetings
    greetings = [
        "hi", "hello", "hey", "hii", "hiii",
        "namaste", "good morning", "good afternoon", "good evening"
    ]
    if text in greetings:
        await update.message.reply_text(
            "👋 Hello! Welcome to the Trading Information Bot.\n\n"
            "📈 Ask me about stock-market concepts or trading indicators.\n"
            "🎨 You can also ask about color trading.\n\n"
            "How can I help you?"
        )
        return

    # Stock market
    if any(word in text for word in ["stock market", "share market", "stocks", "shares", "stock"]):
        await update.message.reply_text(
            "📈 STOCK MARKET\n\n"
            "The stock market is where shares of publicly listed companies are bought and sold.\n\n"
            "Important concepts include:\n"
            "• Price action\n"
            "• Volume\n"
            "• Support and resistance\n"
            "• Moving averages\n"
            "• RSI\n"
            "• MACD\n"
            "• Risk management\n\n"
            "⚠️ No indicator can guarantee whether a stock will rise or fall."
        )
        return

    # RSI
    if "rsi" in text:
        await update.message.reply_text(
            "📊 RSI (Relative Strength Index)\n\n"
            "RSI is a momentum indicator commonly measured on a 0–100 scale.\n\n"
            "Traditionally:\n"
            "• Above 70 → potentially overbought\n"
            "• Below 30 → potentially oversold\n\n"
            "These levels are not guaranteed buy/sell signals. "
            "RSI should be considered together with other market information."
        )
        return

    # Moving Average
    if "moving average" in text or text == "ma":
        await update.message.reply_text(
            "📈 MOVING AVERAGE\n\n"
            "A moving average smooths price data over a selected period.\n\n"
            "Common examples:\n"
            "• SMA — Simple Moving Average\n"
            "• EMA — Exponential Moving Average\n\n"
            "Traders often use moving averages to study trends and price momentum."
        )
        return

    # MACD
    if "macd" in text:
        await update.message.reply_text(
            "📊 MACD (Moving Average Convergence Divergence)\n\n"
            "MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price."
        )
        return

# ============================================================
# MAIN FUNCTION
# ============================================================
def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set. Please set your bot token.")

    # Start Flask Web Server
    keep_alive()

    # Start Telegram Bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
