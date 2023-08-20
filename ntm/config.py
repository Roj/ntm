from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
SERVER_PORT = os.environ.get("SERVER_PORT")
SQLITE_DB = os.environ.get("SQLITE_DB")
GAME_LENGTH = int(os.environ.get("GAME_LENGTH"))
