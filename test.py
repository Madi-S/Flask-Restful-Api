import requests
from models import APIUser, logger

BASE = 'http://127.0.0.1:5000/'

# r = requests.get(BASE + 'hello')
# print(r.json())

# r = requests.post(BASE + 'hello', data={'token': '54612315', 'age': 25})
# print(r.json())

# r = requests.get(BASE + 'health/62/73')
# print(r.json())


# r = requests.put(BASE + 'test/54', {'name': 'Madi', 'age': 17, 'gender': 'male'})
# print(r.json())

# r = requests.get(BASE + 'test/54')
# print(r.json())

# r = requests.delete(BASE + 'test/54')
# print(r.json())

# r = requests.get(BASE + 'test/54')
# print(r.json())

key = APIUser.query.get(1).api_user_key

r = requests.get(BASE + f'/faker/{key}')
logger.debug('Response: %s', r)
logger.debug('JSON: %s', r.json())
logger.debug('Text: %s', r.text)