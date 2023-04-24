FROM python:3.9

COPY bot ./bot
COPY requirements.txt ./requirements.txt
COPY prompt_templates ./prompt_templates

RUN pip install -r requirements.txt

CMD ["python", "bot/telegram_bot.py"]