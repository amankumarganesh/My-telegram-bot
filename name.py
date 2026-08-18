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
# 1. FLASK WEB SERVER (Keep-Alive for Render Web Service)
# ============================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is online and active!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ============================================================
# 2. BOT CONFIGURATION
# ============================================================
# Environment variable se lega ya seedhe yahan quote me daal sakte hain
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Agar Render Environment me nahi dala hai to niche apna token likhein:
# BOT_TOKEN = "APNA_BOT_TOKEN_YAHAN_DAALEIN"

# ============================================================
# 3. TEXT SANITIZER (Render Safe)
# ============================================================
def clean_safe_text(text):
    if not text:
        return ""
    # Safe text sanitization without non-printable corrupt bytes
    clean_chars = [c for c in str(text) if (32 <= ord(c) <= 126) or (128 <= ord(c) <= 65535) or c == '\n']
    return "".join(clean_chars).strip()

# ============================================================
# 4. BOT RESPONSE LOGIC
# ============================================================
def generate_response(user_raw_text):
    text = clean_safe_text(user_raw_text).lower()

    # Check 1: Greetings / Casual words
    if any(k in text for k in ["hi", "hello", "hey", "hii", "namaste", "haan", "ha", "krishna", "jai", "radhe", "ram", "bhai"]):
        return (
            "Namaste! Welcome to Trading Assistant Bot.\n\n"
            "Aap mujhse niche diye gaye kisi bhi topic par pooch sakte hain:\n"
            "- Color (Color Trading Rules)\n"
            "- Uchhal (Market Up Trend)\n"
            "- Giravat (Market Down Trend)\n"
            "- Hot Number (Repeating numbers)\n"
            "- Next Color (Prediction rule)\n"
            "- Stock Market / RSI / MACD / Moving Average\n"
            "- Panel (User ID & Dashboard Help)"
        )

    # Check 2: Color Trading Rules
    elif any(k in text for k in ["color", "colour", "rang", "kitne", "green", "red", "violet", "laal", "hara", "baingani"]):
        return (
            "Color Trading Rules:\n\n"
            "1. Green (Hara):\n"
            "- Numbers: 1, 3, 7, 9 (Odd Numbers)\n"
            "- Signal: High / Bullish Movement\n\n"
            "2. Red (Laal):\n"
            "- Numbers: 2, 4, 6, 8 (Even Numbers)\n"
            "- Signal: Low / Bearish Movement\n\n"
            "3. Violet (Baingani - Special):\n"
            "- Numbers: 0 aur 5\n"
            "- Rule: 0 aane par Red+Violet, 5 aane par Green+Violet milta hai."
        )

    # Check 3: Market Uchhal (Up Trend)
    elif any(k in text for k in ["uchhal", "up", "bullish", "high", "badhat"]):
        return (
            "Market Uchhal (Up Trend) Guide:\n\n"
            "- Uchhal kab hota hai: Jab lagatar Green color aur high numbers (7, 8, 9) repeat hote hain.\n"
            "- Pattern: 3 ya usse jyada baar Green aana continuous up-trend darshata hai.\n"
            "- Strategy: Uchhal ke time trend ke sath chalein, jaldbazi me opposite bet na lagayein."
        )

    # Check 4: Market Giravat (Down Trend)
    elif any(k in text for k in ["giravat", "down", "bearish", "low", "loss"]):
        return (
            "Market Giravat (Down Trend) Guide:\n\n"
            "- Giravat kab hoti hai: Jab lagatar Red color aur low numbers (1, 2, 3, 4) aate hain.\n"
            "- Pattern: Lagatar Red aane par market down-trend me hota hai.\n"
            "- Strategy: Giravat ke dauran break point ka intezar karein."
        )

    # Check 5: Next Color / Prediction Check
    elif any(k in text for k in ["kya aayega", "next", "aage", "aayega", "predict", "konsa"]):
        return (
            "Next Color Guide:\n\n"
            "1. Trend Check: Pichle rounds ka chart dekhein (Dragon trend hai ya AB-AB pattern).\n"
            "2. AB Pattern: Red -> Green -> Red -> Green chal raha ho to alternate color follow karein.\n"
            "3. Hot Numbers: Jo number regular repeat ho raha hai, us color ki sambhavna jyada hoti hai."
        )

    # Check 6: Hot Numbers
    elif any(k in text for k in ["hot", "number", "repeat", "cold", "ank"]):
        return (
            "Hot Numbers Information:\n\n"
            "- Hot Numbers: Jo pichle 10-20 rounds me sabse jyada baar draw hote hain.\n"
            "- Cold Numbers: Jo kaafi lambe time se draw nahi huye hain.\n"
            "- Tip: Chart me repeat numbers dekh kar entry lena safe hota hai."
        )

    # Check 7: Panel / User / Login / Account Help
    elif any(k in text for k in ["panel", "user", "id", "login", "account", "balance", "deposit", "withdraw"]):
        return (
            "Panel User Support:\n\n"
            "- Dashboard: Apna User ID aur balance panel dashboard se verify karein.\n"
            "- Deposit / Withdraw: Hamesha official payment links ka hi upyog karein.\n"
            "- Issue: Kisi bhi error ke liye panel support ticket generate karein."
        )

    # Check 8: Stock Market
    elif any(k in text for k in ["stock market", "share market", "stocks", "shares", "stock"]):
        return (
            "Stock Market Guide:\n\n"
            "Stock market ek aisa platform hai jahan publicly listed companies ke shares trade hote hain.\n"
            "Important Tools: Price Action, Support/Resistance, Volume aur Indicators."
        )

    # Check 9: RSI
    elif "rsi" in text:
        return (
            "RSI (Relative Strength Index):\n\n"
            "RSI ek momentum indicator hai (0-100 scale):\n"
            "- Above 70: Potentially Overbought (Giravat aa sakti hai)\n"
            "- Below 30: Potentially Oversold (Uchhal aa sakta hai)"
        )

    # Check 10: Moving Average
    elif "moving average" in text or text == "ma":
        return (
            "Moving Average (MA):\n\n"
            "- SMA (Simple Moving Average)\n"
            "- EMA (Exponential Moving Average)\n"
            "Traders trend aur price direction janne ke liye iska use karte hain."
        )

    # Check 11: MACD
    elif "macd" in text:
        return (
            "MACD (Moving Average Convergence Divergence):\n\n"
            "Yeh do moving averages ke bich ka relationship dikhakar trend reversal aur momentum batata hai."
        )

    # Fallback: Agar banda kuchh bhi ulta-seedha/manual type kare to instant reply
    else:
        return (
            "Aapka message mila! Kripya niche diye gaye kisi topic par type karein:\n\n"
            "1. Color (Rules & Colors)\n"
            "2. Uchhal (Market Up Movement)\n"
            "3. Giravat (Market Down Movement)\n"
            "4. Hot Number (Repeating Numbers)\n"
            "5. Next Color (Prediction Pattern)\n"
            "6. Panel (User ID & Balance)\n"
            "7. RSI / MACD / Stock Market"
        )

# ============================================================
# 5. TELEGRAM EVENT HANDLERS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome! Main aapka Trading Assistant Bot hoon.\n\n"
        "Aap mujhse puch sakte hain:\n"
        "- Color Trading Rules\n"
        "- Market Uchhal aur Giravat\n"
        "- Hot Numbers\n"
        "- Panel aur User Help\n"
        "- Stock Market & Technical Indicators (RSI, MACD)\n\n"
        "Kisi bhi sawal ke liye seedhe type karein!"
    )
    await update.message.reply_text(welcome_text)

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_text = update.message.text
    bot_reply = generate_response(user_text)
    await update.message.reply_text(bot_reply)

# ============================================================
# 6. MAIN EXECUTION
# ============================================================
def main():
    token = BOT_TOKEN or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("ERROR: BOT_TOKEN set nahi hai! Code me token dalein.")
        return

    # Start Flask Web Server
    keep_alive()

    # Build Application
    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

    print("Bot bina kisi conflict ke chalu ho gaya hai...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
