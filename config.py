from os import environ


class Configuration:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = r'sqlite:///C:\Users\khova\Desktop\Python\Code\Flask-Restful-Api\restfulapi.db'
    SECRET_KEY = 'super_secret_hasehd_encrypted_key_to_protect_my_sophisticated_web_application_from_various_hackers_on_a_daily_basis'

    REDIS_URL = 'redis://'          # environ.get('REDIS_URL')