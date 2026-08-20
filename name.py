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
        "• 💰 *Mutual Fund Knowledge:* Likho 'mutual fund', 'sip'\n\n"
        "Kuch bhi bindaas type karke bhej, sab batayega tera bhai!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# --- Bot Message Handlers ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()

    # 1. Color Trading Prediction
    if any(k in text for k in ["color", "colour", "red", "green", "violet", "laal", "hara"]):
        colors = ["🔴 RED", "🟢 GREEN", "🟣 VIOLET"]
        chosen_color = random.choice(colors)
        confidence = random.randint(75, 98)
        reply = (
            f"🎯 *Bhai ka Color Signal:*\n"
            f"Intuition keh raha hai agla color *{chosen_color}* aane ka solid chance hai! 🔥\n"
            f"Confidence: *{confidence}%*\n\n"
            "_⚠️ Note: Ye fun prediction hai dost, risk manage karke chalna!_"
        )

    # 2. Number Prediction
    elif any(k in text for k in ["number", "no bata", "digit", "ank"]):
        lucky_num = random.randint(0, 9)
        colors_for_num = "🔴 Red" if lucky_num in [2, 4, 6, 8] else ("🟢 Green" if lucky_num in [1, 3, 7, 9] else "🟣 Violet/Red/Green")
        reply = (
            f"🎲 *Lucky Number Guess:*\n"
            f"Tere bhai ki nazar me agla digit *{lucky_num}* ({colors_for_num}) jackpot lag sakta hai!"
        )

    # 3. Market / Trading Trend (Uthaal ya Girawat)
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

    # 4. Silver (Chandi) Ka Dam - Trend & Advice
    elif any(k in text for k in ["silver", "chandi", "silver rate", "chandi dam"]):
        movement = random.choice(["Tezi (Upar)", "Mandi (Girawat)"])
        reply = (
            "🥈 *Silver (Chandi) Analysis & Trend:*\n\n"
            f"• *Current Move Prediction:* Lagta hai aane wale dino me *{movement}* dekhne ko milegi.\n"
            "• *Silver Kyo Badhta Hai:* Industrial demand (Solar panels, EVs, electronics) aur inflation protection ke kaaran silver long term me zabardast return deta hai.\n"
            "• *Kharidne Ka Sahi Tarika:* Physical chandi ke badle *Silver ETF* ya *Silver BeES* le sakte ho jisme making charge aur purity ki tension nahi hoti."
        )

    # 5. Share Market - Kis Type Ke Share Kharidein
    elif any(k in text for k in ["share", "stock", "equity", "kaun sa share", "share advice"]):
        reply = (
            "📈 *Kaun Se Share Kharidne Chahiye? (Pro Guide):*\n\n"
            "1. *Monopoly / Moat Companies:* Jin ke business ko replace karna mushkil ho (e.g., FMCG giants, Tech leaders, Railways).\n"
            "2. *Zero Debt (Karz-Mukt):* Jin companies par koi karz na ho aur cash flow strong ho.\n"
            "3. *Future Growth Sectors:*\n"
            "   • Green Energy & EV Ecosystem\n"
            "   • Artificial Intelligence & IT Services\n"
            "   • Banking & Defense Sector\n\n"
            "💡 *Bhai Ki Advice:* Penny stocks (₹2-₹5 wale share) se door raho. Blue-chip ya Large-cap shares me 'Buy on Dips' karo!"
        )

    # 6. Mutual Fund Complete Masterclass
    elif any(k in text for k in ["mutual fund", "mf", "sip", "investment", "fund"]):
        reply = (
            "💰 *Mutual Fund Ka Pura Bhandar (Zero Se Hero Guide):*\n\n"
            "• *1. Large Cap Funds:* India ki top 100 blue-chip companies me paisa lagta hai. Stable returns, low risk.\n"
            "• *2. Mid & Small Cap Funds:* Choti tez grow hone wali companies. High return potential, high volatility.\n"
            "• *3. Flexi Cap Funds:* Fund manager apni samajh se Large, Mid, Small sab me adjust karta hai. All-rounder choice.\n"
            "• *4. Index Funds (Nifty 50):* India ki economy par direct bet. Super low expense ratio.\n"
            "• *5. ELSS (Tax Saver):* Section 80C me tax bachao + equity return (3 saal lock-in).\n\n"
            "🚀 *Best Strategy:* Lumpsum dalne se behtar hai har mahine *SIP (Systematic Investment Plan)* lagao taaki compounding ka faayda mile!"
        )

    # 7. Conversational Chat & Slang Responses
    elif any(k in text for k in ["yes", "ha", "haa", "deal", "sahi hai", "done", "pakka"]):
        reply = "Full support hai bhai! Deal 100% pakki samjho 🤝 Aur bata kya chal raha hai?"

    elif any(k in text for k in ["hi", "hello", "hey", "bhai", "kaisa hai", "aur bhai"]):
        reply = "Ekdum first class mere bhai! Tu bata sab badhiya? Aaj trading me profit banana hai ya safe investment seekhni hai?"

    else:
        reply = (
            "Arre dost sab samajh raha hoon! 😎\n"
            "Puch le bina jhijhak:\n"
            "• *Color / Number Prediction*\n"
            "• *Market Trend (Up/Down)*\n"
            "• *Silver / Share Market Tips*\n"
            "• *Mutual Fund & SIP Guide*"
        )

    await update.message.reply_text(reply, parse_mode="Markdown")

# --- Main Runner ---
if __name__ == "__main__":
    # Flask thread
    threading.Thread(target=run_flask, daemon=True).start()

    BOT_TOKEN ="8889254295:AAFh8bYuFP5qty19cpP7HMFlPZ39lMNiU80"

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot start ho gaya hai...")
    application.run_polling()
