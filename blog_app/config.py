from decouple import config

DATABASE_URI = config("MONGO_URI", default="mongodb://localhost:27017/blog_db")

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = config("SECRET_KEY", default="guess-me")
    MONGO_URI = DATABASE_URI
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True
    MONGO_URI = config("MONGO_URI_DEV", default="mongodb://localhost:27017/blog_db_dev")


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MONGO_URI = config("MONGO_URI_TEST", default="mongodb://localhost:27017/blog_db_test")
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    DEBUG_TB_ENABLED = False
    MONGO_URI = config("MONGO_URI_PROD", default="mongodb://localhost:27017/blog_db_prod")
