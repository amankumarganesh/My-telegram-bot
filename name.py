import os
import random
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ----------------- 1. Render Keep-Alive Server -----------------
app = Flask('')


@app.route('/')
def home():
  return 'Telegram Bot is Online and Running!'


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.daemon = True
  t.start()


keep_alive()

# ----------------- 2. Bot Initialization -----------------
BOT_TOKEN = os.environ.get(
    'BOT_TOKEN', '8889254295:AAFh8bYuFP5qty19cpP7HMFlPZ39lMNiU80'
)
bot = telebot.TeleBot(BOT_TOKEN)

# Games Storage
ttt_games = {}
guess_games = {}
bb_games = {}
pop_games = {}

# ----------------- 3. Balloon Pop / Shooter Game -----------------
BALLOON_TYPES = [
    {'icon': '🎈', 'name': 'गुब्बारा', 'pts': 10, 'type': 'normal'},
    {'icon': '🎈', 'name': 'गुब्बारा', 'pts': 10, 'type': 'normal'},
    {'icon': '⭐', 'name': 'गोल्डन स्टार', 'pts': 30, 'type': 'bonus'},
    {'icon': '💣', 'name': 'बम', 'pts': -20, 'type': 'bomb'},
    {'icon': '💨', 'name': 'खाली', 'pts': 0, 'type': 'empty'},
]


def generate_pop_grid():
  return [random.choice(BALLOON_TYPES) for _ in range(9)]


def create_pop_markup(grid, score, shots_left, game_over=False):
  markup = types.InlineKeyboardMarkup(row_width=3)
  buttons = []
  for i, item in enumerate(grid):
    if game_over:
      btn_text = item['icon']
    else:
      btn_text = item['icon'] if item.get('revealed') else '🎯'
    buttons.append(
        types.InlineKeyboardButton(text=btn_text, callback_data=f'pop_hit_{i}')
    )

  for r in range(0, 9, 3):
    markup.row(*buttons[r : r + 3])

  markup.row(
      types.InlineKeyboardButton(
          text='🔄 नया गेम शुरू करें', callback_data='pop_restart'
      )
  )
  return markup


@bot.message_handler(commands=['pop', 'balloon', 'balloonshooter'])
def start_balloon_game(message):
  chat_id = message.chat.id
  grid = generate_pop_grid()
  pop_games[chat_id] = {
      'grid': grid,
      'score': 0,
      'shots_left': 6,
      'game_over': False,
  }
  markup = create_pop_markup(grid, 0, 6)
  bot.send_message(
      chat_id,
      '🎈 **Balloon Pop Shooter शुरू हो गया!** 🎯\n\n'
      '• 🎯 पर क्लिक करके गुब्बारा फोड़ो!\n'
      '• 🎈 गुब्बारा = +10 अंक\n'
      '• ⭐ स्टार = +30 अंक\n'
      '• 💣 बम = -20 अंक और गेम ओवर!\n\n'
      '🏹 **निशाने बचे:** 6 | 🏆 **स्कोर:** 0',
      reply_markup=markup,
      parse_mode='Markdown',
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith('pop_'))
def handle_balloon_action(call):
  chat_id = call.message.chat.id
  if chat_id not in pop_games:
    bot.answer_callback_query(
        call.id, 'नया गेम खेलने के लिए /pop टाइप करें दोस्त!'
    )
    return

  game = pop_games[chat_id]
  data = call.data

  if data == 'pop_restart':
    grid = generate_pop_grid()
    game['grid'] = grid
    game['score'] = 0
    game['shots_left'] = 6
    game['game_over'] = False
    markup = create_pop_markup(grid, 0, 6)
    bot.edit_message_text(
        '🎈 **नया Balloon Pop Game!**\n🏹 **निशाने बचे:** 6 | 🏆 **स्कोर:** 0',
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown',
    )
    bot.answer_callback_query(call.id, 'नया गेम तैयार!')
    return

  if game['game_over']:
    bot.answer_callback_query(
        call.id, 'गेम खत्म हो चुका है! रीस्टार्ट बटन दबाएं।'
    )
    return

  idx = int(data.split('_')[2])
  item = game['grid'][idx]

  if item.get('revealed'):
    bot.answer_callback_query(call.id, 'यह जगह पहले ही फोड़ चुके हैं!')
    return

  item['revealed'] = True
  game['shots_left'] -= 1

  alert_text = ''
  if item['type'] == 'bomb':
    game['score'] += item['pts']
    game['game_over'] = True
    alert_text = '💥 बूम! बम फूट गया! (-20 अंक)'
  elif item['type'] == 'bonus':
    game['score'] += item['pts']
    alert_text = '⭐ लकी स्टार! +30 अंक!'
  elif item['type'] == 'normal':
    game['score'] += item['pts']
    alert_text = '🎈 गुब्बारा फूट गया! +10 अंक!'
  else:
    alert_text = '💨 खाली निकला!'

  if game['shots_left'] <= 0:
    game['game_over'] = True

  if game['game_over']:
    msg = (
        f"🏁 **गेम समाप्त!**\n{alert_text}\n🏆 **अंतिम स्कोर:** {game['score']}\n"
        'दोबारा खेलने के लिए नीचे बटन दबाएं।'
    )
  else:
    msg = (
        f'🎈 **Balloon Pop Shooter!**\n{alert_text}\n'
        f"🏹 **निशाने बचे:** {game['shots_left']} | 🏆 **स्कोर:** {game['score']}"
    )

  markup = create_pop_markup(
      game['grid'], game['score'], game['shots_left'], game['game_over']
  )
  bot.edit_message_text(
      msg,
      chat_id=chat_id,
      message_id=call.message.message_id,
      reply_markup=markup,
      parse_mode='Markdown',
  )
  bot.answer_callback_query(call.id, alert_text)


