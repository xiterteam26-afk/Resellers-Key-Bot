import telebot
from telebot import types
import os
from flask import Flask
import threading
import time

# --- FLASK SERVER (For Render Keep-Alive) ---
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
# Inventory to store keys
keys_db = {p: {d: [] for d in products[p]} for p in products}

logged_users = {}

# --- START & LOGIN ---
@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id, "🔐 **XITER TEAM OFFICIAL**\n\nEnter Username:")
    bot.register_next_step_handler(msg, process_username)

def process_username(message):
    username = message.text
    msg = bot.send_message(message.chat.id, "🔒 Enter Password:")
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
        bot.send_message(message.chat.id, "❌ Login Failed! Type /start to retry.")

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Shop Products", "📊 My Wallet")
    if logged_users.get(message.chat.id) == "admin":
        markup.add("⚙️ Admin Panel")
    bot.send_message(message.chat.id, "✅ Welcome! Choose an option:", reply_markup=markup)

# --- ADMIN PANEL ---
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel(message):
    if logged_users.get(message.chat.id) != "admin": return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 Add Stock", "💰 Add Money")
    markup.add("➕ Add Reseller", "➖ Remove Reseller")
    markup.add("🔑 Change Admin Login", "🏠 Main Menu")
    bot.send_message(message.chat.id, "🛠 **ADMIN CONTROL CENTER**", reply_markup=markup)

# 1. ADD RESELLER
@bot.message_handler(func=lambda m: m.text == "➕ Add Reseller")
def add_reseller_start(message):
    if logged_users.get(message.chat.id) != "admin": return
    msg = bot.send_message(message.chat.id, "Enter NEW Reseller Username:")
    bot.register_next_step_handler(msg, add_reseller_pass)

def add_reseller_pass(message):
    new_user = message.text
    msg = bot.send_message(message.chat.id, f"Set Password for {new_user}:")
    bot.register_next_step_handler(msg, lambda m: add_reseller_final(m, new_user))

def add_reseller_final(message, new_user):
    data["resellers"][new_user] = {"password": message.text, "wallet": 0}
    bot.send_message(message.chat.id, f"✅ Reseller '{new_user}' added successfully!")

# 2. REMOVE RESELLER
@bot.message_handler(func=lambda m: m.text == "➖ Remove Reseller")
def remove_reseller_start(message):
    if logged_users.get(message.chat.id) != "admin": return
    msg = bot.send_message(message.chat.id, "Enter Reseller Username to REMOVE:")
    bot.register_next_step_handler(msg, remove_reseller_final)

def remove_reseller_final(message):
    user = message.text
    if user in data["resellers"]:
        del data["resellers"][user]
        bot.send_message(message.chat.id, f"✅ Reseller '{user}' removed!")
    else:
        bot.send_message(message.chat.id, "❌ Reseller not found!")

# 3. ADD MONEY
@bot.message_handler(func=lambda m: m.text == "💰 Add Money")
def add_money_start(message):
    if logged_users.get(message.chat.id) != "admin": return
    msg = bot.send_message(message.chat.id, "Enter Reseller Username:")
    bot.register_next_step_handler(msg, add_money_amount)

def add_money_amount(message):
    res_user = message.text
    if res_user in data["resellers"]:
        msg = bot.send_message(message.chat.id, f"Enter amount to add for {res_user}:")
        bot.register_next_step_handler(msg, lambda m: add_money_final(m, res_user))
    else:
        bot.send_message(message.chat.id, "❌ User not found!")

def add_money_final(message, res_user):
    try:
        amount = int(message.text)
        data["resellers"][res_user]["wallet"] += amount
        bot.send_message(message.chat.id, f"✅ Added Rs.{amount}. New Balance: Rs.{data['resellers'][res_user]['wallet']}")
    except:
        bot.send_message(message.chat.id, "❌ Invalid number!")

# 4. ADD STOCK (KEYS)
@bot.message_handler(func=lambda m: m.text == "📥 Add Stock")
def add_stock_cat(message):
    if logged_users.get(message.chat.id) != "admin": return
    markup = types.InlineKeyboardMarkup()
    for cat in products.keys():
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"as_{cat}"))
    bot.send_message(message.chat.id, "Select Category to add keys:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("as_"))
def add_stock_days(call):
    cat = call.data.replace("as_", "")
    markup = types.InlineKeyboardMarkup()
    for day in products[cat].keys():
        markup.add(types.InlineKeyboardButton(day, callback_data=f"askey_{cat}_{day}"))
    bot.edit_message_text(f"Select Duration for {cat}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("askey_"))
def add_stock_final_step(call):
    _, cat, day = call.data.split("_")
    msg = bot.send_message(call.message.chat.id, f"Send keys for {cat} {day} (One key per line):")
    bot.register_next_step_handler(msg, lambda m: save_keys(m, cat, day))

def save_keys(message, cat, day):
    new_keys = message.text.split('\n')
    keys_db[cat][day].extend(new_keys)
    bot.send_message(message.chat.id, f"✅ Successfully added {len(new_keys)} keys to {cat} {day}!")

@bot.message_handler(func=lambda m: m.text == "🏠 Main Menu")
def go_home(message):
    if message.chat.id in logged_users: show_main_menu(message)

# --- RUN ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    server.run(host="0.0.0.0", port=port)
