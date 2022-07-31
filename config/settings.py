from datetime import timedelta

DEBUG = True
TESTING = False

SERVER_NAME = "localhost:8888"
SECRET_KEY = "insecurefordev"

# Flask-Main
MAIL_DEFAULT_SENDER = "contact@local.host"
MAIl_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIN_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "mail@mail.com"
MAIL_PASSWORD = "dvwsdv"

# Celery
CELERY_BROKER_URL = "redis://:devpassword@redis:6379/0"
CELERY_RESULT_BACKEND = "redis://:devpassword@redis:6379/0"
CELERY_ACECPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_REDIS_MAX_CONNECTIONS = 5


# SQLAlchemy.
db_uri = "postgresql://snakeeyes:devpassword@postgres:5432/snakeeyes"
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# User.
SEED_ADMIN_EMAIL = "dev@local.host"
SEED_ADMIN_PASSWORD = "devpassword"
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Platform
PLATFORM_SECRET_KEY = "secret"
SEED_PLATFORM_NAME = ["myc"]

# Mongo
MONGODB_DB = "calendar"
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_USERNAME = "admin"
MONGODB_PASSWORD = "pass"
MONGO_AUTH_SOURCE = "admin"
