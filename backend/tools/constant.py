import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("key")
DATABASE_PATH = os.environ.get("db_path")
TOKEN_LIFE = float(os.environ.get("token_live"))
COOKIE_NAME = os.environ.get("cookie_name")