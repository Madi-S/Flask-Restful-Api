from functools import wraps
from flask_restful import Resource, reqparse
from flask import request, jsonify, abort
from app import app
from models import APIKey, APIUser, User, Location




def validate_api_key(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        api_key = request.headers.get('api_key')
        api_key_obj = APIKey.query.filter_by(key=api_key).first()
        if api_key_obj and api_key_obj.is_valid and api_key_obj.api_user:
            return api_method(*args, **kwargs)
        else:
            abort(401, 'Specify the valid API key. You can get by contacting me on GitHub')

    return inner

def check_api_calls_limit(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        api_key = request.headers.get('api_key')
        api_user = APIUser.query.filter_by(key=api_key).first()
        if api_user and api_user.api_calls <= api_user.api_calls_limit:
            return api_method(*args, **kwargs)
        else:
            abort(401, f'You have exceeded your API calls limit per {api_call_interval.seconds} seconds')

    return inner

class Faker(Resource):

    # Decorators execution order -> from top to bottom 

    @validate_api_key
    @check_api_calls_limit
    def get(self, user_id):
        pass

    @validate_api_key
    @check_api_calls_limit
    def post(self, **data):
        pass


def top_dec(function):
    def inner(*args, **kwargs):
        print('top dec')
        return function(*args, **kwargs)

    return inner


def low_dec(function):
    def inner(*args, **kwargs):
        print('low dec')
        return function(*args, **kwargs)

    return inner



@top_dec
@low_dec
def func():
    pass

if __name__ == '__main__':
    func()