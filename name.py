import os
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Flask Server (Render port binding keep-alive) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is live and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- Bot Command & Message Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Arre bhai! Swagat hai tere bhai ke bot me! 😎\n\n"
        "Yahan sab milega:\n"
        "• 🎨 **Color Game Prediction:** Likho 'color prediction' ya 'red ya green'\n"
        "• 🔢 **Number Guess:** Likho 'number batao'\n"
        "• 📈 **Market Trend:** Likho 'market trend'\n"
        "• 💰 **Mutual Fund Knowledge:** Likho 'mutual fund'\n\n"
        "Kuch bhi puch, dosti yaari me sab clear bataunga!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()

    # 1. Color Prediction
    if any(k in text for k in ["color", "colour", "red", "green", "violet"]):
        colors = ["🔴 RED", "🟢 GREEN", "🟣 VIOLET"]
        chosen_color = random.choice(colors)
        confidence = random.randint(70, 95)
        reply = (
            f"Bhai intuition keh raha hai is baar **{chosen_color}** aane ke chances hain! "
            f"({confidence}% feeling) 🎯\n\n"
            "_Note: Ye sirf entertainment ke liye fun guess hai bhai, risk apne dam par lena!_"
        )

    # 2. Number Prediction
    elif any(k in text for k in ["number", "no bata", "digit"]):
        lucky_num = random.randint(0, 9)
        reply = (
            f"Number chahiye? Mere hisab se **{lucky_num}** par nazar rakh! 🎲\n"
            "_Sirf fun prediction hai dost!_"
        )

    # 3. Market / Trading Trend (Uthaal ya Girawat)
    elif any(k in text for k in ["trade", "trading", "uthaal", "girawat", "up ya down", "market"]):
        trend = random.choice(["🚀 Bada Uthaal (Bullish/Up)", "📉 Girawat (Bearish/Down)"])
        reply = (
            f"Bhai market reading ke hisaab se agla move **{trend}** lag raha hai! 📊\n\n"
            "Stop-loss laga kar hi trade karna dost, safe rehna!"
        )

    # 4. Mutual Fund Complete Detail
    elif any(k in text for k in ["mutual fund", "mf", "sip", "investment"]):
        reply = (
            "💰 **Mutual Fund Ka Pura Funda (Dostana Style):**\n\n"
            "1. **Equity Funds:** Paisa Share Market me lagta hai. High return + High risk (Long term ke liye best).\n"
            "2. **Debt Funds:** Government bonds aur safe instruments me paisa lagta hai. Low risk + Fixed return.\n"
            "3. **Hybrid Funds:** Equity + Debt dono ka mixture. Medium risk, balanced return.\n"
            "4. **Index Funds:** Nifty 50 ya Sensex ko copy karte hain. Low expense ratio.\n"
            "5. **ELSS:** Tax saving mutual fund (Section 80C ke under tax bachta hai, 3 saal lock-in).\n\n"
            "💡 **Best Advice:** Direct lamba paisa dalne se behtar hai har mahine **SIP (Systematic Investment Plan)** karo!"
        )

    # 5. Casual Chit-Chat & Yes/No Responses
    elif any(k in text for k in ["yes", "ha", "haa", "deal", "sahi hai", "done"]):
        reply = "Full support hai bhai! Deal pakki samjho 🤝 Aur bata kya seva karun?"

    elif any(k in text for k in ["hi", "hello", "hey", "bhai", "kaisa hai"]):
        reply = "Ekdum badhiya mere bhai! Tu bata sab theek-thaak? Kya janana chahta hai aaj?"

    else:
        reply = (
            "Arre bhai sab samajh raha hoon! 😉\n"
            "Color trading, number prediction, market trend ya Mutual Fund — jo puchna hai khul ke bol!"
        )

    await update.message.reply_text(reply, parse_mode="Markdown")

# --- Main Runner ---
if __name__ == "__main__":
    # Render web service ke liye Flask ko background thread me chalayein
    threading.Thread(target=run_flask, daemon=True).start()

    # Telegram Bot Token (Render Environment Variables me set karein)
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not BOT_TOKEN:
        raise ValueError("Error: TELEGRAM_BOT_TOKEN environment variable set nahi hai!")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot start ho gaya hai...")
    application.run_polling()
