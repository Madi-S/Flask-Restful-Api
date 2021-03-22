import logging

from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from config import Configuration

from redis import Redis
from rq import Queue


logger = logging.getLogger('API')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

app = Flask(__name__)
app.config.from_object(Configuration)
logger.debug('Flask app instantiated %s', app)

api = Api(app)
db = SQLAlchemy(app)

q = Queue(connection=Redis())

'''
'acquire_cleaning_lock', 'all', 'compact', 'connection', 'count', 'create_job', 
'deferred_job_registry', 'delete', 'dequeue_any', 'empty', 'enqueue', 'enqueue_at', 
'enqueue_call', 'enqueue_dependents', 'enqueue_in', 'enqueue_job', 
'failed_job_registry', 'fetch_job', 'finished_job_registry', 'from_queue_key', 
'get_job_ids', 'get_jobs', 'is_async', 'is_empty', 'job_class', 'job_ids', 'jobs', 
'key', 'lpop', 'name', 'pop_job_id', 'push_job_id', 'redis_queue_namespace_prefix', 
'redis_queues_keys', 'registry_cleaning_key', 'remove', 'run_job', 
'scheduled_job_registry', 'started_job_registry'
'''
