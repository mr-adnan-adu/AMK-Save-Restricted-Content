#!/bin/bash

echo "Starting VJ Save Restricted Content Bot..."

# Start Flask web server in background
echo "Starting Flask web server on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT app:app &

# Wait a moment for the web server to start
sleep 3

# Start Telegram bot
echo "Starting Telegram bot..."
python3 bot.py
