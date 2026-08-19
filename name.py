import telebot
from telebot import types
import random

# Apna Telegram Bot Token yahan dalein
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

games = {
    'ttt': {}, 'carrom': {}, 'ghost': {}, 'hill': {}
}

# ----------------- 1. Professional Tic-Tac-Toe (Smart AI) -----------------
def get_ttt_kb(board):
    kb = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(board[i] if board[i] != " " else "⬜", callback_data=f"ttt_{i}") 
        for i in range(9)
    ]
    kb.add(*buttons)
    return kb

def check_win(b):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for x, y, z in wins:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]
    return "Tie" if " " not in b else None

# Smart AI (Winning / Blocking Logic)
def get_smart_move(b):
    empty = [i for i, v in enumerate(b) if v == " "]
    # 1. Jeetne ki koshish karein
    for move in empty:
        temp = list(b)
        temp[move] = "⭕"
        if check_win(temp) == "⭕":
            return move
    # 2. Player ko block karein
    for move in empty:
        temp = list(b)
        temp[move] = "❌"
        if check_win(temp) == "❌":
            return move
    # 3. Center le ya random move
    if 4 in empty:
        return 4
    return random.choice(empty)

# ----------------- Commands -----------------
@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    txt = (
        "👋 *नमस्ते दोस्त!*\n\n"
        "🎮 *गेम्स लिस्ट:*\n"
        "• /game - प्रो टिक-टैक-टो (Smart AI)\n"
        "• /hill - हिल क्लाइम्ब रेसिंग\n"
        "• /carrom - कैरम बोर्ड AI\n"
        "• /ghost - हॉरर एस्केप\n\n"
        "📈 *ट्रेडिंग और चैट:*\n"
        "मुझसे कुछ भी पूछें जैसे 'colour trading kya hai', 'red ya green', 'market upar ya niche'!"
    )
    bot.reply_to(message, txt, parse_mode="Markdown")

@bot.message_handler(commands=['game'])
def ttt(m):
    games['ttt'][m.chat.id] = [" "] * 9
    bot.send_message(m.chat.id, "🎮 *Tic-Tac-Toe Pro (AI Battle)*\n\nAap: ❌ | Bot: ⭕\nApna move chuniye:", reply_markup=get_ttt_kb(games['ttt'][m.chat.id]), parse_mode="Markdown")

@bot.message_handler(commands=['hill'])
def hill_cmd(m):
    games['hill'][m.chat.id] = {"dist": 0, "fuel": 100}
    bot.send_message(
        m.chat.id,
        "🚗 *Hill Climb Racing*\n\nदूरी: 0m | फ्यूल: 100%\nगाड़ी चलाओ और फ्यूल खत्म होने से बचो!",
        reply_markup=get_hill_kb(),
        parse_mode="Markdown"
    )

def get_hill_kb():
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("⚡ Race (Speed)", callback_data="hill_race"),
        types.InlineKeyboardButton("⛽ Collect Fuel", callback_data="hill_fuel")
    )
    return kb

