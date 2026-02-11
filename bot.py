import telebot
from telebot import types
import os
from flask import Flask
import threading
import time

# --- FLASK SERVER (Keep-Alive) ---
server = Flask(__name__)
@server.route("/")
def home(): return "Bot is Online!"

# --- CONFIGURATION ---
API_TOKEN = '8218026043:AAHEM3gNJDO5H_kk6z-ixGC36HwRw55OcfY'
bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE ---
# Initialize with your default credentials
data = {
    "admin": {"user": "admin", "pass": "123"},
    "resellers": {
        "test": {"password": "123", "wallet": 5000}
    }
}

# Product Data
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
    "E sign": {"1 Year": {"price": 1800, "keys": []}},
    "Niro IOS": {"1 Month": {"price": 3200, "keys": []}}
}

logged_users = {} # Tracks who is logged in

# --- LOGIN SYSTEM ---
@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id, "🔐 **XITER TEAM OFFICIAL**\n\nPlease enter your Username:")
    bot.register_next_step_handler(msg, process_username)

def process_username(message):
    username = message.text
    msg = bot.send_message(message.chat.id, f"👤 User: {username}\nEnter Password:")
    bot.register_next_step_handler(msg, lambda m: process_password(m, username))

def process_password(message, username):
    password = message.text
    # Admin Check
    if username == data["admin"]["user"] and password == data["admin"]["pass"]:
        logged_users[message.chat.id] = "admin"
        show_main_menu(message)
    # Reseller Check
    elif username in data["resellers"] and data["resellers"][username]["password"] == password:
        logged_users[message.chat.id] = username
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ Login Failed! Invalid credentials. Type /start to retry.")

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Shop Products", "📊 My Wallet")
    if logged_users.get(message.chat.id) == "admin":
        markup.add("⚙️ Admin Panel")
    bot.send_message(message.chat.id, "✅ Access Granted. Welcome to XITER TEAM.", reply_markup=markup)

# --- SHOP LOGIC ---
@bot.message_handler(func=lambda m: m.text == "🛒 Shop Products")
def shop_categories(message):
    if message.chat.id not in logged_users: return
    markup = types.InlineKeyboardMarkup()
    for cat in products.keys():
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.send_message(message.chat.id, "📦 Select Category:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def shop_days(call):
    cat = call.data.replace("cat_", "")
    markup = types.InlineKeyboardMarkup()
    for day, info in products[cat].items():
        markup.add(types.InlineKeyboardButton(f"{day} - Rs.{info['price']}", callback_data=f"buy_{cat}_{day}"))
    bot.edit_message_text(f"💎 {cat} - Select Duration:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def complete_buy(call):
    _, cat, day = call.data.split("_")
    user = logged_users.get(call.message.chat.id)
    price = products[cat][day]["price"]
    
    if user == "admin" or (user in data["resellers"] and data["resellers"][user]["wallet"] >= price):
        if products[cat][day]["keys"]:
            key = products[cat][day]["keys"].pop(0)
            if user != "admin": data["resellers"][user]["wallet"] -= price
            bot.send_message(call.message.chat.id, f"✅ Success!\n🎁 {cat} ({day})\n🔑 Key: `{key}`", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Out of Stock!")
    else:
        bot.answer_callback_query(call.id, f"❌ Insufficient Balance! (Price: Rs.{price})")

# --- ADMIN PANEL ---
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel(message):
    if logged_users.get(message.chat.id) != "admin": return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 Add Stock", "💰 Add Money")
    markup.add("➕ Add Reseller", "➖ Remove Reseller")
    markup.add("🔑 Change Admin Login", "🏠 Main Menu")
    bot.send_message(message.chat.id, "🛠 **ADMIN CONTROL CENTER**", reply_markup=markup)

# Admin Credential Change
@bot.message_handler(func=lambda m: m.text == "🔑 Change Admin Login")
def change_admin_start(message):
    msg = bot.send_message(message.chat.id, "Enter NEW Admin Username:")
    bot.register_next_step_handler(msg, change_admin_user)

def change_admin_user(message):
    new_user = message.text
    msg = bot.send_message(message.chat.id, f"New User: {new_user}\nEnter NEW Admin Password:")
    bot.register_next_step_handler(msg, lambda m: change_admin_final(m, new_user))

def change_admin_final(message, new_user):
    data["admin"]["user"] = new_user
    data["admin"]["pass"] = message.text
    bot.send_message(message.chat.id, "✅ Admin credentials updated successfully!")

@bot.message_handler(func=lambda m: m.text == "📊 My Wallet")
def check_wallet(message):
    user = logged_users.get(message.chat.id)
    if user == "admin":
        bot.send_message(message.chat.id, "💰 Wallet: Unlimited (Admin)")
    else:
        bal = data["resellers"][user]["wallet"]
        bot.send_message(message.chat.id, f"💰 Your Balance: Rs. {bal}")

# --- STARTUP ---
if __name__ == "__main__":
    # Fix for 409 Conflict: Clear previous session
    bot.remove_webhook()
    time.sleep(1)
    
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    server.run(host="0.0.0.0", port=port)
