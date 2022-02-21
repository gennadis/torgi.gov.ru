import locale
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

from mongo_db_client import get_database, get_notification_summary


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Apartments", callback_data="moscow_apartments")],
        [InlineKeyboardButton("Offices", callback_data="moscow_offices")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    reply_text = get_reply_text(query.data)
    query.edit_message_text(text=reply_text, disable_web_page_preview=False)


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start to test this bot.")


def get_reply_text(collection_name: str) -> str:
    mongodb_url = os.getenv("MONGODB_URL")
    mongodb_client = get_database(mongodb_url)

    notification = mongodb_client[collection_name].find_one()
    notification_summary = get_notification_summary(notification)
    price, description = notification_summary["lots_summary"][0]

    reply_text = notification_summary["link"]

    return reply_text


def main():
    load_dotenv()
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")

    locale.setlocale(locale.LC_ALL, "ru_RU")

    updater = Updater(tg_token)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