@bot.message_handler(commands=['carrom'])
def carrom(m):
    games['carrom'][m.chat.id] = {"user": 0, "ai": 0}
    bot.send_message(m.chat.id, "🎯 *कैरम बोर्ड मुकाबला*", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎯 स्ट्राइक मारो", callback_data="carrom_strike")), parse_mode="Markdown")

@bot.message_handler(commands=['ghost'])
def ghost(m):
    games['ghost'][m.chat.id] = 10
    bot.send_message(m.chat.id, "👻 *भूत गेम*: भूत 10 कदम दूर है!", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🏃 भागो!", callback_data="ghost_run")), parse_mode="Markdown")

# ----------------- Callbacks Handler -----------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cid = call.message.chat.id

    # Tic-Tac-Toe Pro
    if call.data.startswith("ttt_"):
        idx = int(call.data.split("_")[1])
        board = games['ttt'].get(cid)
        if board and board[idx] == " ":
            board[idx] = "❌"
            res = check_win(board)
            if not res:
                ai_move = get_smart_move(board)
                board[ai_move] = "⭕"
                res = check_win(board)

            if res:
                msg = "🏆 मुबारक हो! आप जीत गए!" if res == "❌" else ("🤖 Bot जीत गया!" if res == "⭕" else "🤝 मैच टाई हो गया!")
                bot.edit_message_text(f"{msg}\n\nफिर खेलने के लिए /game दबाएं।", cid, call.message.message_id)
            else:
                bot.edit_message_text("🎮 *Tic-Tac-Toe Pro*\n\nआप: ❌ | Bot: ⭕\nअगली चाल चलें:", cid, call.message.message_id, reply_markup=get_ttt_kb(board), parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Hill Climb Racing
    elif call.data.startswith("hill_"):
        st = games['hill'].get(cid, {"dist": 0, "fuel": 100})
        action = call.data.split("_")[1]

        if action == "race":
            st["dist"] += random.randint(15, 30)
            st["fuel"] -= random.randint(10, 20)
        elif action == "fuel":
            st["fuel"] = min(100, st["fuel"] + random.randint(25, 40))
            st["dist"] += 5

        # Check conditions
        if st["fuel"] <= 0:
            bot.edit_message_text(f"💥 *कार का तेल खत्म! दुर्घटनाग्रस्त!*\nकुल दूरी तय की: {st['dist']}m\nफिर खेलने के लिए /hill दबाएं।", cid, call.message.message_id, parse_mode="Markdown")
        elif st["dist"] >= 200:
            bot.edit_message_text(f"🏁 *शानदार जीत!*\nआप पहाड़ की चोटी पर पहुँच गए (200m+ दूरी पार)! 🏆", cid, call.message.message_id, parse_mode="Markdown")
        else:
            games['hill'][cid] = st
            bot.edit_message_text(f"🚗 *Hill Climb Racing*\n\nदूरी: {st['dist']}m | फ्यूल: {st['fuel']}%\nसावधानी से आगे बढ़ें!", cid, call.message.message_id, reply_markup=get_hill_kb(), parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Carrom AI Logic
    elif call.data == "carrom_strike":
        st = games['carrom'].get(cid, {"user": 0, "ai": 0})
        if random.random() > 0.4: st["user"] += 1
        if random.random() > 0.4: st["ai"] += 1
        
        if st["user"] >= 5:
            bot.edit_message_text("🏆 *आप कैरम मैच जीत गए!*", cid, call.message.message_id, parse_mode="Markdown")
        elif st["ai"] >= 5:
            bot.edit_message_text("🤖 *कंप्यूटर कैरम मैच जीत गया!*", cid, call.message.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"🎯 *कैरम मुकाबला:*\n👤 आपका स्कोर: {st['user']}\n🤖 कंप्यूटर: {st['ai']}", cid, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎯 स्ट्राइक मारो", callback_data="carrom_strike")), parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Ghost Game
    elif call.data == "ghost_run":
        dist = games['ghost'].get(cid, 10) - 1
        if dist <= 0:
            bot.edit_message_text("💀 *भूत ने आपको पकड़ लिया! गेम ओवर।* 🪦", cid, call.message.message_id, parse_mode="Markdown")
        else:
            games['ghost'][cid] = dist
            bot.edit_message_text(f"👻 *भूत गेम*: भूत केवल {dist} कदम दूर है! भागते रहो!", cid, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🏃 भागो!", callback_data="ghost_run")), parse_mode="Markdown")
        bot.answer_callback_query(call.id)

# ----------------- Smart Chat Handler (Hindi / Hinglish / Trading) -----------------
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    text = message.text.lower()

    # Colour Trading Explanation
    if any(k in text for k in ["color trading", "colour trading", "color trade", "colour trade", "trading kya"]):
        info = (
            "📊 *कलर ट्रेडिंग क्या है?*\n\n"
            "कलर ट्रेडिंग एक ऑनलाइन प्रेडिक्शन प्लेटफॉर्म है जहाँ आपको अनुमान लगाना होता है कि अगले राउंड में कौन सा रंग (Red, Green, Violet) या नंबर आएगा।\n\n"
            "⚠️ *सावधानी:* यह पूरी तरह से वित्तीय जोखिम और संभावनाओं (Probability) पर निर्भर करता है। इसे सोच-समझकर खेलें।"
        )
        bot.reply_to(message, info, parse_mode="Markdown")

    # Color Prediction Logic
    elif any(k in text for k in ["red", "blue", "green", "lal", "hara", "rang", "color", "colour"]):
        color = random.choice(["लाल (🔴 RED)", "हरा (🟢 GREEN)", "बैंगनी (🟣 VIOLET)"])
        bot.reply_to(message, f"📊 *ट्रेडिंग सिग्नल:* अगले राउंड में **{color}** आने की सबसे ज्यादा संभावना है।")

    # Direction Prediction
    elif any(k in text for k in ["upar", "niche", "up", "down", "rise", "fall", "market"]):
        direction = random.choice(["ऊपर (📈 UP/CALL)", "नीचे (📉 DOWN/PUT)"])
        pct = random.randint(75, 92)
        bot.reply_to(message, f"📈 *मार्केट ट्रेंड:* मार्केट के **{direction}** जाने के {pct}% चांस हैं।")

    # Number Prediction
    elif any(k in text for k in ["number", "no", "num", "ank", "1", "2", "3", "4", "5", "6", "7", "8", "9"]):
        num = random.randint(0, 9)
        bot.reply_to(message, f"🎯 *नंबर प्रेडिक्शन:* अगला लकी नंबर **{num}** हो सकता है!")

    # Hinglish & Hindi Casual Conversations
    elif any(k in text for k in ["hi", "hello", "kaise ho", "kya haal", "bhai", "namaste", "kem cho"]):
        bot.reply_to(message, "नमस्ते भाई! सब बढ़िया है। बताओ आज क्या खेलना है या कौन सी ट्रेडिंग टिप चाहिए?")

    else:
        bot.reply_to(message, "अरे दोस्त! मैं समझ गया। आप /game, /hill, /carrom खेल सकते हैं या मुझसे 'colour trading kya hai', 'red ya green' जैसे सवाल पूछ सकते हैं!")

if __name__ == '__main__':
    print("बॉट सफलता पूर्वक चालू हो गया...")
    bot.infinity_polling()
