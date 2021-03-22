from models import FlushAPICallsJob, APIUser, APIKey, FakeUser, FakeLocation
from flask_restful import Resource, reqparse
from flask import request, jsonify, abort
from app import app, q, logger

from functools import wraps
from datetime import timedelta


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
        api_user = APIUser.query.filter_by(api_user_key=api_key).first()

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
            abort(401, f'You have exceeded your API calls limit per {api_user.api_call_interval.seconds} seconds')

    return inner



class Faker(Resource):

    # Decorators execution order -> from top to bottom 

    @validate_api_key
    @enqueue_api_calls_flush
    @check_api_calls_limit
    def get(self, api_key):
        # args = 
        # TODO: if args req parser has hrown an error, decrement api calls by 1
        logger.debug('FAKER: IN GET')
        fake_user = FakeUser.query.get(1)
        return fake_user.jsonified()

    @validate_api_key
    @check_api_calls_limit
    def post(self, api_key):
        logger.debug('FAKER: IN POST')
        fake_user = FakeUser.query.get(1)
        return fake_user.jsonified()