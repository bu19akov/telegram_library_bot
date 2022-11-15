import requests
from telegram.ext import Updater, Filters, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup
from bot.credentials import bot_token

global TOKEN
TOKEN = bot_token
url = 'https://bib-platz.univie.ac.at/hb-glsk/'
dates = dict()
updater = Updater(TOKEN, use_context=True)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello! I'll help you to find free places in the main library!",
                             reply_to_message_id=update.message.message_id)
    r = requests.get(url)
    content = r.content
    soup = BeautifulSoup(content, "html.parser")
    blocks = soup.find_all("details", {"class": "has-events"})
    for i in blocks:
        if not i.find("a", {"class": "event over"}):
            dates[i.find("time").text] = i.find("a")["href"]
    keyboard = [[InlineKeyboardButton(i, callback_data=i)] for i, j in dates.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose the date:", reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.answer()
    try:
        url = dates[query.data]
    except KeyError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your request has expired! Created a new one by writing /start!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Here is the link:")
        context.bot.send_message(chat_id=update.effective_chat.id, text=url)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Checking free slots... I'll inform you about available places:)")
        dates.clear()
        while True:
            r = requests.get(url)
            content = r.content
            soup = BeautifulSoup(content, "html.parser")
            places = soup.find("div", {"class": "availability-box"}).find("strong")
            if places and (places.text.strip() == "AUSGEBUCHT" or places.text.strip() == "Reserviert"):
                continue
            break
        context.bot.send_message(chat_id=update.effective_chat.id, text="There are free places now! Hurry up!")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write /start!")


def main():
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()

