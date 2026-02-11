import telebot
from telebot import types
import os
from flask import Flask
import threading

# --- FLASK SERVER (For Render Free Tier) ---
server = Flask(__name__)
@server.route("/")
def home(): return "Bot is Online!"

# --- CONFIGURATION ---
API_TOKEN = '8595603162:AAHRk4hN-txEc_uZtyEtFNxuGZ6VJ-s4X0U'
bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE ---
admin_user = {"user": "admin", "pass": "123"}
resellers = {"test": {"password": "123", "wallet": 5000}}

# Updated Price List & Days
products = {
    "Fluorite": {
        "1 Day": {"price": 750, "keys": []},
        "7 Days": {"price": 2100, "keys": []},
        "31 Days": {"price": 3700, "keys": []}
    },
    "Drip Client": {
        "1 Day": {"price": 420, "keys": []},
        "7 Days": {"price": 1000, "keys": []},
        "15 Days": {"price": 1700, "keys": []},
        "30 Days": {"price": 2250, "keys": []}
    },
    "Hg cheats": {
        "10 Days": {"price": 1200, "keys": []},
        "30 Days": {"price": 2400, "keys": []}
    },
    "E sign": {
        "1 Year": {"price": 1800, "keys": []}
    },
    "Niro IOS": {
        "1 Month": {"price": 3200, "keys": []}
    }
}

logged_users = {}

# --- LOGIN SYSTEM ---
@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id, "🔐 **XITER TEAM BOT**\n\nKaruṇākara Username eka danna:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_username)

def process_username(message):
    username = message.text
    msg = bot.send_message(message.chat.id, f"👤 User: {username}\nPassword eka danna:")
    bot.register_next_step_handler(msg, lambda m: process_password(m, username))

def process_password(message, username):
    password = message.text
    if (username == admin_user["user"] and password == admin_user["pass"]) or \
       (username in resellers and resellers[username]["password"] == password):
        logged_users[message.chat.id] = username
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ Login Failed! /start karanna.")

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Shop Products", "📊 My Wallet")
    if logged_users.get(message.chat.id) == admin_user["user"]:
        markup.add("⚙️ Admin Panel")
    bot.send_message(message.chat.id, "✅ Welcome back!", reply_markup=markup)

# --- SHOP LOGIC ---
@bot.message_handler(func=lambda m: m.text == "🛒 Shop Products")
def shop_categories(message):
    if message.chat.id not in logged_users: return
    markup = types.InlineKeyboardMarkup()
    for cat in products.keys():
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.send_message(message.chat.id, "📦 Select Product Category:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def shop_days(call):
    cat = call.data.replace("cat_", "")
    markup = types.InlineKeyboardMarkup()
    for day, data in products[cat].items():
        markup.add(types.InlineKeyboardButton(f"{day} - Rs.{data['price']}", callback_data=f"buy_{cat}_{day}"))
    bot.edit_message_text(f"💎 {cat} - Select Duration:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def complete_buy(call):
    _, cat, day = call.data.split("_")
    user = logged_users.get(call.message.chat.id)
    price = products[cat][day]["price"]
    
    if user == admin_user["user"] or resellers[user]["wallet"] >= price:
        if products[cat][day]["keys"]:
            key = products[cat][day]["keys"].pop(0)
            if user != admin_user["user"]: resellers[user]["wallet"] -= price
            bot.send_message(call.message.chat.id, f"✅ Purchase Success!\n🎁 {cat} {day}\n🔑 Key: `{key}`", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Out of Stock!")
    else:
        bot.answer_callback_query(call.id, f"❌ Salli madiy! Price: Rs.{price}")

# --- ADMIN PANEL ---
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel(message):
    if logged_users.get(message.chat.id) != admin_user["user"]: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Reseller", "💰 Add Money")
    markup.add("📥 Add Stock", "🏠 Main Menu")
    bot.send_message(message.chat.id, "🛠 **ADMIN CONTROL CENTER**", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 My Wallet")
def check_wallet(message):
    user = logged_users.get(message.chat.id)
    if user == admin_user["user"]:
        bot.send_message(message.chat.id, "💰 Wallet: ∞ (Admin)")
    elif user in resellers:
        bot.send_message(message.chat.id, f"💰 Wallet Balance: Rs. {resellers[user]['wallet']}")

# --- RUNNING ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=bot.infinity_polling).start()
    server.run(host="0.0.0.0", port=port)
