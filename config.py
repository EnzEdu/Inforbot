import os
BASE_DIR = os.path.dirname(__file__)
SQLITE_PATH = os.path.join(BASE_DIR, "instance")
PASTA_USERS = os.path.join(SQLITE_PATH, "users")
os.makedirs(PASTA_USERS, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get("INFORBOT_SECRET_KEY_PROD", "dev-secret-key")  # mudar em prod
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_PATH, "inforbot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = SQLITE_PATH