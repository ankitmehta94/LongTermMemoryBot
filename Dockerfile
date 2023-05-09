FROM python:3.9

COPY requirements.txt ./requirements.txt
COPY .env .env

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN TMPDIR=/var/tmp pip install --cache-dir=$TMPDIR -r requirements.txt

COPY bot ./bot

COPY prompt_templates ./prompt_templates

CMD ["python","-u", "bot/telegram_bot.py"]