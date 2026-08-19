import os
from threading import Thread
from flask import Flask
import telebot

# ----------------- 1. Web Server for Render -----------------
app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive and running!'


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.daemon = True
  t.start()


keep_alive()

# ----------------- 2. Bot Configuration -----------------
# Environment variable se token lega ya direct token use karega
BOT_TOKEN = os.environ.get(
    'BOT_TOKEN', '8889254295:AAHh8bYuFP5qty19cpP7HMFlPZ39LMniU80'
)
bot = telebot.TeleBot(BOT_TOKEN)


# /start aur /help command handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  welcome_text = (
      '🙏 आपका बहुत-बहुत स्वागत है!\n\n'
      'मैं आपका स्मार्ट असिस्टेंट हूँ। आप मुझसे कोडिंग, कलर ट्रेडिंग या ज़िंदगी से जुड़ा '
      'कोई भी सवाल पूछ सकते हैं। बताइए मैं आपकी क्या मदद करूँ?'
  )
  bot.reply_to(message, welcome_text)


# Sabhi messages ka reply dene ke liye handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
  user_text = message.text.lower() if message.text else ''

  # 1. Agar Coding, Girawat ya 40 ke baare me ho
  if 'coding' in user_text or 'girawat' in user_text or '40' in user_text:
    reply = (
        'नमस्ते भाई! 👋\n\n'
        '💻 **Coding & Analysis Update:**\n'
        '• कोडिंग में लॉजिक और एरर हैंडलिंग सबसे महत्वपूर्ण है।\n'
        '• गिरावट (Market/Trend Fall) या 40 के लेवल पर हमेशा रिस्क मैनेजमेंट और स्टॉप-लॉस का ध्यान रखें।\n'
        '• धैर्य रखें और सही स्ट्रेटेजी के साथ आगे बढ़ें।\n\n'
        'अगर आपको कोई खास कोडिंग या डेटा चाहिए तो ज़रूर बताएं!'
    )

  # 2. Agar Color Trading se related ho
  elif (
      'color' in user_text
      or 'colour' in user_text
      or 'trading' in user_text
      or 'trade' in user_text
  ):
    reply = (
        'स्वागत है आपका! 📈\n\n'
        '🎨 **Color Trading Info:**\n'
        '• कलर ट्रेडिंग में रेड, ग्रीन और वॉयलेट जैसे कलर्स पर प्रेडिक्शन होता है।\n'
        '• इसमें बहुत जोखिम (Risk) होता है, इसलिए बिना सही समझ और बजट के कभी भी बड़ा पैसा न लगाएं।\n'
        '• हमेशा समझदारी और सावधानी से खेलें!'
    )

  # 3. Agar Zindagi ya Life ke baare me ho
  elif 'zindagi' in user_text or 'life' in user_text:
    reply = (
        'जी भाई, ज़िंदगी का सफर बहुत खूबसूरत है! ✨\n\n'
        'उतार-चढ़ाव तो हर जगह आते हैं, चाहे ज़िंदगी हो या ट्रेडिंग। बस सीखते रहिए, '
        'मेहनत करते रहिए और हमेशा सकारात्मक रहिए।'
    )

  # 4. Koi banda kuch bhi aur likhe, to ye polite & welcoming reply jayega
  else:
    reply = (
        f'🙏 नमस्ते {message.from_user.first_name}! आपका स्वागत है।\n\n'
        'मुझे आपका मैसेज मिल गया है। आप कोडिंग, गिरावट/40, कलर ट्रेडिंग या ज़िंदगी से जुड़ा '
        'कोई भी सवाल पूछ सकते हैं। मैं आपकी पूरी मदद के लिए यहाँ हूँ!'
    )

  bot.reply_to(message, reply)


# Bot ko continuously chalane ke liye
if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()

import telebot
from telebot import types

# Yahan apna Telegram Bot Token dalein
BOT_TOKEN = "8889254295:AAFh8bYuFP5qty19cpP7HMFlPZ39lMNiU80"
bot = telebot.TeleBot(BOT_TOKEN)

# Game state store karne ke liye dictionary
games = {}

def get_empty_board():
    return [" "] * 9

def create_board_markup(board):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(9):
        text = board[i] if board[i] != " " else "⬜"
        callback = f"move_{i}"
        buttons.append(types.InlineKeyboardButton(text=text, callback_data=callback))
    markup.add(*buttons)
    return markup

def check_winner(board):
    win_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for combo in win_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return board[combo[0]]
    if " " not in board:
        return "Draw"
    return None

@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    chat_id = message.chat.id
    games[chat_id] = {
        'board': get_empty_board(),
        'turn': '❌'
    }
    markup = create_board_markup(games[chat_id]['board'])
    bot.send_message(
        chat_id,
        "🎮 Tic-Tac-Toe Game Shuru Ho Gaya!\nTurn: ❌",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('move_'))
def handle_move(call):
    chat_id = call.message.chat.id

    if chat_id not in games:
        bot.answer_callback_query(call.id, "Naya game start karne ke liye /game likhein.")
        return

    index = int(call.data.split('_')[1])
    game = games[chat_id]
    board = game['board']
    turn = game['turn']

    if board[index] != " ":
        bot.answer_callback_query(call.id, "Yeh cell pehle se bhara hua hai!")
        return

    # Move update karein
    board[index] = turn
    result = check_winner(board)

    if result:
        markup = create_board_markup(board)
        if result == "Draw":
            text = "🤝 Match Draw ho gaya! Dobara khelne ke liye /game likhein."
        else:
            text = f"🎉 Player {result} Jeet Gaya! Dobara khelne ke liye /game likhein."
        
        del games[chat_id]
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, "Game Khatam!")
    else:
        # Turn switch karein
        game['turn'] = '⭕' if turn == '❌' else '❌'
        markup = create_board_markup(board)
        bot.edit_message_text(
            f"🎮 Tic-Tac-Toe\nTurn: {game['turn']}",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)

if __name__ == "__main__":
    print("Bot chalu hai...")
    bot.infinity_polling()
