import os
import re
import random
import threading
from collections import Counter
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

user_scores = {}


def get_user_stats(user_id):
    if user_id not in user_scores:
        user_scores[user_id] = {"wins": 0, "losses": 0, "points": 100}
    return user_scores[user_id]


# --- 1. Render Port Server ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is online and working!")

    def log_message(self, format, *args):
        return


def run_web_server():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"Web server running on port {PORT}")
    httpd.serve_forever()


# --- 2. Keyboards (Game Charts) ---
def get_main_game_menu():
    keyboard = [
        [
            InlineKeyboardButton("Color Game", callback_data="menu_color"),
            InlineKeyboardButton("Number Game (0-9)", callback_data="menu_number"),
        ],
        [
            InlineKeyboardButton("Trading UP/DOWN", callback_data="menu_trade"),
            InlineKeyboardButton("Lucky Dice", callback_data="menu_dice"),
        ],
        [
            InlineKeyboardButton("My Score / Balance", callback_data="my_score"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_color_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("RED", callback_data="col_RED"),
            InlineKeyboardButton("GREEN", callback_data="col_GREEN"),
            InlineKeyboardButton("BLUE", callback_data="col_BLUE"),
        ],
        [InlineKeyboardButton("Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_number_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("0", callback_data="num_0"),
            InlineKeyboardButton("1", callback_data="num_1"),
            InlineKeyboardButton("2", callback_data="num_2"),
            InlineKeyboardButton("3", callback_data="num_3"),
            InlineKeyboardButton("4", callback_data="num_4"),
        ],
        [
            InlineKeyboardButton("5", callback_data="num_5"),
            InlineKeyboardButton("6", callback_data="num_6"),
            InlineKeyboardButton("7", callback_data="num_7"),
            InlineKeyboardButton("8", callback_data="num_8"),
            InlineKeyboardButton("9", callback_data="num_9"),
        ],
        [InlineKeyboardButton("Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_trade_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("UP (Bullish / Call)", callback_data="trd_UP"),
            InlineKeyboardButton("DOWN (Bearish / Put)", callback_data="trd_DOWN"),
        ],
        [InlineKeyboardButton("Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_dice_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="dic_1"),
            InlineKeyboardButton("2", callback_data="dic_2"),
            InlineKeyboardButton("3", callback_data="dic_3"),
        ],
        [
            InlineKeyboardButton("4", callback_data="dic_4"),
            InlineKeyboardButton("5", callback_data="dic_5"),
            InlineKeyboardButton("6", callback_data="dic_6"),
        ],
        [InlineKeyboardButton("Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


# --- 3. Game Callbacks & Handlers ---
async def send_game_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg:
        await msg.reply_text(
            "GAME & PREDICTION ZONE\n\n"
            "Apna game select karein:\n"
            "- Color Game (RED, GREEN, BLUE)\n"
            "- Number Game (0 to 9 Buttons)\n"
            "- Trading Trend (UP / DOWN)\n"
            "- Lucky Dice (1 to 6)",
            reply_markup=get_main_game_menu()
        )


async def game_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    stats = get_user_stats(user_id)

    if data == "menu_main":
        await query.edit_message_text(
            "GAME MENU\nEk game select karein:",
            reply_markup=get_main_game_menu()
        )
        return

    elif data == "menu_color":
        await query.edit_message_text(
            "COLOR PREDICTION\nColor select karein:",
            reply_markup=get_color_keyboard()
        )
        return

    elif data == "menu_number":
        await query.edit_message_text(
            "NUMBER GUESSING\n0 se 9 ke beech number chunein:",
            reply_markup=get_number_keyboard()
        )
        return

    elif data == "menu_trade":
        await query.edit_message_text(
            "TRADING TREND PREDICTION\nNext candle kya banegi? UP ya DOWN:",
            reply_markup=get_trade_keyboard()
        )
        return

    elif data == "menu_dice":
        await query.edit_message_text(
            "LUCKY DICE\nDice number chunein:",
            reply_markup=get_dice_keyboard()
        )
        return

    elif data == "my_score":
        await query.edit_message_text(
            f"Player: {user_name}\n"
            f"Points: {stats['points']}\n"
            f"Wins: {stats['wins']}\n"
            f"Losses: {stats['losses']}",
            reply_markup=get_main_game_menu()
        )
        return

    # Result processing
    win = False
    chosen = ""
    result = ""
    next_markup = get_main_game_menu()

    if data.startswith("col_"):
        chosen = data.replace("col_", "")
        result = random.choice(["RED", "GREEN", "BLUE"])
        win = (chosen == result)
        next_markup = get_color_keyboard()

    elif data.startswith("num_"):
        chosen = data.replace("num_", "")
        result = str(random.randint(0, 9))
        win = (chosen == result)
        next_markup = get_number_keyboard()

    elif data.startswith("trd_"):
        chosen = data.replace("trd_", "")
        result = random.choice(["UP", "DOWN"])
        win = (chosen == result)
        next_markup = get_trade_keyboard()

    elif data.startswith("dic_"):
        chosen = data.replace("dic_", "")
        result = str(random.randint(1, 6))
        win = (chosen == result)
        next_markup = get_dice_keyboard()

    if win:
        stats["wins"] += 1
        stats["points"] += 20
        msg_text = (
            f"Badhai ho, {user_name}! Aap jeet gaye!\n\n"
            f"Aapka Choice: {chosen}\n"
            f"Result: {result}\n"
            f"Reward: +20 Points\n\n"
            f"Score: {stats['wins']}W - {stats['losses']}L | Points: {stats['points']}"
        )
    else:
        stats["losses"] += 1
        stats["points"] = max(0, stats["points"] - 10)
        msg_text = (
            f"Oh! Galat anumaan.\n\n"
            f"Aapka Choice: {chosen}\n"
            f"Result: {result}\n"
            f"Penalty: -10 Points\n\n"
            f"Score: {stats['wins']}W - {stats['losses']}L | Points: {stats['points']}"
        )

    await query.edit_message_text(
        text=msg_text + "\n\nFir se khele niche se:",
        reply_markup=next_markup
    )


# --- 4. Trading Knowledge & Questions Helper ---
def answer_trading_query(text):
    t = text.lower()

    if any(w in t for w in ["call", "put"]):
        return (
            "TRADING GUIDE: CALL vs PUT\n\n"
            "- CALL (UP): Jab lagta hai market ka price upar jayega, tab Call buy kiya jata hai.\n"
            "- PUT (DOWN): Jab lagta hai market ka price neeche girega, tab Put buy kiya jata hai.\n\n"
            "Rule: Trend ke saath trade karein!"
        )

    if any(w in t for w in ["bullish", "bearish"]):
        return (
            "TRADING GUIDE: BULLISH vs BEARISH\n\n"
            "- BULLISH (Green): Market me khareedari zyada hai aur prices upar ja rahe hain.\n"
            "- BEARISH (Red): Market me bikwali zyada hai aur prices neeche gir rahe hain."
        )

    if any(w in t for w in ["support", "resistance"]):
        return (
            "TRADING GUIDE: SUPPORT & RESISTANCE\n\n"
            "- SUPPORT: Wo price level jahan se price neeche girna ruk jata hai aur bounce back karta hai.\n"
            "- RESISTANCE: Wo price level jahan se price upar jana ruk jata hai aur neeche gir sakta hai."
        )

    if any(w in t for w in ["loss", "recovery"]):
        return (
            "TRADING ADVICE: LOSS RECOVERY & RISK MANAGEMENT\n\n"
            "1. Revenge trading na karein (jaldbazi me loss recover karne ke chakkar me bada loss hota hai).\n"
            "2. Hamesha Stop-Loss ka use karein.\n"
            "3. Apne total capital ka sirf 1% se 2% hi ek trade me risk karein."
        )

    if any(w in t for w in ["candle", "candlestick", "pattern"]):
        return (
            "TRADING GUIDE: CANDLESTICK PATTERNS\n\n"
            "- Green Candle: Price open neeche hua aur close upar hua (Buyer strong).\n"
            "- Red Candle: Price open upar hua aur close neeche hua (Seller strong).\n"
            "- Popular Patterns: Hammer, Doji, Engulfing, Morning Star."
        )

    if any(w in t for w in ["indicator", "rsi", "macd"]):
        return (
            "TRADING GUIDE: INDICATORS\n\n"
            "- RSI (Relative Strength Index): 70 ke upar overbought (fall aa sakta hai), 30 ke neeche oversold (bounce aa sakta hai).\n"
            "- MACD: Trend reversal aur momentum identify karne ke liye use hota hai."
        )

    if any(w in t for w in ["trading", "trade", "market", "signal"]):
        return (
            "TRADING INFORMATION & ADVICE\n\n"
            "- Trading me patience aur discipline sabse zaroori hai.\n"
            "- Kabhi bhi bina analysis ya strategy ke trade na karein.\n"
            "- Historical patterns aur charts ko study karein.\n\n"
            "Tip: Bot me 'game' likhkar practice prediction karke dekh sakte hain!"
        )

    return None


# --- 5. Historical Data Analysis Logic ---
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

    reply = "DATA ANALYSIS & TREND REPORT\n\n"

    if colors:
        red = colors.count("RED")
        blue = colors.count("BLUE")
        total = len(colors)

        reply += "COLOR METRICS\n"
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

    if numbers:
        counter = Counter(numbers)

        reply += "NUMBER METRICS\n"
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
                "Most frequent: "
                + ", ".join(frequent)
                + f" ({highest_count} times)\n"
            )

        reply += "\n"

    reply += (
        "TREND / MARKET INFO\n"
        "- Uptrend: Price movement upar ki taraf hai.\n"
        "- Downtrend: Movement neeche ki taraf hai.\n"
        "- Caution: Ek single color se next result confirm nahi hota.\n\n"
        "DISCLAIMER: Ye historical data analysis hai, kisi next result ki guarantee nahi hai."
    )

    return reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg:
        await msg.reply_text(
            "Hello! Welcome.\n\n"
            "- Game khelne ke liye 'game' ya /game bhejein.\n"
            "- Trading ke baare me kuch bhi poochne ke liye sawal likhein.\n"
            "- Historical analysis ke liye RED/BLUE ya 0-9 numbers bhejein."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return

    text = msg.text.strip()
    lower_text = text.lower()

    # 1. Greetings (Hi / Hello / Hey)
    if lower_text in ["hi", "hello", "hey", "hy", "namaste", "hlo"]:
        user_name = msg.from_user.first_name if msg.from_user else "Friend"
        await msg.reply_text(
            f"Hello {user_name}! Main aapka Trading & Game Assistant Bot hoon.\n\n"
            "- 'game' likhein: Game & Prediction khelne ke liye.\n"
            "- Trading ka koi bhi sawal poochein (eg: 'Call Put kya hai', 'loss recovery', 'candle').\n"
            "- Historical data bhejein analysis ke liye (eg: RED BLUE RED 7 3 2)."
        )
        return

    # 2. Game trigger
    if any(g in lower_text for g in ["game", "play", "khelna", "khelao"]):
        await send_game_chart(update, context)
        return

    # 3. Historical Data Analysis (RED/BLUE & Numbers)
    analysis_result = analyze_data(text)
    if analysis_result:
        await msg.reply_text(analysis_result)
        return

    # 4. Trading Related Questions
    trading_reply = answer_trading_query(text)
    if trading_reply:
        await msg.reply_text(trading_reply)
        return

    # 5. General fallback
    if update.effective_chat and update.effective_chat.type == "private":
        await msg.reply_text(
            "Message receive ho gaya!\n\n"
            "- 'hi' ya 'hello' bhejein baat karne ke liye.\n"
            "- 'game' likhkar prediction game khele.\n"
            "- Trading se juda koi sawal likhein ya RED/BLUE analysis data bhejein."
        )


# --- 6. Main Execution ---
def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing.")

    # Start Render Port Server
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("game", send_game_chart))
    app.add_handler(CallbackQueryHandler(game_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is up and running...")
    app.run_polling()


if __name__ == "__main__":
    main()