# ----------------- 4. Block Blast Game -----------------
BLOCK_SHAPES = [
    {'name': '🟩 1x1', 'size': 1, 'pts': 10},
    {'name': '🟧 1x2', 'size': 2, 'pts': 20},
    {'name': '🟨 1x3', 'size': 3, 'pts': 30},
    {'name': '🟦 2x2', 'size': 4, 'pts': 40},
]


def create_bb_markup(grid, score, available_blocks):
  markup = types.InlineKeyboardMarkup(row_width=4)
  grid_buttons = []
  for i in range(16):
    text = '🟩' if grid[i] == 1 else '⬜'
    grid_buttons.append(
        types.InlineKeyboardButton(text=text, callback_data=f'bb_grid_{i}')
    )

  for r in range(0, 16, 4):
    markup.row(*grid_buttons[r : r + 4])

  block_buttons = []
  for idx, block in enumerate(available_blocks):
    block_buttons.append(
        types.InlineKeyboardButton(
            text=f"{block['name']} (+{block['pts']})",
            callback_data=f'bb_place_{idx}',
        )
    )
  if block_buttons:
    markup.row(*block_buttons)

  markup.row(
      types.InlineKeyboardButton(
          text='🔄 New Game', callback_data='bb_restart'
      )
  )
  return markup


def clear_lines(grid):
  lines_cleared = 0
  for r in range(4):
    if all(grid[r * 4 + c] == 1 for c in range(4)):
      lines_cleared += 1
      for c in range(4):
        grid[r * 4 + c] = 0
  for c in range(4):
    if all(grid[r * 4 + c] == 1 for r in range(4)):
      lines_cleared += 1
      for r in range(4):
        grid[r * 4 + c] = 0
  return lines_cleared * 100


@bot.message_handler(commands=['blast', 'blockblast'])
def start_block_blast(message):
  chat_id = message.chat.id
  blocks = random.sample(BLOCK_SHAPES, 2)
  bb_games[chat_id] = {
      'grid': [0] * 16,
      'score': 0,
      'blocks': blocks,
      'selected': None,
  }
  markup = create_bb_markup([0] * 16, 0, blocks)
  bot.send_message(
      chat_id,
      '💥 **Block Blast गेम शुरू हो गया!**\n\n'
      '• नीचे से ब्लॉक चुनें और ग्रिड (⬜) पर लगाएं।\n'
      '• पूरी लाइन भरने पर 100 बोनस पॉइंट्स मिलेंगे!\n'
      '🏆 **Score:** 0',
      reply_markup=markup,
      parse_mode='Markdown',
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith('bb_'))
def handle_block_blast_action(call):
  chat_id = call.message.chat.id
  if chat_id not in bb_games:
    bot.answer_callback_query(call.id, 'नया गेम शुरू करने के लिए /blast दबाएं।')
    return

  game = bb_games[chat_id]
  data = call.data

  if data == 'bb_restart':
    game['grid'] = [0] * 16
    game['score'] = 0
    game['blocks'] = random.sample(BLOCK_SHAPES, 2)
    game['selected'] = None
    markup = create_bb_markup(game['grid'], game['score'], game['blocks'])
    bot.edit_message_text(
        '💥 **Block Blast New Game!**\n🏆 **Score:** 0',
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown',
    )
    bot.answer_callback_query(call.id, 'New Game Started!')
    return

  if data.startswith('bb_place_'):
    idx = int(data.split('_')[2])
    game['selected'] = idx
    bot.answer_callback_query(
        call.id,
        f"चुना गया: {game['blocks'][idx]['name']}! अब खाली ⬜ ब्लॉक पर दबाएं।",
    )
    return

  if data.startswith('bb_grid_'):
    cell = int(data.split('_')[2])
    if game['selected'] is None:
      bot.answer_callback_query(
          call.id, '⚠️ पहले नीचे से कोई ब्लॉक सेलेक्ट करें!'
      )
      return

    if game['grid'][cell] == 1:
      bot.answer_callback_query(call.id, '⚠️ यह जगह पहले से भरी है!')
      return

    block = game['blocks'].pop(game['selected'])
    game['selected'] = None
    game['grid'][cell] = 1
    game['score'] += block['pts']

    bonus = clear_lines(game['grid'])
    game['score'] += bonus

    if not game['blocks']:
      game['blocks'] = random.sample(BLOCK_SHAPES, 2)

    msg = f'💥 **Block Blast!**\n'
    if bonus > 0:
      msg += f'🔥 **LINE BLAST! +{bonus} Bonus!**\n'
    msg += f"🏆 **Score:** {game['score']}"

    markup = create_bb_markup(game['grid'], game['score'], game['blocks'])
    bot.edit_message_text(
        msg,
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown',
    )
    bot.answer_callback_query(call.id)


