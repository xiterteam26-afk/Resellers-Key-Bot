import telebot
from telebot import types

# Oyaage Token eka
API_TOKEN = '8256549699:AAEYpBcA3GCG5ATs7A7VOjkVmaVIko9-krY'
bot = telebot.TeleBot(API_TOKEN)

# Login Details
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# Product List
products = [
    {"name": "Netflix 1 Month", "price": "Rs. 450"},
    {"name": "Youtube Premium", "price": "Rs. 250"}
]

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 View Products", "🔑 Admin Login")
    bot.send_message(message.chat.id, "Welcome to Reseller Bot! Thora ganna:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛒 View Products")
def show_prods(message):
    text = "📦 **Products List:**\n\n"
    for p in products:
        text += f"🔹 {p['name']} - {p['price']}\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔑 Admin Login")
def login(message):
    msg = bot.send_message(message.chat.id, "Admin Username eka gahanna:")
    bot.register_next_step_handler(msg, get_user)

def get_user(message):
    if message.text == ADMIN_USER:
        msg = bot.send_message(message.chat.id, "Password eka gahanna:")
        bot.register_next_step_handler(msg, get_pass)
    else:
        bot.send_message(message.chat.id, "Username waradiy!")

def get_pass(message):
    if message.text == ADMIN_PASS:
        bot.send_message(message.chat.id, "Welcome Admin! Oyaata dan products add karanna puluwan.")
    else:
        bot.send_message(message.chat.id, "Password waradiy!")

bot.infinity_polling()
