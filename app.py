import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'VJ Save Restricted Bot is running successfully! 🤖'

@app.route('/health')
def health_check():
    return {
        'status': 'healthy', 
        'service': 'vj-save-restricted-bot',
        'message': 'Bot is running and ready to process Telegram messages'
    }

@app.route('/status')
def status():
    return {
        'bot_status': 'active',
        'service': 'Telegram Save Restricted Content Bot',
        'features': [
            'Save restricted content from Telegram',
            'User session management',
            'Batch message processing',
            'Multi-format media support'
        ]
    }

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
