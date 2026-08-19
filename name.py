import os
import re
from collections import Counter

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def analyze_data(text):
    if not text:
        return None

    upper_text = text.upper()

    colors = re.findall(r"\b(RED|BLUE)\b", upper_text)

    numbers = [
        int(x)
        for x in re.findall(r"\b\d+\b", upper_text)
        if 0 <= int(x) <= 9
    ]

    if not colors and not numbers:
        return None

    reply = "DATA ANALYSIS\n\n"

    # Color analysis
    if colors:
        red = colors.count("RED")
        blue = colors.count("BLUE")
        total = len(colors)

        reply += "COLOR\n"
        reply += f"RED: {red} ({red / total * 100:.1f}%)\n"
        reply += f"BLUE: {blue} ({blue / total * 100:.1f}%)\n"

        last_color = colors[-1]
        streak = 0

        for color in reversed(colors):
            if color == last_color:
                streak += 1
            else:
                break

        reply += f"Last color: {last_color}\n"
        reply += f"Current streak: {last_color} x {streak}\n"

        if red > blue:
            reply += "Observation: RED history me zyada hai.\n"
        elif blue > red:
            reply += "Observation: BLUE history me zyada hai.\n"
        else:
            reply += "Observation: RED aur BLUE barabar hain.\n"

        reply += "\n"

    # Number analysis
    if numbers:
        counter = Counter(numbers)

        reply += "NUMBER\n"
        reply += f"Numbers received: {len(numbers)}\n"
        reply += f"History: {' '.join(map(str, numbers))}\n"

        most_common = counter.most_common()

        if most_common:
            highest_count = most_common[0][1]
            frequent = [
                str(num)
                for num, count in most_common
                if count == highest_count
            ]

            reply += (
                "Most frequent in given history: "
                + ", ".join(frequent)
                + f" ({highest_count} times)\n"
            )

        reply += "\n"

    reply += (
        "TREND / MARKET INFO\n"
        "Uptrend ka matlab price movement generally upar ki taraf hota hai.\n"
        "Downtrend ka matlab movement generally neeche ki taraf hota hai.\n"
        "Sirf ek signal ya ek color se future result confirm nahi hota.\n\n"
        "IMPORTANT\n"
        "Ye historical data ka analysis hai. "
        "Next color, number ya market movement ki guarantee nahi hai."
    )

    return reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg:
        await msg.reply_text(
            "Welcome!\n\n"
            "Aap koi bhi text bhej sakte hain.\n"
            "RED/BLUE aur 0-9 ke historical data ko "
            "main analyze karunga.\n\n"
            "Example:\n"
            "RED BLUE RED RED BLUE 7 3 8 2 7"
        )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # सुरक्षित तरीका: पहले चेक करें कि मैसेज और टेक्स्ट मौजूद हैं
    msg = update.effective_message
    if not msg or not msg.text:
        return

    text = msg.text

    result = analyze_data(text)

    if result:
        await msg.reply_text(result)
    else:
        # अगर सिर्फ प्राइवेट चैट में यूजर गलत इनपुट भेजे तब हिंट दें
        if update.effective_chat and update.effective_chat.type == "private":
            await msg.reply_text(
                "Message receive ho gaya.\n\n"
                "RED/BLUE ya historical numbers bhejo.\n"
                "Example: RED BLUE RED 7 3 8"
            )


def main():
    if not BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable is missing."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
