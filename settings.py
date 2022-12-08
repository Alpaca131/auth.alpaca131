import os

if os.path.isfile('.env'):
    from dotenv import load_dotenv
    load_dotenv()

SESSION_SECRET = os.environ['SESSION_SECRET']
FIVE_DON_BOT_SECRET = os.environ["FIVE_DON_BOT_SECRET"]
FIVE_DON_BOT_TOKEN = os.environ["FIVE_DON_BOT_TOKEN"]
DEVELOPMENT = True if os.getenv("DEVELOPMENT") else False
