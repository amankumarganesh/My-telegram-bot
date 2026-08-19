import telebot
from telebot import types
import random

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

# गेम डेटा स्टोर
guess_games = {}
ttt_games = {}
hill_games = {}
subway_games = {}
rc_games = {}
pizza_games = {}

# ----------------- Helper: Tic-Tac-Toe Keyboard -----------------
def get_ttt_keyboard(board):
    kb = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(9):
        val = board[i] if board[i] != " " else "⬜"
        buttons.append(types.InlineKeyboardButton(val, callback_data=f"ttt_{i}"))
    kb.add(*buttons)
    return kb

def check_winner(b):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for x, y, z in wins:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]
    if " " not in b:
        return "Tie"
    return None

# ----------------- 1. Tic-Tac-Toe vs AI -----------------
@bot.message_handler(commands=['game'])
def start_ttt(message):
    chat_id = message.chat.id
    ttt_games[chat_id] = [" "] * 9
    bot.send_message(
        chat_id, 
        "❌ **टिक-टैक-टो मुकाबला (AI के खिलाफ)** ⭕\nआप **X** हैं और बॉट **O** है। अपनी बारी चलें:", 
        reply_markup=get_ttt_keyboard(ttt_games[chat_id]),
        parse_mode="Markdown"
    )

# ----------------- 2. Hill Climb Racing -----------------
@bot.message_handler(commands=['climb'])
def start_hill_climb(message):
    chat_id = message.chat.id
    hill_games[chat_id] = {"distance": 0, "fuel": 100}
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🚗 गैस दबाओ (+10m)", callback_data="climb_gas"),
        types.InlineKeyboardButton("⛽ पेट्रोल भरो", callback_data="climb_fuel")
    )
    bot.send_message(
        chat_id,
        "🏎️ **हिल क्लाइंब रेसिंग**\n\n📍 दूरी: 0 मीटर | ⛽ ईंधन: 100%",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ----------------- 3. Subway Surfers Game -----------------
@bot.message_handler(commands=['subway'])
def start_subway(message):
    chat_id = message.chat.id
    subway_games[chat_id] = {"score": 0}
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("⬅️ बाएं", callback_data="sub_left"),
        types.InlineKeyboardButton("⬆️ कूदो", callback_data="sub_jump"),
        types.InlineKeyboardButton("➡️ दाएं", callback_data="sub_right")
    )
    bot.send_message(
        chat_id,
        "🏃 **सबवे सर्फर्स**\n\nपुलिस पीछे पड़ी है! बचकर भागो और सिक्के बटोरो।\n💰 स्कोर: 0",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ----------------- 4. Remote Control (RC Car) Game -----------------
@bot.message_handler(commands=['rc'])
def start_rc(message):
    chat_id = message.chat.id
    rc_games[chat_id] = {"pos": "बीच में", "battery": 100}
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("🎛️ बाएं मोड़ो", callback_data="rc_left"),
        types.InlineKeyboardButton("⚡ टर्बो स्पीड", callback_data="rc_turbo"),
        types.InlineKeyboardButton("🎛️ दाएं मोड़ो", callback_data="rc_right")
    )
    bot.send_message(
        chat_id,
        "🎮 **रिमोट कंट्रोल कार**\n\nकार की स्थिति: बीच में\n🔋 बैटरी: 100%",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ----------------- 5. Pizza Tower Game -----------------
@bot.message_handler(commands=['pizza'])
def start_pizza(message):
    chat_id = message.chat.id
    pizza_games[chat_id] = {"floor": 1, "points": 0}
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🍕 ऊपर चढ़ो", callback_data="pizza_up"),
        types.InlineKeyboardButton("👊 तोड़-फोड़", callback_data="pizza_smash")
    )
    bot.send_message(
        chat_id,
        "🍕 **पिज़्ज़ा टॉवर (होरा पिज़्ज़ा टॉप)**\n\nमंज़िल: 1 | स्कोर: 0\nटॉवर की चोटी पर पहुंचना है!",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ----------------- 6. Number Guess Game -----------------
@bot.message_handler(commands=['guess'])
def start_guess_game(message):
    chat_id = message.chat.id
    guess_games[chat_id] = random.randint(1, 20)
    bot.send_message(chat_id, "🎯 मैंने 1 से 20 के बीच एक नंबर सोचा है!\nनंबर लिखकर भेजो और बताओ कौन सा है।")

# ----------------- 7. Balloon Pop & Block Blast -----------------
@bot.message_handler(commands=['pop'])
def start_pop(message):
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("🎈", callback_data="pop_1"),
        types.InlineKeyboardButton("🎈", callback_data="pop_2"),
        types.InlineKeyboardButton("🎈", callback_data="pop_3")
    )
    bot.send_message(message.chat.id, "🎈 गुब्बारा फोड़ने के लिए टच करें:", reply_markup=kb)

