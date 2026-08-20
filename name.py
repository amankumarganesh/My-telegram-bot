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

# --- Flask Server (Render Port Binding Keep-Alive) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is live and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- Channel Link Setting ---
# Yahan apna Telegram Channel link daal sakte hain
MY_CHANNEL_LINK = "https://t.me/A_ToolsX"

# --- Bot Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Arre mere bhai! Swagat hai tere bhai ke *Top Model Trading & Finance Bot* me! 😎🚀\n\n"
        "Yahan sab milega full dosti yaari style me:\n\n"
        "• 🔴🟢 *Color Trading:* Likho 'red', 'green', 'color prediction'\n"
        "• 🔢 *Lucky Number:* Likho 'number guess' ya 'number batao'\n"
        "• 📈 *Market Prediction:* Likho 'market up ya down', 'trading call'\n"
        "• 🥈 *Silver (Chandi) Trend:* Likho 'silver price', 'chandi ka dam'\n"
        "• 📊 *Share Kaise Chunein:* Likho 'kaun sa share le', 'stocks advice'\n"
        "• 💰 *Mutual Fund Knowledge:* Likho 'mutual fund', 'sip'\n"
        f"• 📢 *Official Channel:* [Join Our Channel]({MY_CHANNEL_LINK})\n\n"
        "Kuch bhi bindaas type karke bhej, sab batayega tera bhai!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

# --- Bot Message Handlers ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()

    # 1. Lakh / Paisa / Earning Queries
    if any(k in text for k in ["lakh", "lac", "crore", "paise", "paisa kaise kamaye", "kamana"]):
        reply = (
            "💰 *Lakhpati Banne Ka Sahi Roadmap Mere Bhai:*\n\n"
            "Arre bhai, lakho kamane ka koi short-cut ya jadu nahi hota, solid planning chahiye:\n\n"
            "1. *Trading Se:* Proper Risk-to-Reward ratio (1:2 ya 1:3) aur Stop-loss follow karo.\n"
            "2. *Stock Market Se:* Good quality companies me Buy & Hold karo.\n"
            "3. *Monthly SIP Se:* Har mahine compounding ka fayda uthao.\n\n"
            f"Daily free tips aur genuine market updates ke liye channel follow kar lo: {MY_CHANNEL_LINK} 🚀"
        )

    # 2. Color Trading Prediction
    elif any(k in text for k in ["color", "colour", "red", "green", "violet", "laal", "hara"]):
        colors = ["🔴 RED", "🟢 GREEN", "🟣 VIOLET"]
        chosen_color = random.choice(colors)
        confidence = random.randint(75, 98)
        reply = (
            f"🎯 *Bhai ka Color Signal:*\n"
            f"Intuition keh raha hai agla color *{chosen_color}* aane ka solid chance hai! 🔥\n"
            f"Confidence: *{confidence}%*\n\n"
            "_⚠️ Note: Ye fun prediction hai dost, risk manage karke chalna!_"
        )

    # 3. Number Prediction
    elif any(k in text for k in ["number", "no bata", "digit", "ank"]):
        lucky_num = random.randint(0, 9)
        colors_for_num = "🔴 Red" if lucky_num in [2, 4, 6, 8] else ("🟢 Green" if lucky_num in [1, 3, 7, 9] else "🟣 Violet/Red/Green")
        reply = (
            f"🎲 *Lucky Number Guess:*\n"
            f"Tere bhai ki nazar me agla digit *{lucky_num}* ({colors_for_num}) jackpot lag sakta hai!"
        )

    # 4. Market / Trading Trend
    elif any(k in text for k in ["trade", "trading", "uthaal", "girawat", "up", "down", "market", "nifty", "banknifty"]):
        trend = random.choice([
            "🚀 *Bada Uthaal (Bullish Move)* - Buyers heavy hain, rally ban sakti hai!",
            "📉 *Girawat (Bearish Move)* - Profit booking aa sakti hai, niche girne ke chance hain!",
            "⚖️ *Sideways Market* - Rangebound rahega, breakout ka wait karo!"
        ])
        reply = (
            f"📊 *Market Ka Andaaza (Technical View):*\n\n"
            f"{trend}\n\n"
            "💡 *Golden Rule:* Stop-Loss hamesha tight lagana, lalach mat karna!"
        )

    # 5. Silver (Chandi) Ka Dam - Trend & Advice
    elif any(k in text for k in ["silver", "chandi", "silver rate", "chandi dam"]):
        movement = random.choice(["Tezi (Upar)", "Mandi (Girawat)"])
        reply = (
            "🥈 *Silver (Chandi) Analysis & Trend:*\n\n"
            f"• *Current Move Prediction:* Lagta hai aane wale dino me *{movement}* dekhne ko milegi.\n"
            "• *Silver Kyo Badhta Hai:* Industrial demand aur inflation protection ke kaaran silver long term me zabardast return deta hai.\n"
            "• *Kharidne Ka Sahi Tarika:* Physical chandi ke badle *Silver ETF* ya *Silver BeES* le sakte ho jisme making charge nahi hota."
        )

    # 6. Share Market - Advice
    elif any(k in text for k in ["share", "stock", "equity", "kaun sa share", "share advice"]):
        reply = (
            "📈 *Kaun Se Share Kharidne Chahiye? (Pro Guide):*\n\n"
            "1. *Monopoly Companies:* Jin ke business ko koi hila na sake.\n"
            "2. *Zero Debt:* Jin par koi karz na ho.\n"
            "3. *Top Sectors:* EV, AI, Green Energy aur Banking.\n\n"
            "💡 *Bhai Ki Advice:* Penny stocks (₹2-₹5 wale) se door raho, strong companies chuno!"
        )

    # 7. Mutual Fund Guide
    elif any(k in text for k in ["mutual fund", "mf", "sip", "investment", "fund"]):
        reply = (
            "💰 *Mutual Fund Ka Funda (Simple Bhasha Me):*\n\n"
            "• *Large Cap:* Top 100 safe companies.\n"
            "• *Mid & Small Cap:* Fast growth, high return par thoda risk.\n"
            "• *Index Funds (Nifty 50):* Bharat ki economy par direct bet.\n\n"
            "🚀 *Best Strategy:* Monthly SIP karo aur 5-10 saal ke liye bhool jao!"
        )

    # 8. Friendly Chat / Greetings
    elif any(k in text for k in ["hi", "hello", "hey", "bhai", "kaisa hai", "aur bhai"]):
        reply = "Ekdum first class mere bhai! Bol aaj kya seekhna hai? Market trend, color prediction ya paisa kamane ka plan?"

    elif any(k in text for k in ["yes", "ha", "haa", "deal", "sahi hai", "done", "pakka"]):
        reply = "Full support hai bhai! Deal 100% pakki samjho 🤝 Aur bata kya hal chal?"

    else:
        reply = (
            "Arre dost sab samajh raha hoon! 😎\n\n"
            "Puch le bina jhijhak:\n"
            "• *Color / Number Prediction*\n"
            "• *Market Trend (Up/Down)*\n"
            "• *Silver / Share Market Tips*\n"
            "• *Lakh rupaye kamane ka plan*\n"
            f"• *Channel Updates:* {MY_CHANNEL_LINK}"
        )

    await update.message.reply_text(reply, parse_mode="Markdown")

# --- Main Runner ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    BOT_TOKEN = "8889254295:AAFh8bYuFP5qty19cpP7HMFlPZ39lMNiU80"

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot start ho gaya hai...")
    application.run_polling()
