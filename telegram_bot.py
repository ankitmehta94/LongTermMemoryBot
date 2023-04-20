import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


telegram_token = open_file('telegramtoken.txt')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def generate_response(message):
    # Your response-generating code here
    return "This is a response to your message: " + message


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = generate_response(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(echo_handler)
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()
