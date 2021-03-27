from models import APIUser, APIKey, FakeUser, FakeLocation
from flask import request, jsonify, abort, session
from flask_restful import Resource, reqparse
from app import app, q, logger, conn

from random import randint
from functools import wraps
from datetime import timedelta

# TODO: DECORATOR TO CHECK IF ARQ PARSE HAS THROWN AN ERROR TO DECREMNT API CALLS NUMBER BY 1


faker_get_parser = reqparse.RequestParser(bundle_errors=True)
faker_get_parser.add_argument('user_id', help='Specify user_id (int) to get specific user. If left blank - random user will be retrieved', type=int)


faker_put_parser = reqparse.RequestParser(bundle_errors=True)
faker_put_parser.add_argument('user_id', help='Specify user_id (int) to get specific user. If left blank - random user will be retrieved', type=int, required=True)
faker_put_parser.add_argument('first_name', help='Specify first name (optional)', type=str)
faker_put_parser.add_argument('last_name', help='Specify last name (optional)', type=str)
faker_put_parser.add_argument('middle_name', help='Specify middle name (optional)', type=str)
faker_put_parser.add_argument('location_id', help='Specify location id. Fill it blank if you want to use random location id', type=int)


faker_post_parser = reqparse.RequestParser(bundle_errors=True)
faker_post_parser.add_argument('first_name', help='Specify first name', required=True, type=str)
faker_post_parser.add_argument('last_name', help='Specify last name', required=True, type=str)
faker_post_parser.add_argument('middle_name', help='Specify middle name (optional)', type=str)
faker_post_parser.add_argument('location_id', help='Specify location id. Fill it blank if you want to use random location id', type=int)






def validate_api_key(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        logger.debug('IN validate_api_key')

        api_key = kwargs.get('api_key', 'None')
        logger.debug('GOT API KEY %s', api_key)
        
        api_key_obj = APIKey.query.filter_by(key=api_key).first()
        if api_key_obj:
            logger.debug('FOUND API KEY OBJECT %s', api_key_obj)
        else:
            logger.debug('COULD NOT FIND USER WITH SUCH API KEY %s', api_key)

        if api_key_obj and api_key_obj.is_valid and api_key_obj.user:
            logger.debug('SUCCESSFUL API KEY VALIDATION')

            return api_method(*args, **kwargs)
        else:
            logger.debug('API KEY VALIDATION FAILED')
            logger.debug('ABORTING 401')
            abort(401, 'Specify the valid API key. You can get by contacting me on GitHub')

    return inner


def enqueue_api_calls_flush(api_method):

    @wraps(api_method)
    def inner(*args, **kwargs):

        def create_job():
            func = api_user.flush_api_calls
            interval = api_user.api_call_interval

            job = q.enqueue_in(interval, func, (api_key, ), job_id=api_key)
            logger.debug('JOB CREAETD %s', job)


        logger.debug('IN enqueue_api_calls_flush')

        api_key = kwargs.get('api_key')
        api_user = APIUser.query.filter_by(api_user_key=api_key).first()
        job = q.fetch_job(api_key)
        
        logger.debug('CHECKING FOR EXISTING JOB %s', job)

        # Creating new Job to flush api calls in 10 seconds, and of course granting user access to our APIs, since there were no jobs -> hence no limitations
        if not job:             
            logger.debug('CREATING NEW JOB FOR %s', api_key)
            create_job()

        # Deleting existing jobs and createing new ones, if api calls limit was not exceeded or if current job is finished
        else:
            logger.debug('JOB IS ENQUEUED AT %s', job.enqueued_at)
            logger.debug('IS JOB FINISHED? %s', job.is_finished)

            if api_user.api_calls == api_user.api_calls_limit:
                logger.debug('NOT OVERWRITING EXISTING JOB TO AVOID CONTINIOUS LIMITATIONS FOR USER')
            else:
                if not job.is_finished:
                    # job.delete()
                    job.cancel()
                    logger.debug('JOB NOT FINISHED -> CANCELING IT')
                logger.debug('CREATING NEW JOB SINCE API CALLS LIMIT NOT EXCEEDED')
                create_job()

        logger.debug('RETURNING API METHOD')
        return api_method(*args, **kwargs)        

    return inner


def check_api_calls_limit(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        logger.debug('IN check_api_calls_limit')

        api_key = kwargs.get('api_key')
        api_user = APIUser.query.filter_by(api_user_key=api_key).first()

        logger.debug('API USER CALLS %s per %s', api_user.api_calls, api_user.api_calls_limit)

        if api_user.api_calls < api_user.api_calls_limit:
            logger.debug('INCREMENTING API CALLS BY 1')            
            api_user.change_api_calls_by_n(n=1)        

            return api_method(*args, **kwargs)        
        else:
            logger.debug('API CALLS LIMIT EXCEEDED')
            logger.debug('ABORTING 401')
            abort(401, f'You have exceeded your API limit: {api_user.api_calls_limit} calls per {api_user.api_call_interval.seconds} seconds')

    return inner



class Faker(Resource):

    # Decorators execution order -> from top to bottom 

    # Retrieve
    @validate_api_key
    @enqueue_api_calls_flush
    @check_api_calls_limit
    def get(self, api_key):
        logger.debug('FAKER: IN GET')

        api_user = APIUser.query.filter_by(api_user_key=api_key).first()
        api_user.change_api_calls_by_n(-1)

        args = faker_get_parser.parse_args()
        logger.debug('PARSED GET ARGS %s', args)

        if args['user_id']:
            id = args['user_id']
            fake_user = FakeUser.query.get(id)

        else:
            count = int(APIUser.query.count())
            random_id = randint(1, count)
            fake_user = FakeUser.query.get(random_id)
            logger.debug('Fake user found %s #%s', fake_user, count)

        api_user.change_api_calls_by_n(1)
        return fake_user.jsonified()


    # Update
    @validate_api_key
    @enqueue_api_calls_flush
    @check_api_calls_limit
    def put(self, api_key):
        logger.debug('FAKER: IN PUT')
        api_user = APIUser.query.filter_by(api_user_key=api_key).first()
        api_user.change_api_calls_by_n(-1)

        fields = faker_put_parser.parse_args()

        if not any(fields.values()):
            abort(400, 'You cannot leave all fields blank, specify at least one field to change FakeUser data')

        user_id = fields['user_id']
        fields.pop('user_id')
        updated, fake_user = FakeUser.update(user_id, **fields)
        if not updated:
            abort(400, 'You can specify only these fields: "middle_name", "first_name", "last_name", "location_id"')

        api_user.change_api_calls_by_n(1)
        return {
            'updated': updated,
            'updated_obj': fake_user.jsonified(),
        }
        

    # Create
    @validate_api_key
    @enqueue_api_calls_flush
    @check_api_calls_limit
    def post(self, api_key):
        logger.debug('FAKER: IN POST')
        api_user = APIUser.query.filter_by(api_user_key=api_key).first()
        api_user.change_api_calls_by_n(-1)

        fields = faker_post_parser.parse_args()
        if not fields['location_id']:
            count = int(FakeLocation.query.count())
            random_id = randint(1, count)
            fields['location_id'] = FakeLocation.query.get(random_id).id

        fake_user = FakeUser.create(**fields)

        api_user.change_api_calls_by_n(1)
        return { 
            'created': True, 
            'created_obj': fake_user.jsonified(),
        }