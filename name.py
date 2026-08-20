import asyncio
import logging
import random
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Render पर एरर मॉनिटरिंग के लिए लॉगिंग
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- टोकन्स और सेटिंग्स ---
BOT_TOKEN = "8640814348:AAHlJwDOmEKjY7hAzEXqybPdcslgKGnM-w4"
EARNKARO_API_KEY = "YOUR_EARNKARO_API_KEY"
CHANNEL_ID = "@YOUR_CHANNEL_USERNAME"  # यहाँ अपने चैनल का यूजरनेम डालें (उदा: @mydeals)

# ऑटो-पोस्ट के लिए टॉप डील्स की लिस्ट
DEALS_DATABASE = [
    {
        "title": "🔥 Noise Smartwatch - 70% तक भारी डिस्काउंट!",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
        "url": "https://www.flipkart.com/search?q=smartwatch"
    },
    {
        "title": "🎧 Wireless Earbuds - क्रिस्टल क्लियर साउंड और बेस!",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
        "url": "https://www.flipkart.com/search?q=earbuds"
    },
    {
        "title": "👟 Puma & Adidas Casual Shoes - बंपर सेल!",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
        "url": "https://www.flipkart.com/search?q=shoes"
    }
]

# एफिलिएट लिंक बनाने का फ़ंक्शन
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

# चैनल पर ऑटोमैटिक डील पोस्ट करने का बैकग्राउंड लूप
async def auto_post_deals_to_channel(app):
    while True:
        try:
            # लिस्ट में से कोई एक डील चुनना
            deal = random.choice(DEALS_DATABASE)
            aff_link = make_affiliate_link(deal["url"])

            caption = (
                f"🛍️ **{deal['title']}**\n\n"
                f"⚡ लिमिटेड टाइम डिस्काउंट ऑफर!\n"
                f"🔗 **यहाँ से खरीदें (Buy Now):**\n👉 {aff_link}\n\n"
                f"📢 *रोज़ाना बेस्ट डील्स के लिए चैनल से जुड़े रहें!*"
            )

            # चैनल पर फोटो + एफिलिएट लिंक पोस्ट करना
            await app.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=deal["image"],
                caption=caption,
                parse_mode="Markdown"
            )
            logging.info("चैनल पर नई डील सफलतापूर्वक पोस्ट कर दी गई है।")
        except Exception as e:
            logging.error(f"Channel Post Error: {e}")

        # हर 30 मिनट (1800 सेकंड) बाद अगली डील पोस्ट होगी
        await asyncio.sleep(1800)

# /start कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 **नमस्ते!**\n\n"
        "यह बॉट हमारे ऑफिशियल चैनल पर बेस्ट डिस्काउंट डील्स पोस्ट करता है।\n\n"
        "आप मुझसे सोना, चाँदी, क्रिप्टो या पर्सनल फाइनेंस से जुड़े सवाल भी पूछ सकते हैं!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# चैट में यूज़र के सवालों के स्मार्ट रिप्लाई
async def handle_chat_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if any(k in text for k in ["gold", "sona", "silver", "chandi", "सोना", "चाँदी"]):
        reply = (
            "🪙 **Gold & Silver Update:**\n\n"
            "सोने और चाँदी में मध्यम से लंबी अवधि का ट्रेंड मजबूत है। गिरावट आने पर धीरे-धीरे खरीदारी (Buy on Dips) की रणनीति अपनाई जाती है।"
        )
    elif any(k in text for k in ["crypto", "bitcoin", "btc", "eth", "क्रिप्टो"]):
        reply = (
            "📈 **Crypto Analysis:**\n\n"
            "क्रिप्टो मार्केट में भारी उतार-चढ़ाव रहता है। केवल वही पूँजी निवेश करें जिस पर आप जोखिम ले सकें और स्टॉप-लॉस का हमेशा ध्यान रखें।"
        )
    elif any(k in text for k in ["finance", "trading", "कमाई", "पैसे", "शेयर"]):
        reply = (
            "📚 **फाइनेंस का नियम:**\n\n"
            "1. किसी भी ट्रेड में 1-2% से अधिक रिस्क न लें।\n"
            "2. 6 महीने का इमरजेंसी फंड हमेशा बैंक में रखें।\n"
            "3. बिना स्टॉप-लॉस ट्रेड न करें।"
        )
    else:
        reply = "🔍 हमारे टेलीग्राम चैनल पर जाएँ, जहाँ बेस्ट शॉपिंग डील्स और लिंक्स ऑटोमैटिक शेयर किए जा रहे हैं!"

    await update.message.reply_text(reply, parse_mode="Markdown")

# बैकग्राउंड टास्क शुरू करने के लिए
async def post_init(app):
    asyncio.create_task(auto_post_deals_to_channel(app))

# मुख्य फ़ंक्शन
if __name__ == '__main__':
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_chat_messages))

    print("बॉट चालू हो गया है और चैनल पर डील्स भेजना शुरू कर रहा है...")
    app.run_polling()
