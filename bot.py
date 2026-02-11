import telebot
from telebot import types

API_TOKEN = '8256549699:AAElz0DJxLep_Lr51UWjmTdpmjrasDJ0EoY'
bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE (Temporary) ---
# Reality eke meka file ekaka save wenna ona, danata mehema hadamu
resellers = {
    "testuser": {"password": "123", "wallet": 5000} # Udaharanayak
}

# Stock management
stocks = {
    "Fluorite 1 Day": {"price": 750, "keys": []},
    "Fluorite 7 Days": {"price": 2100, "keys": []},
    "Fluorite 31 Days": {"price": 3700, "keys": []},
    "E sign 1 Year": {"price": 1800, "keys": []},
    "Drip 1 Day": {"price": 420, "keys": []},
    "Drip 7 Days": {"price": 1000, "keys": []},
    "Drip 15 Days": {"price": 1700, "keys": []},
    "Drip 30 Days": {"price": 2250, "keys": []},
    "HG 15 Days": {"price": 1150, "keys": []},
    "HG 30 Days": {"price": 2350, "keys": []},
    "NIRO IOS": {"price": 3200, "keys": []}
}

current_reseller = {} # Logged in tracking

# --- MAIN MENU ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔑 Reseller Login", "📊 My Wallet")
    markup.add("🛒 Shop Products")
    bot.send_message(message.chat.id, "💎 OFFICIAL RESELLING BOT 💎\nThora ganna:", reply_markup=markup)

# --- LOGIN SYSTEM ---
@bot.message_handler(func=lambda m: m.text == "🔑 Reseller Login")
def login(message):
    msg = bot.send_message(message.chat.id, "👤 Username eka danna:")
    bot.register_next_step_handler(msg, auth_user)

def auth_user(message):
    user = message.text
    if user in resellers:
        msg = bot.send_message(message.chat.id, "🔒 Password eka danna:")
        bot.register_next_step_handler(msg, lambda m: auth_pass(m, user))
    else:
        bot.send_message(message.chat.id, "❌ Reseller kenek hoyaganna baha!")

def auth_pass(message, user):
    if message.text == resellers[user]["password"]:
        current_reseller[message.chat.id] = user
        bot.send_message(message.chat.id, f"✅ Welcome {user}! Oya dan logged in.")
    else:
        bot.send_message(message.chat.id, "❌ Password waradiy!")

# --- SHOP & WALLET ---
@bot.message_handler(func=lambda m: m.text == "📊 My Wallet")
def check_wallet(message):
    user = current_reseller.get(message.chat.id)
    if user:
        balance = resellers[user]["wallet"]
        bot.send_message(message.chat.id, f"💰 Oyaage Wallet Balance: Rs. {balance}")
    else:
        bot.send_message(message.chat.id, "⚠️ Palamuwanma Login wenna.")

@bot.message_handler(func=lambda m: m.text == "🛒 Shop Products")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for item, data in stocks.items():
        markup.add(types.InlineKeyboardButton(f"{item} - Rs.{data['price']}", callback_data=f"buy_{item}"))
    bot.send_message(message.chat.id, "📦 Avashya Product eka select karanna:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    item_name = call.data.replace("buy_", "")
    user = current_reseller.get(call.message.chat.id)
    
    if not user:
        bot.answer_callback_query(call.id, "⚠️ Login wenna!")
        return

    price = stocks[item_name]["price"]
    if resellers[user]["wallet"] >= price:
        if stocks[item_name]["keys"]:
            key = stocks[item_name]["keys"].pop(0)
            resellers[user]["wallet"] -= price
            bot.send_message(call.message.chat.id, f"✅ Purchase Success!\n🎁 {item_name} Key: `{key}`", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Out of Stock!")
    else:
        bot.answer_callback_query(call.id, "❌ Salli madiy!")

# --- SECRET ADMIN PANEL ---
@bot.message_handler(commands=['admin123']) # Meka oyaage secret command eka
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Reseller", "📥 Add Stock", "🏠 Main Menu")
    bot.send_message(message.chat.id, "⚙️ ADMIN PANEL ACTIVE", reply_markup=markup)

# Admin logic thawa hadanna puluwan...
bot.infinity_polling()
