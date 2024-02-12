import os

from urllib.parse import unquote
from datetime import timedelta
from uuid import uuid4


class Config(object):
    SECRET_KEY                     = os.getenv("SECRET_KEY", uuid4().hex)
    JWT_SECRET_KEY                 = os.getenv("JWT_SECRET_KEY", uuid4().hex)
    JWT_ACCESS_TOKEN_EXPIRES       = timedelta(minutes=float(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 30)))
    JWT_REFRESH_TOKEN_EXPIRES      = timedelta(days=float(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 1)))
    SQLALCHEMY_DATABASE_URI        = unquote(os.getenv("DATABASE_URI"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL                      = unquote(os.getenv("REDIS_URL"))
    CELERY_BROKER_URL              = unquote(os.getenv("CELERY_BROKER_URL"))
    CELERY_RESULT_BACKEND          = unquote(os.getenv("CELERY_RESULT_BACKEND"))
