import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'VJ Save Restricted Bot is running!'

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'vj-save-restricted-bot'}

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
