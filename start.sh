#!/bin/bash

# Start the Flask web server in the background
gunicorn --bind 0.0.0.0:${PORT:-10000} app:app &

# Start the Telegram bot
python3 bot.py
