from app import app, api
from views import HelloWorld, Health, Test, Football


if __name__ == '__main__':
    api.add_resource(HelloWorld, '/hello')
    api.add_resource(Health, '/health/<int:age>/<int:weight>')
    api.add_resource(Test, '/test/<int:user_id>')
    api.add_resource(Football, '/football/<string:team_name>')
    app.run()
