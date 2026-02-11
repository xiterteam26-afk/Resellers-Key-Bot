import telebot
from telebot import types

API_TOKEN = '8256549699:AAEYpBcA3GCG5ATs7A7VOjkVmaVIko9-krY'
bot = telebot.TeleBot(API_TOKEN)

# Admin details (Mewa oyaata ona widiyata wenas karanna)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

# Danata products save karanna list ekak (Passe meka database ekakata harawamu)
products = [
    {"id": 1, "name": "Netflix 1 Month", "price": "LKR 500"},
    {"id": 2, "name": "Youtube Premium", "price": "LKR 300"}
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('🛒 View Products')
    itembtn2 = types.KeyboardButton('🔑 Admin Login')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Welcome to XiterTeam Reseller Bot! \nThora ganna:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🛒 View Products')
def show_products(message):
    if not products:
        bot.send_message(message.chat.id, "Danata products naha.")
        return
    
    msg = "📦 **Available Products:**\n\n"
    for p in products:
        msg += f"ID: {p['id']} | {p['name']} - {p['price']}\n"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🔑 Admin Login')
def admin_login(message):
    msg = bot.send_message(message.chat.id, "Admin Username eka danna:")
    bot.register_next_step_handler(msg, process_username_step)

def process_username_step(message):
    if message.text == ADMIN_USERNAME:
        msg = bot.send_message(message.chat.id, "Password eka danna:")
        bot.register_next_step_handler(msg, process_password_step)
    else:
        bot.send_message(message.chat.id, "Username waradiy!")

def process_password_step(message):
    if message.text == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, "Welcome Admin! Oyaata dan products add karanna puluwan.")
        # Methana Admin panel eka hadanna puluwan
    else:
        bot.send_message(message.chat.id, "Password waradiy!")

bot.infinity_polling()
