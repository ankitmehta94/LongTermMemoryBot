import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from generate_response import generate_response
from aws_utils import upload_to_s3, transcribe_audio
from utils import load_json, create_directory

aws_constants = load_json('./aws_constants.json')
telegram_token = load_json('./env_constants.json')['TERLRGRAM_BOT_TOKEN']

bucket_name = aws_constants['bucket_name']


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = generate_response(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


async def voice_downloader(update, context):
    file_id = update.message.voice.file_id
    user_id = update.message.from_user.id
    file = await context.bot.get_file(file_id)
    user_folder = 'voice_notes/{user_id}'.format(
        user_id=user_id)
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
    print(transcription)


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
    application.add_handler(start_handler)

    application.run_polling()
