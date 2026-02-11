import telebot
from telebot import types
import os
from flask import Flask
import threading
import time

# --- FLASK SERVER (Render ekata) ---
server = Flask(__name__)
@server.route("/")
def home(): return "XITER TEAM BOT IS ONLINE"

# --- CONFIGURATION ---
API_TOKEN = '8218026043:AAHEM3gNJDO5H_kk6z-ixGC36HwRw55OcfY'
bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE ---
data = {
    "admin": {"user": "admin", "pass": "123"},
    "resellers": {
        "test": {"password": "123", "wallet": 5000}
    }
}

products = {
    "Fluorite": {"1 Day": 750, "7 Days": 2100, "31 Days": 3700},
    "Drip Client": {"1 Day": 420, "7 Days": 1000, "15 Days": 1700, "30 Days": 2250},
    "Hg cheats": {"10 Days": 1200, "30 Days": 2400},
    "E sign": {"1 Year": 1800},
    "Niro IOS": {"1 Month": 3200}
}
keys_db = {p: {d: [] for d in products[p]} for p in products}

# Logged users check karanna
logged_users = {} 

# --- LOGIN CHECKER FUNCTION ---
def check_session(message):
    if message.chat.id in logged_users:
        return True
    bot.send_message(message.chat.id, "⚠️ **Session Expired!**\nKaruṇākara ayeth /start gahalā login wenna.")
    return False

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id, "🔐 **XITER TEAM OFFICIAL**\n\nUsername eka danna:")
    bot.register_next_step_handler(msg, process_username)

def process_username(message):
    username = message.text
    msg = bot.send_message(message.chat.id, "🔒 Password eka danna:")
    bot.register_next_step_handler(msg, lambda m: process_password(m, username))

def process_password(message, username):
    password = message.text
    if username == data["admin"]["user"] and password == data["admin"]["pass"]:
        logged_users[message.chat.id] = "admin"
        show_main_menu(message)
    elif username in data["resellers"] and data["resellers"][username]["password"] == password:
        logged_users[message.chat.id] = username
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ Login Failed! Username ho Password waradi.")

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Shop Products", "📊 My Wallet")
    if logged_users.get(message.chat.id) == "admin":
        markup.add("⚙️ Admin Panel")
    bot.send_message(message.chat.id, "✅ Login una! Pahala buttons pawaichchi karanna.", reply_markup=markup)

# --- WALLET BUTTON ---
@bot.message_handler(func=lambda m: m.text == "📊 My Wallet")
def check_wallet(message):
    if not check_session(message): return
    
    user = logged_users[message.chat.id]
    if user == "admin":
        bot.send_message(message.chat.id, "💰 Wallet: Unlimited (Admin)")
    else:
        balance = data["resellers"][user]["wallet"]
        bot.send_message(message.chat.id, f"💰 Oyaage Balance eka: Rs. {balance}")

# --- SHOP BUTTON ---
@bot.message_handler(func=lambda m: m.text == "🛒 Shop Products")
def shop_categories(message):
    if not check_session(message): return
    
    markup = types.InlineKeyboardMarkup()
    for cat in products.keys():
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.send_message(message.chat.id, "📦 Category ekak thoranna:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def shop_days(call):
    cat = call.data.replace("cat_", "")
    markup = types.InlineKeyboardMarkup()
    for day, price in products[cat].items():
        markup.add(types.InlineKeyboardButton(f"{day} - Rs.{price}", callback_data=f"buy_{cat}_{day}"))
    bot.edit_message_text(f"💎 {cat} - Kalaya thoranna:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- ADMIN PANEL ---
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel(message):
    if not check_session(message): return
    if logged_users[message.chat.id] != "admin": return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 Add Stock", "💰 Add Money")
    markup.add("➕ Add Reseller", "🔑 Change Admin Login")
    markup.add("🏠 Main Menu")
    bot.send_message(message.chat.id, "🛠 **ADMIN PANEL**", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🏠 Main Menu")
def back_home(message):
    if check_session(message): show_main_menu(message)

# --- RUN ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    server.run(host="0.0.0.0", port=port)
