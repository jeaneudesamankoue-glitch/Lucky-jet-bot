import os
import telebot
from telebot import types
import random

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

bankroll_depart = 10000
user_data = {}

def get_user(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {"bankroll": bankroll_depart, "mise_base": 200, "pertes_suite": 0}
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎯 PREDICTION", "💰 MA BANKROLL")
    markup.add("📊 HISTORIQUE", "⚙️ REGLER MISE")
    bot.send_message(message.chat.id, f"🚀 Salut!\n\nLucky Jet Assistant prêt.\n\n💰 Bankroll: {user['bankroll']} FCFA", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎯 PREDICTION")
def prediction(message):
    user = get_user(message.chat.id)
    choix = random.choices(["COTE SURE (1.20 - 1.50)", "COTE MOYENNE (1.80 - 2.50)", "ATTENDRE - NE PAS JOUER"], weights=[50, 30, 20])[0]
    if choix == "ATTENDRE - NE PAS JOUER":
        bot.send_message(message.chat.id, f"🛑 ATTENDRE ce tour\nBankroll: {user['bankroll']} FCFA")
    else:
        mise = user['mise_base'] * (2 ** user['pertes_suite'])
        bot.send_message(message.chat.id, f"🎯 SIGNAL\n\n{choix}\n💵 Mise: {int(mise)} FCFA\nBankroll: {user['bankroll']} FCFA")

@bot.message_handler(func=lambda m: m.text == "💰 MA BANKROLL")
def bankroll(message):
    user = get_user(message.chat.id)
    bot.send_message(message.chat.id, f"💰 BANKROLL: {user['bankroll']} FCFA")

@bot.message_handler(func=lambda m: m.text == "📊 HISTORIQUE")
def histo(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Gagné", callback_data="gagne"), types.InlineKeyboardButton("❌ Perdu", callback_data="perdu"))
    markup.add(types.InlineKeyboardButton("🔄 Reset", callback_data="reset"))
    bot.send_message(message.chat.id, "Dernier tour?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user = get_user(call.message.chat.id)
    if call.data == "gagne":
        user['bankroll'] += user['mise_base']
        user['pertes_suite'] = 0
        bot.send_message(call.message.chat.id, f"✅ Gagné! {user['bankroll']} FCFA")
    elif call.data == "perdu":
        mise = user['mise_base'] * (2 ** user['pertes_suite'])
        user['bankroll'] -= mise
        user['pertes_suite'] += 1
        bot.send_message(call.message.chat.id, f"❌ Perdu. {user['bankroll']} FCFA")
    elif call.data == "reset":
        user['bankroll'] = bankroll_depart
        user['pertes_suite'] = 0
        bot.send_message(call.message.chat.id, f"🔄 Reset: {bankroll_depart} FCFA")

@bot.message_handler(func=lambda m: m.text.isdigit())
def set_mise(message):
    user = get_user(message.chat.id)
    user['mise_base'] = int(message.text)
    bot.send_message(message.chat.id, f"Mise: {message.text} FCFA")

bot.infinity_polling()
