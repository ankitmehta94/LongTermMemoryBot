FROM pytorch/pytorch

COPY requirements.txt ./requirements.txt
COPY .env .env
RUN pip install -r requirements.txt

COPY bot ./bot

COPY prompt_templates ./prompt_templates

CMD ["python","-u", "bot/telegram_bot.py"]