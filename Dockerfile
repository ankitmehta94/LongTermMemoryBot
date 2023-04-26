FROM python:3.9

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY bot ./bot

COPY prompt_templates ./prompt_templates

CMD ["python","-u", "bot/telegram_bot.py"]