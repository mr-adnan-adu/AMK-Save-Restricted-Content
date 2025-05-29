FROM python:3.10.8-slim-buster

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port that the app runs on
EXPOSE 10000

# Run both Flask app and Telegram bot
# The & runs the first command in background, then runs the second command
CMD gunicorn --bind 0.0.0.0:$PORT app:app & python3 bot.py