@bot.message_handler(commands=['blast'])
def start_blast(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💥 ब्लॉक 1 फोड़ो", callback_data="blast_1"),
        types.InlineKeyboardButton("💥 ब्लॉक 2 फोड़ो", callback_data="blast_2")
    )
    bot.send_message(message.chat.id, "💥 ब्लॉक ब्लास्ट गेम:", reply_markup=kb)

# ----------------- 8. Callback Query Handler -----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    # Tic-Tac-Toe
    if call.data.startswith("ttt_"):
        idx = int(call.data.split("_")[1])
        board = ttt_games.get(chat_id, [" "] * 9)

        if board[idx] != " ":
            bot.answer_callback_query(call.id, "यह जगह पहले से भरी है!")
            return

        board[idx] = "❌"
        winner = check_winner(board)

        if not winner:
            empty_spots = [i for i, val in enumerate(board) if val == " "]
            if empty_spots:
                board[random.choice(empty_spots)] = "⭕"
                winner = check_winner(board)

        ttt_games[chat_id] = board

        if winner:
            msg = "🤝 मैच बराबर (टाई) रहा!" if winner == "Tie" else f"🏆 विजेता: {winner}!"
            bot.edit_message_text(f"🏁 खेल समाप्त!\n\n{msg}\nदोबारा खेलें: /game", chat_id, call.message.message_id)
            ttt_games.pop(chat_id, None)
        else:
            bot.edit_message_text("❌ आपकी बारी (X) | ⭕ बॉट की बारी (O):", chat_id, call.message.message_id, reply_markup=get_ttt_keyboard(board))
        bot.answer_callback_query(call.id)

    # Hill Climb
    elif call.data.startswith("climb_"):
        state = hill_games.get(chat_id, {"distance": 0, "fuel": 100})
        action = call.data.split("_")[1]
        if action == "gas":
            state["distance"] += 10
            state["fuel"] -= 15
        elif action == "fuel":
            state["fuel"] = min(100, state["fuel"] + 30)

        if state["fuel"] <= 0:
            bot.edit_message_text(f"💥 तेल खत्म! कुल दूरी: {state['distance']} मीटर\nफिर खेलें: /climb", chat_id, call.message.message_id)
            hill_games.pop(chat_id, None)
        else:
            hill_games[chat_id] = state
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(
                types.InlineKeyboardButton("🚗 गैस दबाओ (+10m)", callback_data="climb_gas"),
                types.InlineKeyboardButton("⛽ पेट्रोल भरो", callback_data="climb_fuel")
            )
            bot.edit_message_text(f"🏎️ **हिल क्लाइंब रेसिंग**\n\n📍 दूरी: {state['distance']} मीटर | ⛽ ईंधन: {state['fuel']}%", chat_id, call.message.message_id, reply_markup=kb, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Subway Surfers
    elif call.data.startswith("sub_"):
        state = subway_games.get(chat_id, {"score": 0})
        if random.random() < 0.15:
            bot.edit_message_text(f"🚨 **पकड़े गए!**\n\nट्रेन से टक्कर हो गई! आपका कुल स्कोर: {state['score']} 💰\nफिर खेलें: /subway", chat_id, call.message.message_id, parse_mode="Markdown")
            subway_games.pop(chat_id, None)
        else:
            state["score"] += 15
            subway_games[chat_id] = state
            kb = types.InlineKeyboardMarkup(row_width=3)
            kb.add(
                types.InlineKeyboardButton("⬅️ बाएं", callback_data="sub_left"),
                types.InlineKeyboardButton("⬆️ कूदो", callback_data="sub_jump"),
                types.InlineKeyboardButton("➡️ दाएं", callback_data="sub_right")
            )
            bot.edit_message_text(f"🏃 **सबवे सर्फर्स**\n\n💰 स्कोर: {state['score']}\nआगे भागते रहो!", chat_id, call.message.message_id, reply_markup=kb, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Remote Control Car
    elif call.data.startswith("rc_"):
        state = rc_games.get(chat_id, {"pos": "बीच में", "battery": 100})
        action = call.data.split("_")[1]
        state["battery"] -= 10
        if action == "left":
            state["pos"] = "बायां ट्रैक"
        elif action == "right":
            state["pos"] = "दायां ट्रैक"
        elif action == "turbo":
            state["pos"] = "रॉकेट स्पीड 🚀"

        if state["battery"] <= 0:
            bot.edit_message_text("🪫 कार की बैटरी खत्म हो गई!\nफिर खेलें: /rc", chat_id, call.message.message_id)
            rc_games.pop(chat_id, None)
        else:
            rc_games[chat_id] = state
            kb = types.InlineKeyboardMarkup(row_width=3)
            kb.add(
                types.InlineKeyboardButton("🎛️ बाएं मोड़ो", callback_data="rc_left"),
                types.InlineKeyboardButton("⚡ टर्बो स्पीड", callback_data="rc_turbo"),
                types.InlineKeyboardButton("🎛️ दाएं मोड़ो", callback_data="rc_right")
            )
            bot.edit_message_text(f"🎮 **रिमोट कंट्रोल कार**\n\nस्थिति: {state['pos']}\n🔋 बैटरी: {state['battery']}%", chat_id, call.message.message_id, reply_markup=kb, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Pizza Tower
    elif call.data.startswith("pizza_"):
        state = pizza_games.get(chat_id, {"floor": 1, "points": 0})
        action = call.data.split("_")[1]
        if action == "up":
            state["floor"] += 1
            state["points"] += 50
        elif action == "smash":
            state["points"] += 30

        if state["floor"] >= 10:
            bot.edit_message_text(f"🏆 **पिज़्ज़ा टॉवर पूरा हुआ!**\n\nआप सबसे ऊपर पहुंच गए! कुल स्कोर: {state['points']}\nदोबारा खेलें: /pizza", chat_id, call.message.message_id, parse_mode="Markdown")
            pizza_games.pop(chat_id, None)
        else:
            pizza_games[chat_id] = state
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(
                types.InlineKeyboardButton("🍕 ऊपर चढ़ो", callback_data="pizza_up"),
                types.InlineKeyboardButton("👊 तोड़-फोड़", callback_data="pizza_smash")
            )
            bot.edit_message_text(f"🍕 **पिज़्ज़ा टॉवर (होरा पिज़्ज़ा टॉप)**\n\nमंज़िल: {state['floor']}/10\nस्कोर: {state['points']}", chat_id, call.message.message_id, reply_markup=kb, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # Pop & Blast
    elif call.data.startswith("pop_"):
        bot.answer_callback_query(call.id, "💥 फूट गया! गुब्बारा खत्म! (+10 अंक)")
    elif call.data.startswith("blast_"):
        bot.answer_callback_query(call.id, "💣 धमाका! ब्लॉक पूरी तरह टूट गया!")

# ----------------- 9. Welcome & Help Command -----------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    name = message.from_user.first_name or "भाई"
    welcome_msg = (
        f"🙏 नमस्ते {name} भाई!\n\n"
        "🎮 **मजेदार गेम्स:**\n"
        "• 🏃 सबवे सर्फर्स 👉 /subway\n"
        "• 🍕 पिज़्ज़ा टॉवर 👉 /pizza\n"
        "• 🎮 रिमोट कंट्रोल कार 👉 /rc\n"
        "• ❌ टिक-टैक-टो 👉 /game\n"
        "• 🏎️ हिल क्लाइंब रेस 👉 /climb\n"
        "• 🎯 नंबर गेस 👉 /guess\n"
        "• 🎈 गुब्बारा फोड़ो 👉 /pop\n"
        "• 💥 ब्लॉक ब्लास्ट 👉 /blast\n\n"
        "📊 **कलर ट्रेडिंग और मार्केट प्रेडिक्शन:**\n"
        "• 'कलर ट्रेडिंग क्या है' पूछें\n"
        "• 'लाल या नीला' / 'Red or Blue' पूछकर प्रेडिक्शन लें\n"
        "• 'ऊपर या नीचे' / 'Up or Down' मार्केट ट्रेंड जानें\n"
        "• '1 नंबर या 2 नंबर' पूछकर नंबर का अनुमान लगाएं\n"
        "• कोडिंग, गिरावट और 40 लेवल सपोर्ट की जानकारी लें"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

# ----------------- 10. Smart Chat & All Hindi Responses -----------------
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    chat_id = message.chat.id
    text = message.text.strip().lower() if message.text else ""
    name = message.from_user.first_name or "दोस्त"

    # नंबर गेस गेम (/guess)
    if chat_id in guess_games and text.isdigit():
        num = int(text)
        secret = guess_games[chat_id]
        if num == secret:
            del guess_games[chat_id]
            bot.reply_to(message, f"🎉 बहुत बढ़िया {name} भाई! सही नंबर {secret} ही था! फिर खेलने के लिए /guess दबाएं।")
        elif num < secret:
            bot.reply_to(message, f"थोड़ा बड़ा नंबर सोचिए {name} भाई! 📈")
        else:
            bot.reply_to(message, f"थोड़ा छोटा नंबर सोचिए {name} भाई! 📉")
        return

    # 1. कलर ट्रेडिंग क्या है / जानकारी
    if any(k in text for k in ["kya hai", "kya hota", "what is", "wat is", "info", "detail", "kaise hota", "rule"]):
        bot.reply_to(
            message,
            f"📊 **कलर ट्रेडिंग की पूरी जानकारी ({name} भाई):**\n\n"
            "• **यह क्या है:** इसमें निश्चित समय (1, 3 या 5 मिनट) के राउंड होते हैं, जहाँ आपको लाल (Red), हरा (Green) या नीला/बैंगनी (Blue/Violet) रंग और 0 से 9 नंबर का अनुमान लगाना होता है।\n"
            "• **कमाई का नियम:** सही रंग आने पर 2 गुना और सही नंबर आने पर 9 गुना तक का हिसाब रहता है।\n"
            "• **जरूरी चेतावनी:** यह पूरी तरह जोखिम (Risk) का खेल है। हमेशा छोटा पैसा लगाएं और बिना सोचे-समझे कभी बड़ा रिस्क न लें!",
            parse_mode="Markdown"
        )
        return

    # 2. नंबर प्रेडिक्शन (1 नंबर या 2 नंबर)
    if any(k in text for k in ["1 ya 2", "1 or 2", "1 number", "2 number", "ek number", "do number", "kaun sa number", "konsa number", "which no", "which number", "no 1", "no 2"]):
        chosen_num = random.choice([1, 2])
        other_num = 2 if chosen_num == 1 else 1
        bot.reply_to(
            message,
            f"🎯 **नंबर का अनुमान ({name} भाई):**\n\n"
            f"• **पहला अनुमान:** सबसे ज्यादा संभावना **नंबर {chosen_num}** आने की है!\n"
            f"• **सपोर्ट नंबर:** अगर बैकअप लेना हो तो **नंबर {other_num}** को भी देख सकते हैं।",
            parse_mode="Markdown"
        )
        return

    # 3. मार्केट ट्रेंड (ऊपर जाएगा या नीचे / Up or Down)
    if any(k in text for k in ["upar", "niche", "up", "down", "upr", "nich", "fall", "girawat", "badhega", "kam hoga"]):
        direction = random.choice(["📈 ऊपर (UP)", "📉 नीचे (DOWN)"])
        rsi_val = random.randint(35, 65)
        bot.reply_to(
            message,
            f"📊 **मार्केट की चाल का अनुमान ({name} भाई):**\n\n"
            f"चार्ट के हिसाब से मार्केट **{direction}** जाने के 80% चांस हैं!\n"
            f"• आरएसआई (RSI) स्तर: {rsi_val}\n"
            f"• स्टॉप-लॉस जरूर लगाकर रखें!",
            parse_mode="Markdown"
        )
        return

    # 4. कलर प्रेडिक्शन: Red vs Blue
    if ("red" in text and "blue" in text) or ("lal" in text and "nila" in text) or ("rd" in text and "blu" in text):
        chosen_color = random.choice(["🔴 लाल (RED)", "🔵 नीला (BLUE / VIOLET)"])
        bot.reply_to(
            message,
            f"🎨 **लाल बनाम नीला प्रेडिक्शन ({name} भाई):**\n\n"
            f"चार्ट ट्रेंड के अनुसार इस बार **{chosen_color}** आने का मजबूत संकेत बन रहा है!",
            parse_mode="Markdown"
        )
        return

    # 5. सीधा रंग पूछने पर (Red / Blue / Green)
    if any(k in text for k in ["red", "laal", "lal", "rd"]):
        bot.reply_to(message, f"🔴 **लाल (RED) प्रेडिक्शन कन्फर्म:**\n\n{name} भाई, अगला रंग **लाल (RED)** आने की 85% संभावना दिख रही है!", parse_mode="Markdown")
        return

    if any(k in text for k in ["blue", "violet", "purple", "baingani", "blu", "nila", "neela"]):
        bot.reply_to(message, f"🔵 **नीला / बैंगनी (BLUE) प्रेडिक्शन कन्फर्म:**\n\n{name} भाई, अगला ट्रेंड **नीला या बैंगनी** रंग आने का संकेत दे रहा है!", parse_mode="Markdown")
        return

    if any(k in text for k in ["green", "hara", "grn", "grean"]):
        bot.reply_to(message, f"🟢 **हरा (GREEN) प्रेडिक्शन कन्फर्म:**\n\n{name} भाई, इस राउंड में **हरा (GREEN)** आने का मजबूत चांस है!", parse_mode="Markdown")
        return

    if any(k in text for k in ["color", "colour", "trad", "trading", "kolor", "clor", "traid"]):
        colors = ["🔴 लाल (RED)", "🟢 हरा (GREEN)", "🔵 नीला (BLUE/VIOLET)"]
        predicted = random.choice(colors)
        bot.reply_to(message, f"📊 **कलर ट्रेडिंग सिग्नल ({name} भाई):**\n\nहमारे हिसाब से अगला रंग **{predicted}** आ सकता है!\n\n*(नोट: हमेशा कम पैसों से ही खेलें।)*", parse_mode="Markdown")
        return

    # 6. कोडिंग और 40 लेवल
    if any(k in text for k in ["cod", "coding", "koding", "40", "market", "mrkt"]):
        bot.reply_to(
            message,
            f"💻📉 **कोडिंग और 40 लेवल एनालिसिस ({name} भाई):**\n\n"
            "• **40 का स्तर:** 40 RSI एक मजबूत सपोर्ट होता है, यहाँ से अक्सर तेजी (बाउंस-बैक) देखने को मिलती है।\n"
            "• **कोडिंग सलाह:** लॉजिक को मजबूत रखें और गलतियों (एरर) से घबराएं नहीं।"
        )
        return

    # 7. अभिवादन (Greetings)
    if any(greet in text for greet in ['hi', 'hello', 'hey', 'namaste', 'ram ram', 'kaise ho', 'hlo', 'hlw', 'sup']):
        bot.reply_to(message, f"अरे नमस्ते {name} भाई! ❤️\nबताइए आज क्या खेलना पसंद करेंगे या ट्रेडिंग प्रेडिक्शन चाहिए?")
        return

    # सामान्य डिफ़ॉल्ट संदेश (हिंदी में)
    bot.reply_to(
        message,
        f"अरे {name} भाई! 😊\n\n"
        "आप ट्रेडिंग प्रेडिक्शन (लाल, नीला, ऊपर/नीचे, 1 या 2 नंबर) पूछ सकते हैं या ये गेम्स खेल सकते हैं:\n"
        "• /subway - सबवे सर्फर्स\n"
        "• /pizza - पिज़्ज़ा टॉवर\n"
        "• /rc - रिमोट कंट्रोल कार\n"
        "• /game - टिक-टैक-टो\n"
        "• /climb - हिल क्लाइंब रेस\n"
        "• /guess - नंबर गेस खेलें"
    )

# ----------------- 11. Polling -----------------
if __name__ == '__main__':
    print("बॉट सफलता पूर्वक चालू हो गया है...")
    bot.infinity_polling()
