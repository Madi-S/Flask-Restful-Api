from models import APIKey, APIUser, User, Location, Job
from flask_restful import Resource, reqparse
from flask import request, jsonify, abort
from app import app

from functools import wraps
from rq import Queue, Connection

import redis

r = redis.Redis()
q = Queue(connection=r)


def enqueue_api_calls_flush(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        api_key = request.headers.get('api_key')
        
        existing_job = Job.query.filter_by(key=api_key).first()
        if not existing_job:
            # Creating new Job to flush api calls in 4 hours
            api_user = APIUser.query.filter_by(key=api_key).first()
            job = q.enqueue(api_user.flush_api_calls)
            
            Job.create(job.id, api_key)

        else:
            if existing_job.is_completed:
                # Delete job
                existing_job.delete()
            else:
                # Abort
                abort(401, 'You have exceeded maximum api calls, wait for while and the come back')


    return inner


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
            abort(401, f'You have exceeded your API calls limit per {api_user.api_call_interval.seconds} seconds')

    return inner



class Faker(Resource):

    # Decorators execution order -> from top to bottom 

    @validate_api_key
    @enqueue_api_calls_flush
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