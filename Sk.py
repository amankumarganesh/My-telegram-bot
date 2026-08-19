import telebot
from telebot import types

# Yahan apna Telegram Bot Token dalein
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
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
