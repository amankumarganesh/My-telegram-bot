import os
import re

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste!\n\n"
        "RED/BLUE history bhejo.\n"
        "Example:\n"
        "RED BLUE RED RED BLUE\n\n"
        "Main data ka analysis karke bataunga."
    )


def analyze_colors(text):
    colors = re.findall(r"\b(RED|BLUE)\b", text.upper())

    if not colors:
        return None

    red = colors.count("RED")
    blue = colors.count("BLUE")
    total = len(colors)

    red_percent = red / total * 100
    blue_percent = blue / total * 100

    last = colors[-1]

    streak = 0
    for color in reversed(colors):
        if color == last:
            streak += 1
        else:
            break

    if red > blue:
        observation = "Is history me RED zyada hai."
    elif blue > red:
        observation = "Is history me BLUE zyada hai."
    else:
        observation = "RED aur BLUE barabar hain."

    return (
        "COLOR TRADING DATA ANALYSIS\n\n"
        f"Total: {total}\n"
        f"RED: {red} ({red_percent:.1f}%)\n"
        f"BLUE: {blue} ({blue_percent:.1f}%)\n\n"
        f"Last result: {last}\n"
        f"Current streak: {last} x {streak}\n\n"
        f"Observation: {observation}\n\n"
        "Note: Ye historical data ka analysis hai. "
        "Next result ki guarantee nahi hai."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    result = analyze_colors(text)

    if result:
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(
            "Message mil gaya.\n\n"
            "RED aur BLUE data bhejo.\n"
            "Example: RED BLUE RED BLUE RED"
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
