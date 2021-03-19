from functools import wraps
from flask_restful import Resource, reqparse
from flask import request, jsonify, abort
from app import app

from football_parser import FootballParser


footbal_args_parser = reqparse.RequestParser()
footbal_args_parser.add_argument(
    'team_name', type=str, help='Specify the football team name as string', required=True)


test_create_parser = reqparse.RequestParser()
test_create_parser.add_argument(
    'name', type=str, help='Specify your name', required=True)
test_create_parser.add_argument(
    'age', type=int, help='Specify your age', required=True)
test_create_parser.add_argument(
    'location', type=str, help='Specify your location')
test_create_parser.add_argument(
    'gender', choices=['male', 'female'], help='Specify your gender')


test_update_parser = reqparse.RequestParser()
test_update_parser.add_argument('name', type=str, help='Specify your name')
test_update_parser.add_argument('age', type=int, help='Specify your age')
test_update_parser.add_argument('location', type=str, help='Specify your location')
test_update_parser.add_argument('gender', choices=['male', 'female'], help='Specify your gender')


def abort_if_team_doesnt_exist(team_name):
    if not FootballParser.team_exists(team_name):
        abort(404, 'Sorry, but specified football team does not exist')


class HelloWorld(Resource):
    def get(self):
        return {'method': request.method, 'hello': 'world'}

    def post(self):
        # return {
        #     'method': request.method,
        #     'got': {
        #         'form': str(request.form),
        #         'args': str(request.args),
        #         'json': str(request.json),
        #         'data': str(request.data),
        #         'files': str(request.files),
        #         'values': str(request.values),
        #     }}

        return jsonify(request.values)


class Health(Resource):
    def get(self, age, weight):
        healthy = age <= 50 and weight <= 80
        return {'healthy': healthy}


followers = {}



class Test(Resource):
    @staticmethod
    def abort_if_follower_already_exists(user_id):
        if user_id in followers:
            abort(409, 'Follower with such id already exists, you cannot create a new one with the same id')

    @staticmethod
    def abort_if_follower_doesnt_exist(user_id):
        if user_id in followers:
            abort(404, 'Follower with such id does not exist, you cannot delete or get data from non-existing user')


    # Retrieving
    def get(self, user_id):
        Test.abort_if_follower_doesnt_exist(user_id)

        return followers, 200

    # Creating
    def put(self, user_id):
        Test.abort_if_follower_already_exists(user_id)

        args = test_create_parser.parse_args()
        followers[user_id] = args
        return {'status': True, 'received_data': args}, 201

    # Updating
    def patch(self, user_id):
        Test.abort_if_follower_doesnt_exist(user_id)
        
        follower = followers[user_id]

        args = test_update_parser.parse_args()
        for key, value in args:            
            if value:
                follower[key] = value
        


    # Deleting
    def delete(self, user_id):
        Test.abort_if_follower_doesnt_exist(user_id)

        followers.pop(user_id, None)
        return {'deleted': True}, 204



def require_api_key(api_method):
    @wraps(api_method)
    def check_api_key(*args, **kwargs):
        # apikey = request.headers.get('ApiKey')
        # if apikey and apikey == SECRET_KEY:
        #     return api_method(*args, **kwargs)
        # else:
        #     abort(401)
        print('!!! CHECKING API KEY')
        return api_method(*args, **kwargs)

    return check_api_key


class Football(Resource):
    def get(self, team_name):
        args = footbal_args_parser.parse_args()
        football_team = args.football_team

        data = FootballParser.get_team_info(football_team)
        return data