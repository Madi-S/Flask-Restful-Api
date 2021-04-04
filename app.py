from flask import Flask
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_migrate import Migrate
from flask_analytics import Analytics
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_googlemaps import GoogleMaps


from rq import Queue
from redis import Redis
from logger import logger
from config import Configuration


app = Flask(__name__)
app.config.from_object(Configuration)
logger.debug('Flask app instantiated %s', app)

api = Api(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
cache = Cache(app)
admin = Admin(app, 'Restful', template_mode='bootstrap3')

GoogleMaps(app)

Analytics(app)
app.config['ANALYTICS']['GAUGES']['SITE_ID'] = 'XXXXXXXXXXXXX'


conn = Redis('127.0.0.1', 6379)
q = Queue(connection=conn)

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
