# TOKEN = ''
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = '7765094995:AAFxubX32mdHJ3eSR_3m4_IyycyK7GSqRCo'
bot = telebot.TeleBot(TOKEN)

# Global dictionary to store user states: {user_id: {'target': target_id, 'anonymous': bool}}
user_states = {}


@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()[1:]  # Get arguments after /start
    if args and args[0].startswith('anon_'):
        try:
            owner_id = int(args[0].split('_')[1])
            owner = bot.get_chat(owner_id)
            owner_username = owner.username if owner.username else f"User {owner_id}"

            # Set state for this user (sender)
            user_states[message.from_user.id] = {'target': owner_id, 'anonymous': False}

            bot.reply_to(message, f"لطفا پیام ناشناس خود را برای @{owner_username} بفرستید.")
        except ValueError:
            bot.reply_to(message, "لینک نامعتبر است.")
    else:
        # Show inline keyboard for creating link
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("ساخت لینک ناشناس", callback_data='create_link'))
        bot.send_message(message.chat.id, "برای ساخت لینک ناشناس، روی دکمه زیر کلیک کنید:", reply_markup=markup)


@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
        bot.reply_to(message, "حالت گفتگو لغو شد.")
    else:
        bot.reply_to(message, "شما در حال حاضر در هیچ حالتی نیستید.")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'create_link':
        user_id = call.from_user.id
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start=anon_{user_id}"
        bot.answer_callback_query(call.id, "لینک ساخته شد!")
        bot.send_message(call.message.chat.id,
                         f"لینک ناشناس شما: {link}\nهر کسی که روی این لینک کلیک کند، می‌تواند پیام ناشناس برای شما بفرستد.")
    elif call.data.startswith('reply_to_'):
        sender_id = int(call.data.split('_')[2])
        # Set state for owner to reply anonymously to sender
        user_states[call.from_user.id] = {'target': sender_id, 'anonymous': True}
        bot.answer_callback_query(call.id, "حالا می‌توانید پیام ناشناس بفرستید.")
        bot.send_message(call.message.chat.id,
                         "پیام خود را وارد کنید تا به صورت ناشناس ارسال شود. برای خروج، /cancel بزنید.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id in user_states:
        state = user_states[user_id]
        target_id = state['target']

        if state['anonymous']:
            # Owner sending anonymous reply to sender
            bot.send_message(target_id, f"\n{message.text}")
            bot.reply_to(message, "پیام شما ارسال شد.")
        else:
            # Sender sending message to owner with username
            sender_username = message.from_user.username if message.from_user.username else "Anonymous"

            # Prepare reply markup for owner to reply
            reply_markup = InlineKeyboardMarkup()
            reply_markup.add(InlineKeyboardButton("پاسخ ناشناس", callback_data=f"reply_to_{user_id}"))

            bot.send_message(target_id, f"پیام ناشناس از @{sender_username}:\n{message.text}",
                             reply_markup=reply_markup)
            bot.reply_to(message, "پیام شما ارسال شد.")
    else:
        bot.reply_to(message, "برای شروع، /start را بزنید.")


bot.infinity_polling()