import telebot

# Oyaage API Token eka
API_TOKEN = '8256549699:AAEYpBcA3GCG5ATs7A7VOjkVmaVIko9-krY'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to RESELLERS KEY BOT!\nMama dan online wada.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Oya kiwwe: {message.text}")

bot.infinity_polling()
