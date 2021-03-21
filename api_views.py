import models 
from flask_restful import Resource, reqparse
from flask import request, jsonify, abort
from app import app, q

from functools import wraps
from datetime import timedelta


def validate_api_key(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):

        print('*** IN validate_api_key')

        api_key = kwargs.get('api_key', 'lololo')

        api_key_obj = models.APIKey.query.filter_by(key=api_key).first()

        print('*** API KEY OBJ:', api_key_obj)

        if api_key_obj and api_key_obj.is_valid and api_key_obj.user:

            print('*** SUCCESSFUL API KEY VALIDATION')

            return api_method(*args, **kwargs)
        else:
            abort(401, 'Specify the valid API key. You can get by contacting me on GitHub')

    return inner


def enqueue_api_calls_flush(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):

        print('*** IN enqueue_api_calls_flush')

        api_key = kwargs.get('api_key')
        api_user = models.APIUser.query.filter_by(api_user_key=api_key).first()

        print('*** API_KEY:', api_key)

        job_model = models.Job.query.filter_by(api_user_key=api_key).first()
        if job_model:
            job_id = job_model.id
            rq_job = q.fetch_job(job_id)
        else:
            rq_job = None

        # if rq_job:
        #     rq_job.refresh()

        print('*** EXISTING RQ JOB:', rq_job)
        print('*** EXISTING JOB MODEL:', job_model)

        # Creating new Job to flush api calls in 4 hours, anf ofc granting user access to our APIs
        if not (job_model and rq_job):             
            print('*** NO EXISTING JOB -> CREATING NEW JOB')

            print('*** GONNA FLUSH API_CALLS TO:', api_key)
            
            func = api_user.flush_api_calls
            # interval = api_user.api_call_interval
            interval = timedelta(seconds=10)

            print('*** INTERVAL IN SEC:', interval.seconds)

            rq_job = q.enqueue_in(interval, func, (api_key, ))
            models.Job.create(rq_job.id, api_key)

        # Deleting Job on completion and creating a new one, if not completed yet -> rewriting it with a new rq job
        else:            
            print('*** JOB ALREADY EXISTS')


            print('*** RQ JOB:', rq_job)
            print('*** JOB MODEL:', job_model)

            print('*** ENQUEUED AT:',rq_job.enqueued_at)

            print('*** JOB STATUS:', rq_job.is_finished)

            # Finished? Delete it, and grant user access to our APIs and enqueue another job
            if rq_job.is_finished:
                print('*** JOB IS FINISHED -> DELETING IT')
            
                # Delete as rq object
                rq_job.delete()

                # Delete as model object
                job_model.delete()

                # Enqueue new job
                func = api_user.flush_api_calls
                # interval = api_user.api_call_interval
                interval = timedelta(seconds=10)

                rq_job = q.enqueue_in(interval, func, (api_key,))
                models.Job.create(rq_job.id, api_key)

            # Overwrite existing running job only if limit was not exceeded with in order to not refresh job every time locked api call was received 
            else:           
                print('*** GONNA OVERWRITE EXISTING JOB ONLY IF API CALLS LIMIT WAS NOT EXCEED')                

                # As said above, canceling existing job if api calls limit is not exceeded
                if api_user.api_calls < api_user.api_calls_limit:
                    print('*** OVERWRITING EXISTING JOB')

                    rq_job.delete()

                    # Delete as model object
                    # existing_job.delete()
                    job_model.delete()

                    # Enqueue new job
                    func = api_user.flush_api_calls
                    # interval = api_user.api_call_interval
                    interval = timedelta(seconds=10)

                    rq_job = q.enqueue_in(interval, func, (api_key, ))
                    models.Job.create(rq_job.id, api_key)

                    print('*** OVERWRITTEN')

        return api_method(*args, **kwargs)        

    return inner


def check_api_calls_limit(api_method):
    @wraps(api_method)
    def inner(*args, **kwargs):

        print('*** IN check_api_calls_limit')

        api_key = kwargs.get('api_key', 'lololo')
        api_user = models.APIUser.query.filter_by(api_user_key=api_key).first()

        print('*** API_USER:', api_user)

        if api_user.api_calls < api_user.api_calls_limit:
            api_user.increment_api_calls_by_n(n=1)
        
            print('*** INCREMENTING API CALLS')

            return api_method(*args, **kwargs)        
        else:
            print('*** API CALLS LIMIT EXCEEDED')

            abort(401, f'You have exceeded your API calls limit per {api_user.api_call_interval.seconds} seconds')

    return inner



class Faker(Resource):

    # Decorators execution order -> from top to bottom 

    @validate_api_key
    @enqueue_api_calls_flush
    @check_api_calls_limit
    def get(self, api_key):
        print('*** IN GET')

    @validate_api_key
    @check_api_calls_limit
    def post(self, api_key):
        print('*** IN POST')
