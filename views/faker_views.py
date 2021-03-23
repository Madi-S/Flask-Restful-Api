from models import FlushAPICallsJob, APIUser, APIKey, FakeUser, FakeLocation
from flask import request, jsonify, abort, session
from flask_restful import Resource, reqparse
from app import app, q, logger

from random import randint
from functools import wraps
from datetime import timedelta

# TODO: DECORATOR TO CHECK IF ARQ PARSE HAS THROWN AN ERROR TO DECREMNT API CALLS NUMBER BY 1


faker_get_parser = reqparse.RequestParser(bundle_errors=True)
faker_get_parser.add_argument('user_id', help='Specify user_id (int) to get specific user', type=int, nullable=False)
faker_get_parser.add_argument('random', help='By passing random a random user will be retrieved', action='store_true')

faker_post_parser = reqparse.RequestParser(bundle_errors=True)
faker_post_parser.add_argument('first_name', help='Specify first name', required=True, type=str)
faker_post_parser.add_argument('last_name', help='Specify last name', required=True, type=str)
faker_post_parser.add_argument('middle_name', help='Specify middle name (optional)', type=str)
faker_post_parser.add_argument('location_id', help='Specify location id. Fill it blank if you want to use random location id', type=int)

faker_put_parser = reqparse.RequestParser(bundle_errors=True)
faker_put_parser.add_argument('first_name', help='Specify first name (optional)', type=str)
faker_put_parser.add_argument('last_name', help='Specify last name (optional)', type=str)
faker_put_parser.add_argument('middle_name', help='Specify middle name (optional)', type=str)
faker_put_parser.add_argument('location_id', help='Specify location id. Fill it blank if you want to use random location id', type=int)



def create_jobs_for(api_user):
    api_key = api_user.api_user_key
    func = api_user.flush_api_calls
    interval = api_user.api_call_interval

    rq_job = q.enqueue_in(interval, func, (api_key, ))
    logger.debug('RQ JOB CREAETD %s', rq_job)
    
    job_model = FlushAPICallsJob.create(rq_job.id, api_key)
    logger.debug('JOB MODEL CREATED %s', job_model)



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

            session['api_user'] = api_key_obj.user
            return api_method(*args, **kwargs)
        else:
            logger.debug('API KEY VALIDATION FAILED')
            logger.debug('ABORTING 401')
            abort(401, 'Specify the valid API key. You can get by contacting me on GitHub')

    return inner


def enqueue_api_calls_flush(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        logger.debug('IN enqueue_api_calls_flush')

        api_key = kwargs.get('api_key')
        api_user = session.get('api_user')

        job_model = FlushAPICallsJob.query.filter_by(api_user_key=api_key).first()
        
        if job_model:
            logger.debug('JOB MODEL EXISTS %s', job_model)
            job_id = job_model.job_id
            rq_job = q.fetch_job(job_id)
            logger.debug('REDIS QUEUE JOB %s', rq_job)
        else:
            logger.debug('NO FLUSH API CALLS JOBS WERE FOUND')
            rq_job = None

        # Creating new Job to flush api calls in 10 seconds, anf of course granting user access to our APIs, since there were no jobs -> hence no limitations
        if not (job_model and rq_job):             
            logger.debug('CREATING NEW JOB FOR %s', api_key)
            create_jobs_for(api_user) 

        # Deleting existing jobs and createing new ones, if api calls limit was not exceeded or if current job is finished
        else:
            logger.debug('RQ JOB IS ENQUEUED AT %s', rq_job.enqueued_at)
            logger.debug('IS JOB FINISHED? %s', rq_job.is_finished)

            if rq_job.is_finished or api_user.api_calls < api_user.api_calls_limit:
                logger.debug('JOB IS FINISHED OR API CALLS LIMIT WAS NOT EXCEEDED')            
                rq_job.delete()
                job_model.delete()
                logger.debug('JOBS DELETED')

                create_jobs_for(api_user)
            else:
                logger.debug('API CALLS LIMIT IS EXCEEDED')
                logger.debug('NOT OVERWRITING EXISTING JOB TO AVOID CONTINIOUS LIMITATIONS FOR USER')

        logger.debug('RETURNING API METHOD')
        return api_method(*args, **kwargs)        

    return inner


def check_api_calls_limit(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):
        logger.debug('IN check_api_calls_limit')

        api_user = session.get('api_user')

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
        api_user = session.get('api_user')
        api_user.change_api_calls_by_n(-1)

        args = faker_get_parser.parse_args()
        logger.debug('PARSED GET ARGS %s', args)

        if not any(args.values()) or all(args.values()):
            abort(400, 'You cannot specify both "random" and "user_id" parameters or leave the both blank')

        if args['random']:
            count = int(APIUser.query.count())
            random_id = randint(1, count)
            fake_user = APIUser.query.get(random_id)

        elif args['location_id']:
            n = args['user_id']
            fake_user = FakeUser.query.get(n)

        api_user.change_api_calls_by_n(1)
        return fake_user.jsonified()


    # Update
    @validate_api_key
    @enqueue_api_calls_flush
    @check_api_calls_limit
    def put(self, api_key):
        logger.debug('FAKER: IN PUT')
        api_user = session.get('api_user')
        api_user.change_api_calls_by_n(-1)

        fields = faker_put_parser.parse_args()

        if not any(fields.values()):
            abort(400, 'You cannot leave all fields blank, specify at least one field to change FakeUser data')

        updated, fake_user = FakeUser.update(api_user.id, **fields)
        if not updated:
            abort(400, 'You have specified can change only these fields: "middle_name", "first_name", "last_name", "location_id"')

        api_user.change_api_calls_by_n(1)
        return {
            'updated': updated,
            'updated_obj': fake_user.jsonified(),
        }
        

    # Create
    @validate_api_key
    @check_api_calls_limit
    def post(self, api_key):
        logger.debug('FAKER: IN POST')
        api_user = session.get('api_user')
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