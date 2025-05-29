import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7580467227:AAGagVf4gzoH1w5qzJaOu5vx0bF9ZJ0PXjM")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "8078347"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "721e258069f64e1ecb75c56907927ff2")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "1980071557"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://AMK-Save-Restricted-Content:hSgvCEAHbvzTjgjl@cluster0.jrzeth7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "amksavecontentbot")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
