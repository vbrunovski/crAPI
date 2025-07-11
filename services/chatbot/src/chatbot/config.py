import os

from dotenv import load_dotenv

from .dbconnections import MONGO_CONNECTION_URI

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
    MONGO_URI = MONGO_CONNECTION_URI
