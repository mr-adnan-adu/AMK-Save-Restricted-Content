#!/bin/bash

# Enhanced startup script with better error handling and process management
set -e  # Exit on any error

echo "🚀 Starting VJ Save Restricted Content Bot..."
echo "🕐 Current time: $(date)"

# Function to cleanup processes on exit
cleanup() {
    echo "🧹 Cleaning up processes..."
    # Kill background processes
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
    # Kill any remaining gunicorn processes
    pkill -f "gunicorn.*app:app" 2>/dev/null || true
    echo "✅ Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Validate required environment variables
required_vars=("BOT_TOKEN" "API_ID" "API_HASH" "DB_URI")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables: ${missing_vars[*]}"
    echo "Please set these variables before starting the bot."
    exit 1
fi

# Set default PORT if not provided
if [ -z "$PORT" ]; then
    export PORT=10000
    echo "⚠️ PORT not set, using default: $PORT"
fi

echo "🌐 Environment Variables:"
echo "  - PORT: $PORT"
echo "  - API_ID: ${API_ID:0:3}***"
echo "  - BOT_TOKEN: ${BOT_TOKEN:0:10}***"
echo "  - DB_URI: ${DB_URI:0:10}***"

# Clean up any existing session files
echo "🧹 Cleaning up old session files..."
find /tmp -name "techvj_*" -type f \( -name "*.session*" \) -delete 2>/dev/null || true

# Create a simple health check endpoint
echo "🏥 Starting health check server..."
cat > /tmp/health_server.py << 'EOF'
import os
import time
from flask import Flask, jsonify

app = Flask(__name__)
start_time = time.time()

@app.route('/')
def root():
    return jsonify({
        'status': 'healthy',
        'service': 'VJ Save Restricted Content Bot',
        'uptime': f"{int(time.time() - start_time)} seconds",
        'message': 'Bot is running successfully! 🤖'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time()),
        'uptime': f"{int(time.time() - start_time)} seconds"
    })

@app.route('/status')
def status():
    return jsonify({
        'bot_status': 'active',
        'service': 'Telegram Save Restricted Content Bot',
        'uptime': f"{int(time.time() - start_time)} seconds",
        'features': [
            'Save restricted content from Telegram',
            'User session management', 
            'Batch message processing',
            'Multi-format media support'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# Start Flask web server in background with better configuration
echo "🌐 Starting Flask web server on port $PORT..."
gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gevent \
    --worker-connections 1000 \
    --timeout 120 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    /tmp/health_server:app &

FLASK_PID=$!
echo "✅ Flask server started with PID: $FLASK_PID"

# Wait for Flask server to be ready
echo "⏳ Waiting for Flask server to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:$PORT/health >/dev/null 2>&1; then
        echo "✅ Flask server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Flask server failed to start within 30 seconds"
        cleanup
        exit 1
    fi
    sleep 1
done

# Set Python path and other optimizations
export PYTHONPATH="${PYTHONPATH}:."
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Configure asyncio policy for better performance
export PYTHONIOENCODING=utf-8

echo "🤖 Starting Telegram bot..."
echo "📊 System Info:"
echo "  - Python Version: $(python3 --version)"
echo "  - Available Memory: $(free -h | awk '/^Mem:/ {print $7}' 2>/dev/null || echo 'N/A')"
echo "  - Disk Space: $(df -h / | awk 'NR==2 {print $4}' 2>/dev/null || echo 'N/A')"

# Function to restart bot if it crashes
start_bot() {
    local attempt=1
    local max_attempts=5
    
    while [ $attempt -le $max_attempts ]; do
        echo "🚀 Starting bot (attempt $attempt/$max_attempts)..."
        
        # Start the bot
        python3 bot.py
        exit_code=$?
        
        echo "⚠️ Bot exited with code: $exit_code"
        
        if [ $exit_code -eq 0 ]; then
            echo "✅ Bot exited gracefully"
            break
        else
            echo "❌ Bot crashed with exit code: $exit_code"
            
            if [ $attempt -lt $max_attempts ]; then
                wait_time=$((attempt * 10))
                echo "⏳ Waiting $wait_time seconds before restart..."
                sleep $wait_time
                
                # Clean up session files before restart
                echo "🧹 Cleaning up session files..."
                find /tmp -name "techvj_*" -type f \( -name "*.session*" \) -delete 2>/dev/null || true
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Max restart attempts reached. Bot failed to start."
        cleanup
        exit 1
    fi
}

# Start the bot with restart capability
start_bot

echo "👋 Bot has stopped. Cleaning up..."
cleanup
