import os
import asyncio
import logging
import random
import requests
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Render logs ke liye logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- Configuration (Environment Variables prefer karein) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8640814348:AAHlJwDOmEKjY7hAzEXqybPdcslgKGnM-w4")
EARNKARO_API_KEY = os.getenv("EARNKARO_API_KEY", "YOUR_EARNKARO_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@YOUR_CHANNEL_USERNAME")  # e.g., @mydeals

# Shopping Deals Database (Amazon, Myntra, Flipkart, Meesho)
DEALS_DATABASE = [
    {
        "title": "🔥 Noise Smartwatch - 70% छूट!",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
        "url": "https://www.flipkart.com/search?q=smartwatch",
        "platform": "Flipkart"
    },
    {
        "title": "🎧 Boat / Boult Earbuds - Biggest Price Drop!",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
        "url": "https://www.amazon.in/s?k=earbuds",
        "platform": "Amazon"
    },
    {
        "title": "👗 Trendy Kurtis & Dresses - 60-80% OFF",
        "image": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600",
        "url": "https://www.myntra.com/dresses",
        "platform": "Myntra"
    },
    {
        "title": "👟 Casual Shoes & Sneakers - Lowest Price",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
        "url": "https://www.meesho.com/shoes",
        "platform": "Meesho"
    }
]

# EarnKaro Affiliate Link Generator
def make_affiliate_link(url: str) -> str:
    try:
        api_url = "https://api.earnkaro.com/v1/deals/generate-link"
        payload = {"url": url, "apiKey": EARNKARO_API_KEY}
        res = requests.post(api_url, json=payload, timeout=8)
        if res.status_code == 200:
            return res.json().get("affiliate_url", url)
    except Exception as e:
        logging.error(f"Affiliate Error: {e}")
    return url

# Bitcoin Live Price Tracker
def get_bitcoin_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr&include_24hr_change=true"
        res = requests.get(url, timeout=10).json()
        btc = res["bitcoin"]
        return {
            "usd": btc["usd"],
            "inr": btc["inr"],
            "change": round(btc["usd_24h_change"], 2)
        }
    except Exception as e:
        logging.error(f"Bitcoin API Error: {e}")
        return None

# Background Task: Auto Shopping Deals & Price Drop Alerts
async def auto_post_deals_to_channel(app):
    while True:
        try:
            deal = random.choice(DEALS_DATABASE)
            aff_link = make_affiliate_link(deal["url"])

            caption = (
                f"🛍️ **[LOOT DEAL - {deal['platform']}]**\n"
                f"🏷️ **{deal['title']}**\n\n"
                f"💥 भारी डिस्काउंट, सीमित समय के लिए!\n"
                f"🔗 **यहाँ से खरीदें:**\n👉 {aff_link}\n\n"
                f"📢 *रोज़ाना बेस्ट डील्स के लिए चैनल से जुड़े रहें!*"
            )

            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=deal["image"],
                caption=caption,
                parse_mode="Markdown"
            )
            logging.info("Deal posted successfully.")
        except Exception as e:
            logging.error(f"Channel Post Error: {e}")

        # Post every 30 minutes (1800 seconds)
        await asyncio.sleep(1800)

# Background Task: Bitcoin Market Movement Alert
async def auto_post_btc_alert(app):
    while True:
        try:
            data = get_bitcoin_price()
            if data:
                usd_price = data["usd"]
                inr_price = data["inr"]
                change = data["change"]

                direction = "🚀 Bullish / ऊपर जा रहा है" if change > 0 else "🔻 Bearish / नीचे आ रहा है"

                msg = (
                    f"⚡ **BITCOIN LIVE MARKET ALERT** ⚡\n\n"
                    f"💰 **Current Price (USD):** ${usd_price:,}\n"
                    f"🇮🇳 **Current Price (INR):** ₹{inr_price:,}\n"
                    f"📊 **24h Change:** {change}%\n"
                    f"📈 **Trend:** {direction}\n\n"
                    f"💡 *Risk Warning: क्रिप्टो मार्केट अत्यधिक वोलेटाइल है। स्टॉप-लॉस जरूर रखें।*"
                )

                await app.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
                logging.info("Bitcoin alert posted.")
        except Exception as e:
            logging.error(f"BTC Alert Error: {e}")

        # Check & alert every 2 hours (7200 seconds)
        await asyncio.sleep(7200)

# /start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 **नमस्ते!**\n\n"
        "यह बॉट आपको शॉपिंग डिस्काउंट डील्स (Amazon, Meesho, Myntra) और लाइव क्रिप्टो/गोल्ड अपडेट्स देता है।"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# /btc Command for On-Demand Price
async def btc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_bitcoin_price()
    if data:
        msg = (
            f"🪙 **Bitcoin Live Status**\n\n"
            f"💵 USD: ${data['usd']:,}\n"
            f"🇮🇳 INR: ₹{data['inr']:,}\n"
            f"📈 24h Change: {data['change']}%"
        )
    else:
        msg = "डाटा फेच करने में समस्या आ रही है। कृपया थोड़ी देर बाद प्रयास करें।"
    await update.message.reply_text(msg, parse_mode="Markdown")

# User Query Handler
async def handle_chat_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if any(k in text for k in ["btc", "bitcoin", "crypto", "क्रिप्टो"]):
        data = get_bitcoin_price()
        if data:
            reply = f"📈 **Bitcoin Update:** ${data['usd']:,} ({data['change']}%) | ट्रेंड: {'ऊपर' if data['change'] > 0 else 'नीचे'}"
        else:
            reply = "मार्केट डेटा अपडेट हो रहा है।"
    elif any(k in text for k in ["gold", "silver", "सोना", "चाँदी"]):
        reply = "🪙 **Gold/Silver:** लॉन्ग टर्म ट्रेंड पॉजिटिव है। गिरावट पर खरीदारी की रणनीति बेहतर मानी जाती है।"
    elif any(k in text for k in ["deal", "offer", "loot", "सस्ता"]):
        reply = "🛍️ हमारे ऑफिशियल चैनल पर जाएँ, जहाँ Amazon, Meesho और Myntra की टॉप ड्रॉप डील्स लगातार पोस्ट हो रही हैं!"
    else:
        reply = "❓ आप मुझसे /btc टाइप करके बिटकॉइन का भाव या बेस्ट शॉपिंग डील्स की जानकारी ले सकते हैं।"

    await update.message.reply_text(reply, parse_mode="Markdown")

# Post Init hook for starting background loops
async def on_startup(app):
    asyncio.create_task(auto_post_deals_to_channel(app))
    asyncio.create_task(auto_post_btc_alert(app))

# Dummy HTTP server for Render free web service
async def start_web_server():
    app = web.Application()
    app.router.add_get("/", lambda _: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("btc", btc_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat_messages))

    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())

    logging.info("Bot shuru ho chuka hai...")
    application.run_polling()

if __name__ == "__main__":
    main()
