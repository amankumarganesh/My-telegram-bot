
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
import sys

# ==========================================
# 1. SYSTEM PROMPT (Clean ASCII Hinglish)
# ==========================================
SYSTEM_PROMPT = """
Trading Assistant Bot Knowledge:
1. Color Rules:
   - Green (Odd numbers): 1, 3, 7, 9
   - Red (Even numbers): 2, 4, 6, 8
   - Violet (Special): 0 (Red+Violet) aur 5 (Green+Violet)
2. Numbers:
   - Hot Numbers: Jo pichle rounds me sabse jyada repeat hote hain.
   - Cold Numbers: Jo kafi time se nahi aaye hain.
3. Market Movements:
   - Uchhal (Up/Bullish): Lagatar Green ya high-value pattern.
   - Giravat (Down/Bearish): Lagatar Red ya low-value pattern.
4. User Fallback:
   - Agar naya user galat ya typo input kare to turant help menu bhejein.
"""

# ==========================================
# 2. STRICT PRINTABLE ASCII SANITIZER
# ==========================================
def clean_printable_text(text):
    """
    Kewal standard printable ASCII characters (range 32-126) aur newline ko allow karta hai.
    Koi bhi hidden character, corrupt bytes ya non-printable character remove ho jayega.
    """
    if not text:
        return ""
    clean_chars = [c for c in str(text) if (32 <= ord(c) <= 126) or c == '\n']
    return "".join(clean_chars).strip()

# ==========================================
# 3. MAIN TRADING BOT HANDLER
# ==========================================
def get_bot_response(user_input):
    safe_text = clean_printable_text(user_input).lower()
    
    # 1. Color Trading Rules
    if any(w in safe_text for w in ["color", "colour", "rang", "green", "red", "violet", "laal", "hara"]):
        return (
            "Color Trading Rules:\n"
            "- Green (Hara): Numbers 1, 3, 7, 9 (Odd)\n"
            "- Red (Laal): Numbers 2, 4, 6, 8 (Even)\n"
            "- Violet: Special Numbers 0 (Red+Violet) aur 5 (Green+Violet)"
        )
    
    # 2. Hot / Cold Numbers
    elif any(w in safe_text for w in ["hot", "number", "repeat", "cold"]):
        return (
            "Hot Numbers Information:\n"
            "- Hot Numbers: Woh numbers jo pichle 10 se 20 rounds me sabse jyada baar aaye hain.\n"
            "- Cold Numbers: Woh numbers jo kaafi rounds se draw nahi huye hain."
        )
    
    # 3. Giravat ya Uchhal (Market Trend)
    elif any(w in safe_text for w in ["giravat", "uchhal", "trend", "up", "down", "market"]):
        return (
            "Market Trend Guide:\n"
            "- Uchhal (Up Trend): Lagatar Green color aur high numbers ka aana.\n"
            "- Giravat (Down Trend): Lagatar Red color aur low numbers ka aana.\n"
            "- Strategy: Trend ke direction me hi decision lein."
        )
    
    # 4. Panel / User Help
    elif any(w in safe_text for w in ["panel", "user", "id", "login", "account"]):
        return (
            "Panel User Help:\n"
            "- Apna User ID aur balance panel dashboard par check karein.\n"
            "- Galat balance ya login issue ke liye support panel par connect karein."
        )
    
    # 5. Default Fallback (New user ya Galat/Typo input ke liye instant reply)
    else:
        return (
            "Namaste! Lagta hai aapne galat option type kiya hai.\n\n"
            "Aap inme se koi ek word likhkar bhej sakte hain:\n"
            "1. Color (Red, Green, Violet rules)\n"
            "2. Hot Number (Repeat hone wale numbers)\n"
            "3. Trend (Giravat ya Uchhal guide)\n"
            "4. Panel (User dashboard help)"
        )

# ==========================================
# 4. RUN & TEST
# ==========================================
if __name__ == "__main__":
    test_queries = [
        "red color rules kya hai",
        "hot number btao",
        "market me giravat hai ya uchhal",
        "panel user id problem",
        "kuchhbhi_galat_type123"  # Typo test
    ]
    
    for q in test_queries:
        print("User:", q)
        print("Bot Response:")
        print(get_bot_response(q))
        print("-" * 50)
