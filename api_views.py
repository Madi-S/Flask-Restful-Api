from models import APIKey, APIUser, User, Location, Job
from flask_restful import Resource, reqparse
from flask import request, jsonify, abort
from app import app

from functools import wraps
from datetime import timedelta
from rq import Queue, Connection

import redis

r = redis.Redis()
q = Queue(connection=r)


def enqueue_api_calls_flush(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):

        print('*** In enqueue_api_calls_flush')

        api_key = kwargs.get('api_key', 'lololo')

        existing_job = Job.query.filter_by(api_user_key=api_key).first()
        if not existing_job:
            # Creating new Job to flush api calls in 4 hours
            api_user = APIUser.query.filter_by(api_user_key=api_key).first()
            
            func = api_user.flush_api_calls
            interval = api_user.api_call_interval

            job = q.enqueue_in(interval, func)
            
            Job.create(job.id, api_key)

            return api_method(*args, **kwargs)

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

        print('*** In validate_api_key')

        api_key = kwargs.get('api_key', 'lololo')

        api_key_obj = APIKey.query.filter_by(key=api_key).first()

        print('*** API KEY OBJ', api_key_obj)

        if api_key_obj and api_key_obj.is_valid and api_key_obj.user:
            return api_method(*args, **kwargs)
        else:
            abort(401, 'Specify the valid API key. You can get by contacting me on GitHub')

    return inner


def check_api_calls_limit(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):

        print('*** In check_api_calls_limit')

        api_key = kwargs.get('api_key', 'lololo')

        api_user = APIUser.query.filter_by(api_user_key=api_key).first()
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
    def get(self, api_key):
        print('*** In get')

    @validate_api_key
    @check_api_calls_limit
    def post(self, api_key):
        print('*** In post')