# ----------------- 5. Tic-Tac-Toe Game -----------------
def get_empty_board():
  return [' '] * 9


def create_board_markup(board):
  markup = types.InlineKeyboardMarkup(row_width=3)
  buttons = []
  for i in range(9):
    text = board[i] if board[i] != ' ' else '⬜'
    buttons.append(
        types.InlineKeyboardButton(text=text, callback_data=f'ttt_{i}')
    )
  markup.add(*buttons)
  return markup


def check_winner(board):
  win_combos = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
  ]
  for combo in win_combos:
    if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
      return board[combo[0]]
  if ' ' not in board:
    return 'Draw'
  return None


@bot.message_handler(commands=['game', 'tictactoe'])
def start_tictactoe(message):
  chat_id = message.chat.id
  ttt_games[chat_id] = {'board': get_empty_board(), 'turn': '❌'}
  markup = create_board_markup(ttt_games[chat_id]['board'])
  bot.send_message(
      chat_id,
      '🎮 Tic-Tac-Toe शुरू हो गया दोस्त!\nतुम्हारी चाल: ❌',
      reply_markup=markup,
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_'))
def handle_tictactoe_move(call):
  chat_id = call.message.chat.id
  if chat_id not in ttt_games:
    bot.answer_callback_query(call.id, 'नया गेम शुरू करने के लिए /game भेजें!')
    return

  index = int(call.data.split('_')[1])
  game = ttt_games[chat_id]
  board = game['board']
  turn = game['turn']

  if board[index] != ' ':
    bot.answer_callback_query(call.id, 'यह जगह भरी हुई है!')
    return

  board[index] = turn
  result = check_winner(board)

  if result:
    markup = create_board_markup(board)
    text = (
        '🤝 मैच ड्रॉ हो गया दोस्त!'
        if result == 'Draw'
        else f'🎉 प्लेयर {result} जीत गया!'
    )
    text += ' दोबारा खेलने के लिए /game भेजें।'
    del ttt_games[chat_id]
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )
    bot.answer_callback_query(call.id, 'खेल खत्म!')
  else:
    game['turn'] = '⭕' if turn == '❌' else '❌'
    markup = create_board_markup(board)
    bot.edit_message_text(
        f"🎮 Tic-Tac-Toe\nअगली चाल: {game['turn']}",
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )
    bot.answer_callback_query(call.id)


# ----------------- 6. Number Guess Game -----------------
@bot.message_handler(commands=['guess'])
def start_guess_game(message):
  chat_id = message.chat.id
  guess_games[chat_id] = random.randint(1, 20)
  bot.send_message(
      chat_id,
      '🎯 मैंने 1 से 20 के बीच एक नंबर सोचा है!\nनंबर लिखकर भेजो और बताओ कौन सा'
      ' है।',
  )


# ----------------- 7. Welcome & Help Command -----------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  name = message.from_user.first_name or 'भाई'
  welcome_msg = (
      f'🙏 नमस्ते {name} भाई! आपका दिल से बहुत स्वागत है।\n\n'
      '🎮 **मजेदार गेम्स खेलें:**\n'
      '• 🎈 Balloon Shooter 👉 /pop\n'
      '• 💥 Block Blast 👉 /blast\n'
      '• ❌ Tic-Tac-Toe 👉 /game\n'
      '• 🎯 Number Guess 👉 /guess\n\n'
      '📊 **हेल्प और एनालिसिस:**\n'
      '• कोडिंग, गिरावट (Market Fall), 40 का लेवल\n'
      '• कलर ट्रेडिंग (Color Trading) गाइड\n'
      '• मोटिवेशन और ज़िंदगी की बातें\n\n'
      'कुछ भी पूछना हो बस टाइप करके भेज दो दोस्त!'
  )
  bot.reply_to(message, welcome_msg)


