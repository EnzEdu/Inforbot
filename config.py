import os
BASE_DIR = os.path.dirname(__file__)
SQLITE_PATH = os.path.join(BASE_DIR, "inforbot.db")

class Config:
    SECRET_KEY = os.environ.get("INFORBOT_SECRET_KEY_PROD", "dev-secret-key")  # mudar em prod
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False