import telebot
from telebot import types
import os
from flask import Flask
import threading

server = Flask(__name__)
@server.route("/")
def home(): return "Bot is Running!"

API_TOKEN = '8595603162:AAHRk4hN-txEc_uZtyEtFNxuGZ6VJ-s4X0U'
bot = telebot.TeleBot(API_TOKEN)

resellers = {"admin": {"password": "123", "wallet": 5000}} 
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

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔑 Reseller Login", "📊 My Wallet")
    markup.add("🛒 Shop Products")
    bot.send_message(message.chat.id, "💎 **XITER TEAM OFFICIAL BOT** 💎", reply_markup=markup, parse_mode="Markdown")

# --- ADMIN PANEL & ADD STOCK ---
@bot.message_handler(commands=['admin123'])
def admin(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 Add Stock", "🏠 Main Menu")
    bot.send_message(message.chat.id, "⚙️ **ADMIN PANEL**", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📥 Add Stock")
def add_stock_start(message):
    markup = types.InlineKeyboardMarkup()
    for item in stocks.keys():
        markup.add(types.InlineKeyboardButton(item, callback_data=f"add_{item}"))
    bot.send_message(message.chat.id, "Select Product to add keys:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def process_add_stock(call):
    product = call.data.replace("add_", "")
    msg = bot.send_message(call.message.chat.id, f"Enter Keys for **{product}** (Codes thunaka nam, thunama wenas peliyata type karala ewanna):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: save_keys(m, product))

def save_keys(message, product):
    new_keys = message.text.split('\n') # Hama line ekama aluth key ekak widiyata gannawa
    stocks[product]["keys"].extend(new_keys)
    bot.send_message(message.chat.id, f"✅ Successfully added {len(new_keys)} keys to {product}!")

# [Anith login saha shop logic tika mama kalin deepu widiyatama thiyanawa...]
# (Mama meka thawa loku wenna nisa login/shop part eka hemin liyanawa, oya full code eka kalin thibba ekatama me function eka add karaganna)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=bot.infinity_polling).start()
    server.run(host="0.0.0.0", port=port)