# ----------------- 8. Smart Chat Handler -----------------
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
  chat_id = message.chat.id
  text = message.text.strip().lower() if message.text else ''
  name = message.from_user.first_name or 'दोस्त'

  # Number Guess Check
  if chat_id in guess_games and text.isdigit():
    num = int(text)
    secret = guess_games[chat_id]
    if num == secret:
      del guess_games[chat_id]
      bot.reply_to(
          message,
          f'🎉 सही पकड़े हैं {name} भाई! नंबर {secret} ही था! दोबारा खेलने के'
          ' लिए /guess दबाएं।',
      )
      return
    elif num < secret:
      bot.reply_to(message, f'थोड़ा बड़ा नंबर सोचो {name} भाई! 📈')
      return
    else:
      bot.reply_to(message, f'थोड़ा छोटा नंबर सोचो {name} भाई! 📉')
      return

  # Greetings
  if any(
      greet in text
      for greet in [
          'hi',
          'hello',
          'hey',
          'namaste',
          'pranam',
          'hlo',
          'ram ram',
          'kaise ho',
      ]
  ):
    reply = (
        f'अरे नमस्ते {name} भाई! ❤️\n\n'
        'सब बढ़िया? बताओ आज क्या नया चल रहा है? Balloon Pop (/pop) खेलना है या'
        ' ट्रेडिंग/कोडिंग पर बात करनी है?'
    )

  # Coding & Girawat / 40
  elif any(
      k in text
      for k in [
          'cod',
          'coding',
          'koding',
          'girawat',
          'girvat',
          'downfall',
          '40',
          'market',
      ]
  ):
    reply = (
        f'अरे {name} भाई, कोडिंग और मार्केट दोनों का हिसाब अपने पास है! 💻📉\n\n'
        '• **कोडिंग टिप:** लॉजिक मजबूत रखो और एरर से मत घबराओ।\n'
        '• **गिरावट और 40 लेवल:** जब भी गिरावट आए या चार्ट 40 के सपोर्ट पर आए,'
        ' स्टॉप-लॉस जरूर लगाओ। बिना सोचे-समझे ट्रेड मत लेना!\n'
        '• **धैर्य:** शांति से काम लोगे तो हमेशा जीतोगे!'
    )

  # Color Trading
  elif any(
      k in text
      for k in [
          'color',
          'colour',
          'kolor',
          'trad',
          'trading',
          'traid',
          'tradin',
          'red',
          'green',
      ]
  ):
    reply = (
        f'बिल्कुल {name} भाई, कलर ट्रेडिंग समझ लो 📈🎨:\n\n'
        '• इसमें रेड, ग्रीन और वॉयलेट पर प्रेडिक्शन होता है।\n'
        '• **वार्निंग:** यह बहुत हाई-रिस्क होता है, इसलिए लालच में आकर बड़ा पैसा'
        ' कभी न लगाएं।\n'
        '• हमेशा छोटे बजट और समझदारी से ही खेलें!'
    )

  # Life / Motivation
  elif any(
      k in text
      for k in ['zindagi', 'jindagi', 'life', 'jeevan', 'kismat', 'tension']
  ):
    reply = (
        f'सुनो {name} भाई, ज़िंदगी बहुत अनमोल है! ✨\n\n'
        'उतार-चढ़ाव तो लगे रहते हैं। बस सीखते रहो, मुस्कुराते रहो और मेहनत'
        ' करते रहो। तुम्हारा भाई हमेशा साथ है!'
    )

  # Balloon or pop mention
  elif any(k in text for k in ['pop', 'balloon', 'ballon', 'shooter', 'fodo']):
    reply = (
        f'🎈 अरे {name} भाई, गुब्बारे फोड़ने हैं? तुरंत /pop दबाओ और गेम शुरू'
        ' करो!'
    )

  # Fallback
  else:
    reply = (
        f'अरे {name} भाई, मुझे आपका मैसेज मिल गया! 😊\n\n'
        'आप कोडिंग, कलर ट्रेडिंग, गिरावट/40 पूछ सकते हैं या फिर गेम खेल सकते हैं:\n'
        '• /pop - Balloon Shooter\n'
        '• /blast - Block Blast\n'
        '• /game - Tic-Tac-Toe\n'
        '• /guess - Number Guessing'
    )

  bot.reply_to(message, reply)


# ----------------- 9. Polling Execution -----------------
if __name__ == '__main__':
  print('Telegram Bot is starting polling...')
  bot.infinity_polling()
