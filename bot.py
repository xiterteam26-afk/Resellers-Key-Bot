import telebot
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '8256549699:AAElz0DJxLep_Lr51UWjmTdpmjrasDJ0EoY' # Oyaage aluth token eka
bot = telebot.TeleBot(API_TOKEN)

# Admin Credentials
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# Product Data (Temporary list)
products = [
    {"name": "Netflix 1 Month", "price": "Rs. 450"},
    {"name": "Youtube Premium", "price": "Rs. 250"}
]

# --- USER SIDE ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 View Products", "🔑 Admin Login")
    bot.send_message(message.chat.id, "👋 Welcome to XiterTeam Reseller Bot!\nOyaata avashya de thora ganna:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛒 View Products")
def show_prods(message):
    if not products:
        bot.send_message(message.chat.id, "📦 Danata products naha.")
        return
    
    text = "📦 **Available Products:**\n\n"
    for p in products:
        text += f"🔹 **{p['name']}** - {p['price']}\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- ADMIN LOGIN SIDE ---

@bot.message_handler(func=lambda m: m.text == "🔑 Admin Login")
def login(message):
    msg = bot.send_message(message.chat.id, "👤 Admin Username eka danna:")
    bot.register_next_step_handler(msg, get_user)

def get_user(message):
    if message.text == ADMIN_USER:
        msg = bot.send_message(message.chat.id, "🔒 Password eka danna:")
        bot.register_next_step_handler(msg, get_pass)
    else:
        bot.send_message(message.chat.id, "❌ Username waradiy!")

def get_pass(message):
    if message.text == ADMIN_PASS:
        admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        admin_markup.add("➕ Add Product", "🏠 Main Menu")
        bot.send_message(message.chat.id, "✅ Welcome Admin! Oyaata dan bot wa manage karanna puluwan.", reply_markup=admin_markup)
    else:
        bot.send_message(message.chat.id, "❌ Password waradiy!")

# --- ADMIN ACTIONS (ADD PRODUCT) ---

@bot.message_handler(func=lambda m: m.text == "➕ Add Product")
def add_product_start(message):
    msg = bot.send_message(message.chat.id, "📝 Product eke nama danna (e.g. Netflix):")
    bot.register_next_step_handler(msg, process_product_name)

def process_product_name(message):
    product_name = message.text
    msg = bot.send_message(message.chat.id, f"💰 {product_name} eke ganan danna (e.g. Rs. 500):")
    bot.register_next_step_handler(msg, lambda m: finalize_product(m, product_name))

def finalize_product(message, name):
    price = message.text
    products.append({"name": name, "price": price})
    bot.send_message(message.chat.id, f"✅ '{name}' product eka sarthakawa ekathu kala!")

@bot.message_handler(func=lambda m: m.text == "🏠 Main Menu")
def back_to_main(message):
    start(message)

# --- RUN BOT ---
print("Bot is running...")
bot.infinity_polling()
