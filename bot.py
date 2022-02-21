import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Привет, {update.effective_user.first_name}!")


def main():
    load_dotenv()
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(tg_token)

    updater.dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
