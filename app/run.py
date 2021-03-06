from views import *

from resources.faker import Faker
from resources.sample import SampleEndpoint
from resources.common import HelloWorld, Health, Test


if __name__ == '__main__':
    logger.debug('ADDING RESOURCES')

    api.add_resource(HelloWorld, '/hello')
    api.add_resource(Test, '/test/<int:user_id>')
    api.add_resource(Faker, '/faker/<string:api_key>')
    api.add_resource(Health, '/health/<int:age>/<int:weight>')

    app.add_url_rule('/sample/<key>', view_func=SampleEndpoint.as_view('sample'))

    admin.add_view(AdminModelView(APIUser, db.session))
    admin.add_view(AdminModelView(APIKey, db.session))

    logger.debug('RESOURCES ADDED -> APP IS RUNNING')
    
    # app.run()
    sio.run(app)

    # Don't forget to run redis worker:
    # rq worker --with-scheduler

    # Authorize with strip account:
    # stripe login

    # Running via uWSGI:
    # uwsgi app.ini`