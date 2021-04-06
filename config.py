from os import environ


class Configuration:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super_secret_hasehd_encrypted_key_to_protect_my_sophisticated_web_application_from_various_hackers_on_a_daily_basis'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/retful.db'                  # 'mysql+mysqlconnector://root:1234@localhost/restful'

    GOOGLEMAPS_KEY = '8JZ7i18MjFuM35dJHq70n3Hx4'

    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    
    STRIPE_PUBLIC_KEY = environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY') 