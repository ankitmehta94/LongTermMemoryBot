import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from generate_response import generate_response
from aws_utils import upload_to_s3, transcribe_audio, get_transcript, add_transcript, add_multiple_todos
from utils import root_dir, create_directory
from langchain_utils import get_fixed_message, get_todo_list
from message_utils import create_todo_list, update_todo_list
import os
from uuid import uuid4

telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
bucket_name = "fast-telegram-bot-files"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def create_todo_buttons(todo_array):
    formatted_keyboard = []
    for todo in todo_array:
        id = todo['id']
        single_line = [InlineKeyboardButton(todo['todo'], callback_data="Deeper:{todo_id}".format(todo_id=id)),
                       InlineKeyboardButton("✅",
                                            callback_data="Complete:{t_id}".format(t_id=id)),
                       InlineKeyboardButton("🗓",
                                            callback_data="Delete:{t_id}".format(t_id=id)),
                       ]
        formatted_keyboard.append(single_line)
    print(formatted_keyboard)
    return InlineKeyboardMarkup(formatted_keyboard)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print(update, context)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    callback_data_array = query.data.split(":")
    transcription = get_transcript(transcript_id=callback_data_array[1])
    response = 'You did not journal'
    if callback_data_array[0] == "Journal":
        response = get_fixed_message(transcription)
        await query.edit_message_text(text=response)
    if callback_data_array[0] == "Create Todo List":
        todo_json = update_todo_list(get_todo_list(transcription))
        add_multiple_todos(todo_json)
        response = create_todo_list(todo_array=todo_json)
        reply_markup = create_todo_buttons(todo_array=todo_json)
        await query.edit_message_text(text=response)
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=reply_markup, text='Choose What to do with the todo list')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = generate_response(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


async def voice_downloader(update, context):
    file_id = update.message.voice.file_id
    user_id = update.message.from_user.id
    file = await context.bot.get_file(file_id)
    user_folder = '{root_dir}/voice_notes/{user_id}'.format(
        user_id=user_id, root_dir=root_dir)
    create_directory(user_folder)
    file_path = '{user_folder}/{file_id}.ogg'.format(
        file_id=file_id, user_folder=user_folder)
    await file.download_to_drive(file_path)
    return file_path


async def recieve_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = await voice_downloader(update, context)
    upload_to_s3(bucket_name=bucket_name, file_path=file_path,
                 local_file_path=file_path)
    transcription = transcribe_audio(
        bucket_name=bucket_name, file_name=file_path)
    user_id = update.message.from_user.id
    t_id = str(uuid4())
    print(transcription)
    add_transcript(user_id=user_id, transcript_text=transcription,
                   transcript_id=t_id)
    keyboard = [
        [InlineKeyboardButton("Journal", callback_data="Journal:{t_id}".format(t_id=t_id)),
         InlineKeyboardButton("Create Todo List",
                              callback_data="Create Todo List:{t_id}".format(t_id=t_id)),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=reply_markup, text='Choose What to do with the recording')
    # reply = get_fixed_message(transcription)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    echo_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), echo)
    voice_handler = MessageHandler(filters.VOICE, recieve_voice)

    application.add_handler(echo_handler)
    application.add_handler(voice_handler)
    start_handler = CommandHandler('start', start)
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(start_handler)

    application.run_polling()
