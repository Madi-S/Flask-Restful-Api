from os import environ
from sys import platform


class Configuration:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super_secret_hasehd_encrypted_key_to_protect_my_sophisticated_web_application_from_various_hackers_on_a_daily_basis'

    if platform.startswith('w'):
        # For Windows
        SQLALCHEMY_DATABASE_URI = r'sqlite:///C:\Users\khova\Desktop\Python\Code\Flask-Restful-Api\app\restful.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/retful.db'                  # 'mysql+mysqlconnector://root:1234@localhost/restful'


    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    
    STRIPE_PUBLIC_KEY = environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY') 